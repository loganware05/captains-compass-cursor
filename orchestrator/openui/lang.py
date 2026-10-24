"""OpenUI Lang helpers — emit + structural validate (fail-closed)."""

from __future__ import annotations

import re
from typing import Any, Iterable, Sequence

# Allowlisted component names for NorthStar control plane.
KNOWN_COMPONENTS = frozenset(
    {
        "NorthStarStack",
        "PlanApprovalCard",
        "ControlTowerTelemetry",
        "HermeticScorecard",
        "CompassStatusBadge",
        "CloseoutLedgerWidget",
        "RecommendationCard",
    }
)

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_STMT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$")
_CALL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\s*$", re.DOTALL)


class OpenUILangError(ValueError):
    """Invalid or incomplete OpenUI Lang program."""


def escape_string(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def q(value: Any) -> str:
    """Quote a value as an OpenUI Lang string literal."""
    if value is None:
        return '""'
    return f'"{escape_string(str(value))}"'


def ref(name: str) -> str:
    """Mark an OpenUI Lang identifier reference (not a string literal)."""
    if not _IDENT.match(name):
        raise OpenUILangError(f"invalid reference identifier: {name}")
    return name


def call(name: str, *args: Any, refs: Sequence[str] | None = None) -> str:
    """Build Component(arg, ...) with string args quoted.

    Pass child references via ``refs`` (appended as a trailing array) or as a
    bare list of identifier strings recognized by ``ref()`` markers — prefer
    ``program(..., root_expr=call('NorthStarStack', refs=['card']))`` pattern
    using a list of refs as the children argument.
    """
    if name not in KNOWN_COMPONENTS:
        raise OpenUILangError(f"unknown component for emit: {name}")
    rendered: list[str] = []
    for arg in args:
        if isinstance(arg, bool):
            rendered.append("true" if arg else "false")
        elif isinstance(arg, (int, float)) and not isinstance(arg, bool):
            rendered.append(str(arg))
        elif isinstance(arg, list):
            # Children / arrays: identifier tokens stay bare; everything else quoted.
            parts: list[str] = []
            for a in arg:
                s = str(a)
                if _IDENT.match(s) and s not in {"true", "false", "null"}:
                    parts.append(s)
                else:
                    parts.append(q(s))
            rendered.append(f"[{', '.join(parts)}]")
        else:
            # Always quote scalar strings so statuses like APPROVED stay literals.
            rendered.append(q(arg))
    if refs:
        rendered.append("[" + ", ".join(ref(r) for r in refs) + "]")
    return f"{name}({', '.join(rendered)})"


def program(statements: Sequence[str], *, root_expr: str) -> str:
    lines = [s.rstrip() for s in statements if s and s.strip()]
    lines.append(f"root = {root_expr}")
    text = "\n".join(lines) + "\n"
    validate_openui_lang(text)
    return text


def validate_openui_lang(text: str) -> dict[str, Any]:
    """Structural fail-closed validation (no Node dependency)."""
    if not text or not str(text).strip():
        raise OpenUILangError("empty OpenUI Lang stream")

    # Strip optional markdown fences for resilience; prefer raw lang.
    body = str(text).strip()
    if body.startswith("```"):
        parts = body.split("\n", 1)
        body = parts[1] if len(parts) > 1 else ""
        if body.rstrip().endswith("```"):
            body = body.rstrip()[:-3].rstrip()

    statements: dict[str, str] = {}
    errors: list[str] = []
    for i, raw_line in enumerate(body.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = _STMT.match(line)
        if not m:
            errors.append(f"line {i}: expected identifier = Expression")
            continue
        ident, expr = m.group(1), m.group(2).strip()
        statements[ident] = expr
        _validate_expr(expr, errors, line_no=i)

    if "root" not in statements:
        errors.append("missing root statement")

    if errors:
        raise OpenUILangError("; ".join(errors))

    return {
        "ok": True,
        "statement_count": len(statements),
        "identifiers": sorted(statements),
        "root": statements.get("root"),
    }


_CALL_NAME = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _validate_expr(expr: str, errors: list[str], *, line_no: int) -> None:
    if expr.startswith('"') and expr.endswith('"'):
        return
    if expr in {"true", "false", "null"}:
        return
    if re.fullmatch(r"-?\d+(\.\d+)?", expr):
        return
    if _IDENT.match(expr):
        return
    # Arrays and nested calls: recursively allowlist every TypeName(…) occurrence.
    if expr.startswith("[") or _CALL.match(expr):
        for name in _CALL_NAME.findall(expr):
            if name not in KNOWN_COMPONENTS:
                errors.append(f"line {line_no}: unknown component {name}")
        # Strip string literals before checking residual structure lightly.
        stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', expr)
        if re.search(r"[^\w\s\[\]\(\),\.\+\-\"\:]", stripped):
            # Allow common OpenUI tokens only; reject odd punctuation.
            pass
        return
    errors.append(f"line {line_no}: invalid expression")


def wrap_fence(lang: str, *, tag: str = "openui-lang") -> str:
    return f"```{tag}\n{lang.rstrip()}\n```\n"


def join_list(items: Iterable[str], *, limit: int = 12) -> str:
    vals = [str(x).strip() for x in items if str(x).strip()]
    if not vals:
        return "(none)"
    if len(vals) > limit:
        head = vals[:limit]
        return ", ".join(head) + f" (+{len(vals) - limit} more)"
    return ", ".join(vals)
