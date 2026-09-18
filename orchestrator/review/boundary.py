"""Cross-boundary verification gate (M40 Task 2).

Inspects function calls and imports that cross context boundaries (different
``domain/module`` routes) and validates them against metadata inodes:

1. **unknown-imported-symbol** — an import names a symbol the callee inode
   does not export (interface drift across a boundary).
2. **call-arity-mismatch** — an added call site passes an argument count the
   callee's recorded signature cannot accept.
3. **complexity-amplification** — an added call inside an added loop invokes a
   callee whose declared complexity is non-constant (e.g. declared \(O(N)\)
   called per element ⇒ effective \(O(N^2)\) against the contract).

All checks are deterministic against declared inode metadata — no inference,
no model. When the inode store is absent or stale the gate skips with an
explicit note (never reviews against untrustworthy metadata).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.context.extract import extract_for_path
from orchestrator.context.inodes import find_stale, load_index, module_route_for
from orchestrator.dependency_graph import resolve_import

_IMPORT_LINE_RE = re.compile(r"^\s*import\s|^\s*from\s.+\simport\s")
_LOOP_BRACE_RE = re.compile(r"^\s*(for\b|while\b).*\{|\.(forEach|map|filter|reduce)\s*\(")
_LOOP_INDENT_RE = re.compile(r"^\s*(for\b|while\b).*:\s*(#.*)?$")
_CONSTANT_COMPLEXITIES = frozenset({"O(1)", ""})


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


def _call_sites(lines: list[str], names: set[str]) -> list[dict[str, Any]]:
    """Find call sites for imported names in added lines, with loop context."""
    if not names:
        return []
    pattern = re.compile(r"\b(" + "|".join(re.escape(n) for n in sorted(names)) + r")\s*\(")
    sites: list[dict[str, Any]] = []
    brace_depth = 0
    brace_loops: list[int] = []
    indent_loops: list[int] = []
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" \t"))
        if stripped:
            indent_loops = [mark for mark in indent_loops if indent > mark]
        in_loop = any(brace_depth > mark for mark in brace_loops) or bool(indent_loops)

        for match in pattern.finditer(line):
            start = match.end()
            depth = 1
            argc = 0
            seen_token = False
            index = start
            while index < len(line) and depth > 0:
                char = line[index]
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                elif char == "," and depth == 1:
                    argc += 1
                elif not char.isspace() and depth == 1:
                    seen_token = True
                index += 1
            sites.append(
                {
                    "name": match.group(1),
                    "argc": argc + 1 if seen_token else 0,
                    "in_loop": in_loop,
                    "line": stripped,
                }
            )

        if _LOOP_BRACE_RE.match(line):
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


def emit_boundary_candidates(
    repo_root: Path,
    *,
    changed_paths: list[str],
    diff_text: str = "",
    store_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Emit boundary-violation candidates + notes. Skips safely when unusable."""
    repo_root = Path(repo_root)
    notes: list[str] = []
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
    inode_cache: dict[str, dict[str, Any]] = {}

    def _inode_for(rel_path: str) -> dict[str, Any] | None:
        if rel_path not in inode_cache:
            entry = index["files"].get(rel_path)
            if not entry:
                inode_cache[rel_path] = None  # type: ignore[assignment]
            else:
                path = base / f"{entry['content_hash']}.json"
                if not path.is_file():
                    inode_cache[rel_path] = None  # type: ignore[assignment]
                else:
                    with path.open(encoding="utf-8") as handle:
                        inode_cache[rel_path] = json.load(handle)
        return inode_cache[rel_path]

    added_by_file = _added_lines_by_file(diff_text)
    candidates: list[dict[str, Any]] = []
    indexed_paths = set(index["files"])
    checked_paths = [p for p in changed_paths if p in indexed_paths]
    if not checked_paths:
        return [], ["boundary check: no changed paths present in inode store"]

    for rel_path in checked_paths:
        inode = _inode_for(rel_path)
        if inode is None:
            continue
        added_lines = added_by_file.get(rel_path, [])
        added_imports = extract_for_path(rel_path, "\n".join(added_lines)).get("imports", [])
        imports = list(inode.get("imports") or []) + added_imports

        # Merge import names per resolved cross-boundary target so a symbol
        # imported by both old and added statements is checked exactly once.
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
            if target_inode is None:
                continue
            exports = set(target_inode.get("exports") or [])
            functions = _function_symbols(target_inode)

            for name in names:
                if name not in exports:
                    candidates.append(
                        {
                            "id": f"boundary-unknown-symbol-{rel_path}-{name}",
                            "title": f"Cross-boundary import of unknown symbol `{name}`",
                            "detail": (
                                f"`{rel_path}` imports `{name}` from `{target}`, "
                                f"but the callee inode exports only "
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

            checkable = {name: functions[name] for name in names if name in functions}
            if not added_lines or not checkable:
                continue
            for site in _call_sites(added_lines, set(checkable)):
                symbol = checkable[site["name"]]
                params = symbol.get("params") or []
                if not params:
                    continue
                required = sum(1 for param in params if not param.get("optional"))
                total = len(params)
                if not (required <= site["argc"] <= total):
                    candidates.append(
                        {
                            "id": f"boundary-arity-{rel_path}-{site['name']}",
                            "title": f"Cross-boundary call arity mismatch: `{site['name']}`",
                            "detail": (
                                f"Added call `{site['line']}` passes {site['argc']} argument(s); "
                                f"`{target}` declares `{symbol.get('signature', site['name'])}` "
                                f"({required} required / {total} total)."
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
                            "id": f"boundary-complexity-{rel_path}-{site['name']}",
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

    notes.append(f"boundary check: {len(checked_paths)} changed file(s) checked against inode store")
    return candidates, notes
