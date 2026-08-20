"""Minimal YAML loader for Compass capability sidecars (stdlib only)."""

from __future__ import annotations

from orchestrator.registry.loader import RegistryLoadError


def load_simple_yaml(text: str, path: str = "<yaml>") -> dict:
    lines = text.splitlines()
    index = 0
    result, index = _parse_mapping(lines, index, 0, path)
    if index < len(lines) and lines[index].strip():
        raise RegistryLoadError(f"unexpected trailing content in {path} at line {index + 1}")
    if not isinstance(result, dict):
        raise RegistryLoadError(f"sidecar root must be a mapping: {path}")
    return result


def _parse_mapping(lines: list[str], index: int, indent: int, path: str) -> tuple[dict, int]:
    mapping: dict = {}
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        current_indent = _leading_spaces(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise RegistryLoadError(f"invalid indent at {path} line {index + 1}")
        stripped = line.strip()
        if ":" not in stripped:
            raise RegistryLoadError(f"expected key:value at {path} line {index + 1}")
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        index += 1
        if raw_value:
            mapping[key] = _parse_scalar(raw_value)
            continue
        # nested structure
        if index >= len(lines) or _leading_spaces(lines[index]) <= indent:
            mapping[key] = None
            continue
        nested_indent = _leading_spaces(lines[index])
        if _is_list_item(lines[index]):
            value, index = _parse_list(lines, index, nested_indent, f"{path}.{key}")
        else:
            value, index = _parse_mapping(lines, index, nested_indent, f"{path}.{key}")
        mapping[key] = value
    return mapping, index


def _parse_list(lines: list[str], index: int, indent: int, path: str) -> tuple[list, int]:
    items: list = []
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        current_indent = _leading_spaces(line)
        if current_indent < indent:
            break
        if not _is_list_item(line):
            break
        item_text = line.strip()[1:].strip()
        index += 1
        if item_text:
            items.append(_parse_scalar(item_text))
            continue
        if index >= len(lines):
            items.append(None)
            break
        nested_indent = _leading_spaces(lines[index])
        if _is_list_item(lines[index]):
            raise RegistryLoadError(f"nested lists not supported at {path} line {index + 1}")
        value, index = _parse_mapping(lines, index, nested_indent, f"{path}[]")
        items.append(value)
    return items, index


def _is_list_item(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("- ") or stripped == "-"


def _leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_scalar(raw: str):
    if raw in {"true", "True"}:
        return True
    if raw in {"false", "False"}:
        return False
    if raw in {"null", "None", "~"}:
        return None
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",") if part.strip()]
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw
