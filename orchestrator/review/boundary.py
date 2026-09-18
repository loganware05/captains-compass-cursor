"""Cross-boundary verification gate (M40 Task 2).

Inspects function calls and imports that cross context boundaries (different
``domain/module`` routes) and validates them against metadata inodes:

1. **unknown-imported-symbol** — an import names a symbol the callee does not
   export (interface drift across a boundary). Checked both directions:
   changed importers, and unchanged importers of a changed callee.
2. **call-arity-mismatch** — an added call site passes an argument count the
   callee's recorded signature cannot accept (variadic-aware).
3. **complexity-amplification** — an added call inside an added loop invokes a
   callee whose declared complexity is non-constant (e.g. declared \(O(N)\)
   called per element ⇒ effective \(O(N^2)\) against the contract).

All checks are deterministic against declared inode metadata — no inference,
no model. When the inode store is absent or stale the gate skips with an
explicit note (never reviews against untrustworthy metadata).

Store semantics: the store normally describes the tree under review (head).
To stay correct when the store was built from the base tree, a changed file's
*effective* exports are computed as store exports − removed-line exports +
added-line exports, which converges to the head state in both modes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.context.extract import _split_top_level, extract_for_path
from orchestrator.context.inodes import find_stale, load_index, module_route_for
from orchestrator.dependency_graph import resolve_import


def _split_args(arg_text: str) -> list[str]:
    return _split_top_level(arg_text)

_LOOP_KEYWORD_RE = re.compile(r"^\s*(?:async\s+)?(?:for\b|while\b)")
_LOOP_METHOD_RE = re.compile(r"\.(?:forEach|map|filter|reduce)\s*\(")
_LOOP_INDENT_RE = re.compile(r"^\s*(?:async\s+)?(?:for\b|while\b).*:\s*(#.*)?$")
_CONSTANT_COMPLEXITIES = frozenset({"O(1)", ""})
_LINE_COMMENT_RE = re.compile(r"//.*$")
_STRING_RE = re.compile(r"'[^'\n]*'|\"[^\"\n]*\"|`[^`\n]*`")


def _added_lines_by_file(diff_text: str) -> dict[str, list[str]]:
    added: dict[str, list[str]] = {}
    current: str | None = None
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:].strip()
            added.setdefault(current, [])
        elif line.startswith("+++"):
            current = None
        elif current is not None and line.startswith("+") and not line.startswith("+++"):
            added[current].append(line[1:])
    return added


def _removed_lines_by_file(diff_text: str) -> dict[str, list[str]]:
    removed: dict[str, list[str]] = {}
    current: str | None = None
    for line in diff_text.splitlines():
        if line.startswith("--- a/"):
            current = line[6:].strip()
            removed.setdefault(current, [])
        elif line.startswith("---"):
            current = None
        elif current is not None and line.startswith("-") and not line.startswith("---"):
            removed[current].append(line[1:])
    return removed


def _logical_lines(lines: list[str]) -> list[str]:
    """Join lines while parentheses are unbalanced (multi-line calls)."""
    logical: list[str] = []
    buffer = ""
    depth = 0
    for line in lines:
        buffer = f"{buffer} {line.strip()}" if buffer else line
        depth += line.count("(") - line.count(")")
        if depth <= 0:
            logical.append(buffer)
            buffer = ""
            depth = 0
    if buffer:
        logical.append(buffer)
    return logical


def _strip_noise(line: str) -> str:
    """Remove string literals and trailing line comments before scanning."""
    return _LINE_COMMENT_RE.sub("", _STRING_RE.sub('""', line))


def _call_sites(lines: list[str], names: set[str]) -> list[dict[str, Any]]:
    """Find call sites for imported names in added lines, with loop context.

    Method calls (`obj.name(`) are not imports of `name` and are skipped.
    """
    if not names:
        return []
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(n) for n in sorted(names)) + r")(?:<[^>]*>)?\s*\("
    )
    sites: list[dict[str, Any]] = []
    brace_depth = 0
    brace_loops: list[int] = []
    indent_loops: list[int] = []
    for raw_line in _logical_lines(lines):
        line = _strip_noise(raw_line)
        stripped = line.strip()
        indent = len(raw_line) - len(raw_line.lstrip(" \t"))
        if stripped:
            indent_loops = [mark for mark in indent_loops if indent > mark]
        is_loop_line = bool(
            _LOOP_KEYWORD_RE.match(line) or _LOOP_METHOD_RE.search(line) or _LOOP_INDENT_RE.match(line)
        )
        in_loop = (
            any(brace_depth > mark for mark in brace_loops)
            or bool(indent_loops)
            or is_loop_line
        )

        for match in pattern.finditer(line):
            if match.start() > 0 and line[match.start() - 1] == ".":
                continue  # method call, not an import reference
            start = match.end()
            depth = 1
            index = start
            arg_text_end = -1
            while index < len(line) and depth > 0:
                char = line[index]
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        arg_text_end = index
                        break
                index += 1
            if arg_text_end < 0:
                arg_text = line[start:]  # unclosed — count what we can see
            else:
                arg_text = line[start:arg_text_end]
            segments = [
                seg
                for seg in _split_args(arg_text)
                if seg.strip()
            ]
            sites.append(
                {
                    "name": match.group(1),
                    "argc": len(segments),
                    "in_loop": in_loop,
                    "line": stripped[:160],
                }
            )

        if is_loop_line and ("{" in line or _LOOP_METHOD_RE.search(line)):
            brace_loops.append(brace_depth)
        if _LOOP_INDENT_RE.match(line):
            indent_loops.append(indent)
        brace_depth += line.count("{") - line.count("}")
        brace_loops = [mark for mark in brace_loops if brace_depth > mark]
    return sites


def _function_symbols(inode: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        symbol["name"]: symbol
        for symbol in inode.get("symbols") or []
        if symbol.get("kind") in {"function", "const"} and symbol.get("exported")
    }


def _exports_of(inode: dict[str, Any]) -> set[str]:
    return set(inode.get("exports") or [])


def _effective_exports(
    rel_path: str,
    inode: dict[str, Any] | None,
    added_by_file: dict[str, list[str]],
    removed_by_file: dict[str, list[str]],
) -> set[str]:
    """Store exports adjusted by the diff — converges to head state whether the
    store was built from base or head."""
    exports = set(_exports_of(inode)) if inode else set()
    removed = removed_by_file.get(rel_path)
    if removed:
        removed_exports = extract_for_path(rel_path, "\n".join(removed))
        exports -= {s["name"] for s in removed_exports.get("symbols", []) if s.get("exported")}
    added = added_by_file.get(rel_path)
    if added:
        added_exports = extract_for_path(rel_path, "\n".join(added))
        exports |= {s["name"] for s in added_exports.get("symbols", []) if s.get("exported")}
    return exports


def emit_boundary_candidates(
    repo_root: Path,
    *,
    changed_paths: list[str],
    diff_text: str = "",
    store_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Emit boundary-violation candidates + notes. Skips safely when unusable."""
    repo_root = Path(repo_root)
    try:
        index = load_index(repo_root, store_dir=store_dir)
    except Exception:
        return [], ["boundary check skipped: inode store absent (run scripts/build-context-inodes.sh)"]

    stale = find_stale(repo_root, store_dir=store_dir)
    if stale:
        return [], [
            f"boundary check skipped: inode store stale for {len(stale)} path(s) "
            f"(e.g. {stale[0]['path']} {stale[0]['reason']}) — rerun scripts/build-context-inodes.sh"
        ]

    base = Path(store_dir) if store_dir else repo_root / ".agent" / "inodes"
    inode_cache: dict[str, dict[str, Any] | None] = {}

    def _inode_for(rel_path: str) -> dict[str, Any] | None:
        if rel_path not in inode_cache:
            entry = index["files"].get(rel_path)
            if not entry:
                inode_cache[rel_path] = None
            else:
                path = base / f"{entry['content_hash']}.json"
                if not path.is_file():
                    inode_cache[rel_path] = None
                else:
                    with path.open(encoding="utf-8") as handle:
                        inode_cache[rel_path] = json.load(handle)
        return inode_cache[rel_path]

    added_by_file = _added_lines_by_file(diff_text)
    removed_by_file = _removed_lines_by_file(diff_text)
    indexed_paths = set(index["files"])
    candidates: list[dict[str, Any]] = []
    seen_ids: dict[str, int] = {}

    def _next_id(kind: str, rel_path: str, name: str) -> str:
        key = f"boundary-{kind}-{rel_path}-{name}"
        occurrence = seen_ids.get(key, 0)
        seen_ids[key] = occurrence + 1
        return key if occurrence == 0 else f"{key}-{occurrence + 1}"

    def _check_imports(
        rel_path: str,
        imports: list[dict[str, Any]],
        added_lines: list[str],
        *,
        importer_changed: bool,
    ) -> None:
        names_by_target: dict[str, set[str]] = {}
        for imp in imports:
            module = imp.get("module") or ""
            names = {n for n in (imp.get("names") or []) if n}
            if not names:
                continue
            target = resolve_import(rel_path, module, indexed_paths)
            if target is None or target == rel_path:
                continue
            if module_route_for(target) == module_route_for(rel_path):
                continue  # intra-module: not a boundary crossing
            names_by_target.setdefault(target, set()).update(names)

        for target in sorted(names_by_target):
            names = sorted(names_by_target[target])
            target_inode = _inode_for(target)
            target_changed = target in changed_set
            if target_inode is None and not target_changed:
                continue
            exports = _effective_exports(target, target_inode, added_by_file, removed_by_file)
            functions = _function_symbols(target_inode) if target_inode else {}
            if target_changed:
                for symbol in extract_for_path(target, "\n".join(added_by_file.get(target, []))).get(
                    "symbols", []
                ):
                    if symbol.get("exported") and symbol.get("kind") in {"function", "const"}:
                        functions.setdefault(symbol["name"], symbol)

            for name in names:
                if name not in exports:
                    candidates.append(
                        {
                            "id": _next_id("unknown-symbol", rel_path, name),
                            "title": f"Cross-boundary import of unknown symbol `{name}`",
                            "detail": (
                                f"`{rel_path}` imports `{name}` from `{target}`, "
                                f"but the callee exports only "
                                f"{sorted(exports) or 'nothing'}. Interface drift across the "
                                f"`{module_route_for(rel_path)}` → `{module_route_for(target)}` boundary."
                            ),
                            "severity": "high",
                            "confidence": 0.9,
                            "skill": "code-reviewer",
                            "category": "boundary",
                            "evidence_paths": [rel_path, target],
                            "suggested_fix": f"Import an exported symbol from `{target}` or add `{name}` to its exports.",
                        }
                    )

            if not importer_changed:
                continue  # arity/complexity need the importer's added lines
            checkable = {name: functions[name] for name in names if name in functions}
            if not added_lines or not checkable:
                continue
            for site in _call_sites(added_lines, set(checkable)):
                symbol = checkable[site["name"]]
                params = symbol.get("params") or []
                if not params:
                    continue
                variadic = any(param.get("variadic") for param in params)
                required = sum(
                    1 for param in params if not param.get("optional") and not param.get("variadic")
                )
                total = len(params)
                arity_bad = site["argc"] < required or (not variadic and site["argc"] > total)
                if arity_bad:
                    candidates.append(
                        {
                            "id": _next_id("arity", rel_path, site["name"]),
                            "title": f"Cross-boundary call arity mismatch: `{site['name']}`",
                            "detail": (
                                f"Added call `{site['line']}` passes {site['argc']} argument(s); "
                                f"`{target}` declares `{symbol.get('signature', site['name'])}` "
                                f"({required} required / {total} total"
                                f"{', variadic' if variadic else ''})."
                            ),
                            "severity": "medium",
                            "confidence": 0.85,
                            "skill": "code-reviewer",
                            "category": "boundary",
                            "evidence_paths": [rel_path, target],
                            "suggested_fix": f"Align the call with the declared signature in `{target}`.",
                        }
                    )
                declared = symbol.get("complexity") or ""
                if site["in_loop"] and declared and declared not in _CONSTANT_COMPLEXITIES:
                    candidates.append(
                        {
                            "id": _next_id("complexity", rel_path, site["name"]),
                            "title": f"Complexity amplification across boundary: `{site['name']}` declared {declared}",
                            "detail": (
                                f"Added call `{site['line']}` invokes `{site['name']}` "
                                f"(declared {declared} in `{target}`) inside a loop, giving "
                                f"effective O(N×{declared[2:-1]}) — e.g. O(N) callee ⇒ O(N^2) total."
                            ),
                            "severity": "medium",
                            "confidence": 0.8,
                            "skill": "code-reviewer",
                            "category": "boundary",
                            "evidence_paths": [rel_path, target],
                            "suggested_fix": "Hoist the call out of the loop, batch the input, or renegotiate the callee's declared complexity.",
                        }
                    )

    changed_set = set(changed_paths)
    checked = 0

    # Direction 1: changed source files as importers. New files (absent from
    # the store) are still checked via their added import lines. Non-source
    # files (docs, hooks, assets) are not indexable and are skipped.
    from orchestrator.context.inodes import INDEXED_SUFFIXES

    for rel_path in sorted(changed_set):
        inode = _inode_for(rel_path)
        added_lines = added_by_file.get(rel_path, [])
        if inode is None and Path(rel_path).suffix.lower() not in INDEXED_SUFFIXES:
            continue
        if inode is None and not added_lines:
            continue
        imports = list(inode.get("imports") or []) if inode else []
        if added_lines:
            imports += extract_for_path(rel_path, "\n".join(added_lines)).get("imports", [])
        _check_imports(rel_path, imports, added_lines, importer_changed=True)
        checked += 1

    # Direction 2: changed files as callees — re-check unchanged importers
    # against the callee's effective (post-change) exports.
    importers_by_target: dict[str, list[str]] = {}
    for rel_path in sorted(indexed_paths):
        inode = _inode_for(rel_path)
        if inode is None:
            continue
        for imp in inode.get("imports") or []:
            target = resolve_import(rel_path, imp.get("module") or "", indexed_paths)
            if target:
                importers_by_target.setdefault(target, []).append(rel_path)
    for target in sorted(changed_set):
        for importer in sorted(set(importers_by_target.get(target, []))):
            if importer in changed_set:
                continue  # already checked in direction 1
            inode = _inode_for(importer)
            if inode is None:
                continue
            _check_imports(importer, list(inode.get("imports") or []), [], importer_changed=False)
            checked += 1

    notes = [f"boundary check: {checked} file(s) checked against inode store"]
    if checked == 0:
        notes = ["boundary check: no changed paths present in inode store"]
    return candidates, notes
