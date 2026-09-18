"""Hermetic structural metadata extractors for the inode store (M40).

Python source is parsed with the stdlib ``ast`` module. TypeScript/TSX source
uses a conservative line-oriented parser-lite: it recognizes top-level
``interface`` / ``type`` / ``function`` / arrow-``const`` declarations and
``import`` statements. The parser-lite deliberately extracts less than a full
compiler — unknown constructs are skipped, never guessed. Declared complexity
comes only from an explicit ``@complexity O(...)`` annotation (docstring for
Python, JSDoc/line comment for TypeScript); it is never inferred.
"""

from __future__ import annotations

import ast
import re
from typing import Any

_COMPLEXITY_RE = re.compile(r"@complexity\s+(O\([^)\s]*\))")

_TS_IMPORT_RE = re.compile(
    r"^\s*import\s+(?:type\s+)?"
    r"(?:(?P<default>[A-Za-z_$][\w$]*)\s*,?\s*)?"
    r"(?:\{(?P<names>[^}]*)\})?\s*"
    r"(?:\*\s*as\s+(?P<ns>[A-Za-z_$][\w$]*))?\s*"
    r"from\s*['\"](?P<module>[^'\"]+)['\"]"
)
_TS_IMPORT_SIDE_EFFECT_RE = re.compile(r"^\s*import\s*['\"](?P<module>[^'\"]+)['\"]")
_TS_INTERFACE_RE = re.compile(
    r"^(?P<export>\s*export\s+)?(?:default\s+)?interface\s+(?P<name>[A-Za-z_$][\w$]*)"
)
_TS_TYPE_RE = re.compile(
    r"^(?P<export>\s*export\s+)?type\s+(?P<name>[A-Za-z_$][\w$]*)\s*=(?P<rhs>.*)$"
)
_TS_FUNCTION_RE = re.compile(
    r"^(?P<export>\s*export\s+)?(?:async\s+)?function\s+(?P<name>[A-Za-z_$][\w$]*)"
    r"\s*\((?P<params>[^)]*)\)\s*(?::\s*(?P<ret>[^{;]+?))?\s*\{?\s*$"
)
_TS_ARROW_RE = re.compile(
    r"^(?P<export>\s*export\s+)?const\s+(?P<name>[A-Za-z_$][\w$]*)"
    r"\s*(?::\s*[^=]+?)?=\s*(?:async\s*)?\((?P<params>[^)]*)\)"
    r"\s*(?::\s*(?P<ret>[^=]+?))?\s*=>"
)
_TS_CONST_RE = re.compile(
    r"^(?P<export>\s*export\s+)?const\s+(?P<name>[A-Za-z_$][\w$]*)"
    r"\s*(?::\s*(?P<ret>[^=;]+?))?\s*=\s*(?P<value>[^=;][^;]*?)\s*;?\s*$"
)
_TS_FIELD_RE = re.compile(r"^\s*(?:readonly\s+)?(?P<name>[A-Za-z_$][\w$]*)(?P<opt>\?)?\s*:\s*(?P<type>[^;,]+)")


def _declared_complexity(*texts: str) -> str:
    for text in texts:
        if not text:
            continue
        match = _COMPLEXITY_RE.search(text)
        if match:
            return match.group(1)
    return ""


def _parse_params(raw: str) -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        chunk = chunk.lstrip("...").strip()
        optional = "=" in chunk
        if "=" in chunk:
            chunk = chunk.split("=", 1)[0].strip()
        if ":" in chunk:
            name, ptype = chunk.split(":", 1)
            name = name.strip()
            optional = optional or name.endswith("?")
            params.append({"name": name.rstrip("?"), "type": ptype.strip(), "optional": optional})
        else:
            name = chunk.strip()
            optional = optional or name.endswith("?")
            params.append({"name": name.rstrip("?"), "type": "", "optional": optional})
    return params


def _params_signature(params: list[dict[str, str]]) -> str:
    parts = []
    for param in params:
        if param.get("type"):
            parts.append(f"{param['name']}: {param['type']}")
        else:
            parts.append(param["name"])
    return ", ".join(parts)


def extract_python(source: str) -> dict[str, Any]:
    """Extract symbols/imports from Python source via stdlib ast.

    Unparseable source yields empty metadata rather than raising — an inode
    with no symbols is more useful to review tooling than a crashed build.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"language": "python", "symbols": [], "imports": [], "declared_complexity": ""}
    symbols: list[dict[str, Any]] = []
    imports: list[dict[str, Any]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params: list[dict[str, Any]] = []
            positional = list(node.args.posonlyargs) + list(node.args.args)
            defaults = [None] * (len(positional) - len(node.args.defaults)) + list(node.args.defaults)
            for arg, default in zip(positional, defaults):
                params.append(
                    {
                        "name": arg.arg,
                        "type": ast.unparse(arg.annotation) if arg.annotation else "",
                        "optional": default is not None,
                    }
                )
            for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                params.append(
                    {
                        "name": arg.arg,
                        "type": ast.unparse(arg.annotation) if arg.annotation else "",
                        "optional": default is not None,
                    }
                )
            if node.args.vararg:
                params.append({"name": node.args.vararg.arg, "type": "", "optional": True})
            if node.args.kwarg:
                params.append({"name": node.args.kwarg.arg, "type": "", "optional": True})
            return_type = ast.unparse(node.returns) if node.returns else ""
            docstring = ast.get_docstring(node) or ""
            signature = f"def {node.name}({_params_signature(params)})"
            if return_type:
                signature += f" -> {return_type}"
            symbols.append(
                {
                    "name": node.name,
                    "kind": "function",
                    "exported": not node.name.startswith("_"),
                    "signature": signature,
                    "params": params,
                    "return_type": return_type,
                    "complexity": _declared_complexity(docstring),
                }
            )
        elif isinstance(node, ast.ClassDef):
            methods = [
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            symbols.append(
                {
                    "name": node.name,
                    "kind": "class",
                    "exported": not node.name.startswith("_"),
                    "signature": f"class {node.name}",
                    "complexity": _declared_complexity(ast.get_docstring(node) or ""),
                    "fields": [{"name": method, "type": "method"} for method in methods],
                }
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"module": alias.name, "names": [alias.asname or alias.name]})
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            imports.append(
                {"module": module, "names": [alias.name for alias in node.names]}
            )
    module_doc = ast.get_docstring(tree) or ""
    return {
        "language": "python",
        "symbols": symbols,
        "imports": imports,
        "declared_complexity": _declared_complexity(module_doc),
    }


def _brace_body(lines: list[str], start: int) -> tuple[list[str], int]:
    """Return lines of a brace-delimited body starting at line index start."""
    body: list[str] = []
    depth = 0
    opened = False
    for index in range(start, len(lines)):
        line = lines[index]
        depth += line.count("{")
        if "{" in line:
            opened = True
        depth -= line.count("}")
        if opened and index > start:
            body.append(line)
        if opened and depth <= 0:
            return body, index
    return body, len(lines) - 1


def extract_typescript(source: str, *, language: str = "typescript") -> dict[str, Any]:
    """Parser-lite extraction for TypeScript/TSX (conservative, line-oriented)."""
    lines = source.splitlines()
    symbols: list[dict[str, Any]] = []
    imports: list[dict[str, Any]] = []
    pending_comment = ""
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
            pending_comment = f"{pending_comment}\n{stripped}"
            index += 1
            continue

        import_match = _TS_IMPORT_RE.match(line) or _TS_IMPORT_SIDE_EFFECT_RE.match(line)
        if import_match:
            names_raw = import_match.groupdict().get("names") or ""
            names = [
                part.strip().split(" as ")[-1].strip()
                for part in names_raw.split(",")
                if part.strip()
            ]
            default = import_match.groupdict().get("default")
            if default:
                names.append(default)
            imports.append({"module": import_match.group("module"), "names": names})
            index += 1
            continue

        interface_match = _TS_INTERFACE_RE.match(line)
        if interface_match and "{" in line:
            body, end = _brace_body(lines, index)
            fields = []
            for body_line in body:
                field_match = _TS_FIELD_RE.match(body_line)
                if field_match:
                    fields.append(
                        {
                            "name": field_match.group("name"),
                            "type": field_match.group("type").strip(),
                            "optional": bool(field_match.group("opt")),
                        }
                    )
            name = interface_match.group("name")
            field_sig = ", ".join(
                f"{f['name']}{'?' if f.get('optional') else ''}: {f['type']}" for f in fields
            )
            symbols.append(
                {
                    "name": name,
                    "kind": "interface",
                    "exported": bool(interface_match.group("export")),
                    "signature": f"interface {name} {{ {field_sig} }}",
                    "fields": fields,
                    "complexity": _declared_complexity(pending_comment),
                }
            )
            pending_comment = ""
            index = end + 1
            continue

        type_match = _TS_TYPE_RE.match(line)
        if type_match:
            symbols.append(
                {
                    "name": type_match.group("name"),
                    "kind": "type",
                    "exported": bool(type_match.group("export")),
                    "signature": f"type {type_match.group('name')} = {type_match.group('rhs').strip()}",
                    "complexity": _declared_complexity(pending_comment),
                }
            )
            pending_comment = ""
            index += 1
            continue

        function_match = _TS_FUNCTION_RE.match(line) or _TS_ARROW_RE.match(line)
        if function_match:
            params = _parse_params(function_match.group("params") or "")
            return_type = (function_match.group("ret") or "").strip()
            kind = "function" if function_match.re is _TS_FUNCTION_RE else "const"
            signature = f"{function_match.group('name')}({_params_signature(params)})"
            if return_type:
                signature += f": {return_type}"
            symbols.append(
                {
                    "name": function_match.group("name"),
                    "kind": kind,
                    "exported": bool(function_match.group("export")),
                    "signature": signature,
                    "params": params,
                    "return_type": return_type,
                    "complexity": _declared_complexity(pending_comment),
                }
            )
            pending_comment = ""
            index += 1
            continue

        const_match = _TS_CONST_RE.match(line)
        if const_match and "=>" not in line:
            return_type = (const_match.group("ret") or "").strip()
            symbols.append(
                {
                    "name": const_match.group("name"),
                    "kind": "const",
                    "exported": bool(const_match.group("export")),
                    "signature": f"const {const_match.group('name')}"
                    + (f": {return_type}" if return_type else ""),
                    "return_type": return_type,
                    "complexity": _declared_complexity(pending_comment),
                }
            )
            pending_comment = ""
            index += 1
            continue

        if stripped:
            pending_comment = ""
        index += 1

    header = "\n".join(lines[:5])
    return {
        "language": language,
        "symbols": symbols,
        "imports": imports,
        "declared_complexity": _declared_complexity(header),
    }


def language_for_path(path: str) -> str:
    lowered = path.lower()
    if lowered.endswith(".py"):
        return "python"
    if lowered.endswith(".tsx"):
        return "tsx"
    if lowered.endswith((".ts", ".mts", ".cts")):
        return "typescript"
    return "other"


def extract_for_path(path: str, source: str) -> dict[str, Any]:
    """Dispatch extraction by file extension; unsupported types yield empty metadata."""
    language = language_for_path(path)
    if language == "python":
        return extract_python(source)
    if language in {"typescript", "tsx"}:
        return extract_typescript(source, language=language)
    return {"language": "other", "symbols": [], "imports": [], "declared_complexity": ""}
