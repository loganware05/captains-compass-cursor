"""Hermetic structural metadata extractors for the inode store (M40).

Python source is parsed with the stdlib ``ast`` module. TypeScript/TSX source
uses a conservative line-oriented parser-lite: it recognizes top-level
``interface`` / ``type`` / ``function`` (incl. generics and ``export
default``) / arrow-``const`` / ``class`` declarations, ``import`` statements
(incl. multi-line), and named re-exports. The parser-lite deliberately
extracts less than a full compiler — unknown constructs are skipped, never
guessed. Declared complexity comes only from an explicit ``@complexity
O(...)`` annotation (docstring for Python, JSDoc/line comment for
TypeScript); it is never inferred. Literal values are elided from signatures
— inodes carry metadata, never file contents.
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
_TS_IMPORT_START_RE = re.compile(r"^\s*import\s+(?:type\s+)?\{(?P<names>[^}]*)$")
_TS_IMPORT_END_RE = re.compile(r"^(?P<names>[^}]*)\}\s*from\s*['\"](?P<module>[^'\"]+)['\"]")
_TS_IMPORT_SIDE_EFFECT_RE = re.compile(r"^\s*import\s*['\"](?P<module>[^'\"]+)['\"]")
_TS_REEXPORT_RE = re.compile(
    r"^\s*export\s*\{(?P<names>[^}]*)\}\s*from\s*['\"](?P<module>[^'\"]+)['\"]"
)
_TS_REEXPORT_STAR_RE = re.compile(r"^\s*export\s*\*\s*from\s*['\"](?P<module>[^'\"]+)['\"]")
_TS_INTERFACE_RE = re.compile(
    r"^(?P<export>\s*export\s+)?(?:default\s+)?interface\s+(?P<name>[A-Za-z_$][\w$]*)"
)
_TS_TYPE_RE = re.compile(
    r"^(?P<export>\s*export\s+)?type\s+(?P<name>[A-Za-z_$][\w$]*)\s*=(?P<rhs>.*)$"
)
_TS_FUNCTION_RE = re.compile(
    r"^(?P<export>\s*export\s+)?(?:default\s+)?(?:async\s+)?function\s+"
    r"(?P<name>[A-Za-z_$][\w$]*)(?:<[^>]*>)?\s*\("
)
_TS_ARROW_RE = re.compile(
    r"^(?P<export>\s*export\s+)?const\s+(?P<name>[A-Za-z_$][\w$]*)"
    r"(?:<[^>]*>)?\s*(?::\s*[^=]+?)?=\s*(?:async\s*)?\("
)
_TS_CLASS_RE = re.compile(
    r"^(?P<export>\s*export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(?P<name>[A-Za-z_$][\w$]*)"
)
_TS_METHOD_RE = re.compile(
    r"^\s+(?:public\s+|private\s+|protected\s+|static\s+|async\s+|readonly\s+)*"
    r"(?P<name>[A-Za-z_$][\w$]*)\s*\([^)]*\)\s*(?::\s*[^{;]+?)?\s*\{"
)
_TS_CONST_RE = re.compile(
    r"^(?P<export>\s*export\s+)?const\s+(?P<name>[A-Za-z_$][\w$]*)"
    r"\s*(?::\s*(?P<ret>[^=;]+?))?\s*=\s*(?P<value>[^=;][^;]*?)\s*;?\s*$"
)
_TS_FIELD_RE = re.compile(r"^\s*(?:readonly\s+)?(?P<name>[A-Za-z_$][\w$]*)(?P<opt>\?)?\s*:\s*(?P<type>[^;,]+)")

_LITERAL_RE = re.compile(r"'[^']*'|\"[^\"]*\"|`[^`]*`|\b\d+(?:\.\d+)?\b")


def _elide_literals(text: str, *, max_len: int = 120) -> str:
    """Replace literal values with placeholders — inodes carry metadata, not content."""
    elided = _LITERAL_RE.sub("…", text).strip()
    if len(elided) > max_len:
        elided = elided[: max_len - 1] + "…"
    return elided


def _declared_complexity(*texts: str) -> str:
    for text in texts:
        if not text:
            continue
        match = _COMPLEXITY_RE.search(text)
        if match:
            return match.group(1)
    return ""


def _split_top_level(raw: str) -> list[str]:
    """Split on commas at bracket depth 0, outside string literals."""
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    quote = ""
    index = 0
    while index < len(raw):
        char = raw[index]
        if quote:
            current.append(char)
            if char == quote and (index == 0 or raw[index - 1] != "\\"):
                quote = ""
        elif char in "'\"`":
            quote = char
            current.append(char)
        else:
            if char in "<([{":
                depth += 1
            elif char in ">)]}":
                depth = max(depth - 1, 0)
            if char == "," and depth == 0:
                parts.append("".join(current))
                current = []
            else:
                current.append(char)
        index += 1
    parts.append("".join(current))
    return parts


def _scan_balanced(text: str, start: int) -> str:
    """Return the contents between text[start-1] (an open paren) and its match."""
    depth = 1
    index = start
    while index < len(text) and depth > 0:
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start:index]
        index += 1
    return text[start:]


def _parse_params(raw: str) -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = []
    for chunk in _split_top_level(raw):
        chunk = chunk.strip()
        if not chunk:
            continue
        variadic = chunk.startswith("...")
        if variadic:
            chunk = chunk[3:].strip()
        optional = variadic
        if "=" in chunk:
            chunk = chunk.split("=", 1)[0].strip()
            optional = True
        if ":" in chunk:
            name, ptype = chunk.split(":", 1)
            name = name.strip()
            optional = optional or name.endswith("?")
            params.append(
                {
                    "name": name.rstrip("?"),
                    "type": ptype.strip(),
                    "optional": optional,
                    "variadic": variadic,
                }
            )
        else:
            name = chunk.strip()
            optional = optional or name.endswith("?")
            params.append(
                {"name": name.rstrip("?"), "type": "", "optional": optional, "variadic": variadic}
            )
    return params


def _params_signature(params: list[dict[str, Any]]) -> str:
    parts = []
    for param in params:
        name = f"...{param['name']}" if param.get("variadic") else param["name"]
        if param.get("type"):
            parts.append(f"{name}: {_elide_literals(param['type'])}")
        else:
            parts.append(name)
    return ", ".join(parts)


def extract_python(source: str) -> dict[str, Any]:
    """Extract symbols/imports from Python source via stdlib ast.

    Unparseable source yields empty metadata rather than raising — an inode
    with no symbols is more useful to review tooling than a crashed build.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
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
                        "variadic": False,
                    }
                )
            for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                params.append(
                    {
                        "name": arg.arg,
                        "type": ast.unparse(arg.annotation) if arg.annotation else "",
                        "optional": default is not None,
                        "variadic": False,
                    }
                )
            if node.args.vararg:
                params.append(
                    {
                        "name": node.args.vararg.arg,
                        "type": ast.unparse(node.args.vararg.annotation) if node.args.vararg.annotation else "",
                        "optional": True,
                        "variadic": True,
                    }
                )
            if node.args.kwarg:
                params.append(
                    {
                        "name": node.args.kwarg.arg,
                        "type": ast.unparse(node.args.kwarg.annotation) if node.args.kwarg.annotation else "",
                        "optional": True,
                        "variadic": True,
                    }
                )
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


def _ts_function_symbol(
    name: str,
    params_raw: str,
    remainder: str,
    *,
    exported: bool,
    kind: str,
    pending_comment: str,
) -> dict[str, Any]:
    params = _parse_params(params_raw)
    return_type = ""
    ret_match = re.match(r"\s*:\s*(?P<ret>[^={;]+?)\s*(?:\{|=>|;|$)", remainder)
    if ret_match:
        return_type = _elide_literals(ret_match.group("ret"))
    signature = f"{name}({_params_signature(params)})"
    if return_type:
        signature += f": {return_type}"
    return {
        "name": name,
        "kind": kind,
        "exported": exported,
        "signature": signature,
        "params": params,
        "return_type": return_type,
        "complexity": _declared_complexity(pending_comment),
    }


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

        # Multi-line import: `import {\n  a,\n  b\n} from './x'`
        import_start = _TS_IMPORT_START_RE.match(line)
        if import_start and "from" not in line:
            names_raw = import_start.group("names")
            end = index
            module = ""
            while end + 1 < len(lines):
                end += 1
                end_match = _TS_IMPORT_END_RE.match(lines[end])
                if end_match:
                    names_raw = f"{names_raw},{end_match.group('names')}"
                    module = end_match.group("module")
                    break
                if "}" in lines[end]:
                    break
                names_raw = f"{names_raw},{lines[end].strip()}"
            if module:
                names = [
                    part.strip().split(" as ")[-1].strip()
                    for part in names_raw.split(",")
                    if part.strip()
                ]
                imports.append({"module": module, "names": names})
            index = end + 1
            continue

        reexport = _TS_REEXPORT_RE.match(line)
        if reexport:
            names = [
                part.strip().split(" as ")[-1].strip()
                for part in (reexport.group("names") or "").split(",")
                if part.strip()
            ]
            imports.append({"module": reexport.group("module"), "names": names})
            for name in names:
                symbols.append(
                    {
                        "name": name,
                        "kind": "reexport",
                        "exported": True,
                        "signature": f"export {{ {name} }} from '{reexport.group('module')}'",
                    }
                )
            index += 1
            continue

        star = _TS_REEXPORT_STAR_RE.match(line)
        if star:
            # Star re-exports cannot be expanded statically; record the edge only.
            imports.append({"module": star.group("module"), "names": []})
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
                            "type": _elide_literals(field_match.group("type").strip()),
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
            rhs = _elide_literals(type_match.group("rhs").strip())
            symbols.append(
                {
                    "name": type_match.group("name"),
                    "kind": "type",
                    "exported": bool(type_match.group("export")),
                    "signature": f"type {type_match.group('name')} = {rhs}",
                    "complexity": _declared_complexity(pending_comment),
                }
            )
            pending_comment = ""
            index += 1
            continue

        class_match = _TS_CLASS_RE.match(line)
        if class_match:
            body, end = _brace_body(lines, index)
            methods = []
            for body_line in body:
                method_match = _TS_METHOD_RE.match(body_line)
                if method_match and method_match.group("name") not in {
                    "if", "for", "while", "switch", "catch", "return", "constructor"
                }:
                    methods.append({"name": method_match.group("name"), "type": "method"})
            name = class_match.group("name")
            symbols.append(
                {
                    "name": name,
                    "kind": "class",
                    "exported": bool(class_match.group("export")),
                    "signature": f"class {name}",
                    "fields": methods,
                    "complexity": _declared_complexity(pending_comment),
                }
            )
            pending_comment = ""
            index = end + 1
            continue

        function_match = _TS_FUNCTION_RE.match(line)
        if function_match:
            params_raw = _scan_balanced(line, function_match.end())
            remainder = line[function_match.end() + len(params_raw) + 1 :]
            symbols.append(
                _ts_function_symbol(
                    function_match.group("name"),
                    params_raw,
                    remainder,
                    exported=bool(function_match.group("export")),
                    kind="function",
                    pending_comment=pending_comment,
                )
            )
            pending_comment = ""
            index += 1
            continue

        arrow_match = _TS_ARROW_RE.match(line)
        if arrow_match:
            params_raw = _scan_balanced(line, arrow_match.end())
            remainder = line[arrow_match.end() + len(params_raw) + 1 :]
            symbols.append(
                _ts_function_symbol(
                    arrow_match.group("name"),
                    params_raw,
                    remainder,
                    exported=bool(arrow_match.group("export")),
                    kind="const",
                    pending_comment=pending_comment,
                )
            )
            pending_comment = ""
            index += 1
            continue

        const_match = _TS_CONST_RE.match(line)
        if const_match and "=>" not in line:
            return_type = _elide_literals((const_match.group("ret") or "").strip())
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
