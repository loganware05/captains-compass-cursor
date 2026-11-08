"""Plan-approval binding for T3 execution starts."""

from __future__ import annotations

import re
from pathlib import Path


class PlanGateError(ValueError):
    """Raised when a T3 start would bypass the plan gate."""


_STATUS_LINE = re.compile(r"^- Status:\s*\*?\*?([^*\n]+)\*?\*?\s*$", re.MULTILINE)
_PLAN_ID = re.compile(r"\|\s*Plan ID\s*\|\s*`?([^`|]+)`?\s*\|", re.IGNORECASE)


def parse_plan_document(text: str) -> tuple[str, str]:
    """Return (plan_id, status) from IMPLEMENTATION_PLAN.md text."""
    status = ""
    match = _STATUS_LINE.search(text or "")
    if match:
        status = match.group(1).strip()
    plan_id = ""
    pid = _PLAN_ID.search(text or "")
    if pid:
        plan_id = pid.group(1).strip()
    return plan_id, status


def plan_status_allows_dispatch(status: str) -> bool:
    upper = (status or "").upper()
    return any(token in upper for token in ("APPROVED", "IN PROGRESS", "VALIDATING"))


def require_plan_binding(
    repo_root: Path,
    *,
    plan_id: str,
    allow_fixture_plan: bool = False,
) -> dict[str, str]:
    """Ensure referenced plan_id is the active approved plan (unless fixture escape)."""
    if allow_fixture_plan:
        return {
            "plan_id": plan_id,
            "plan_status": "FIXTURE",
            "binding": "fixture-allow",
            "bypassed_plan_gate": "false",
        }
    path = Path(repo_root) / "IMPLEMENTATION_PLAN.md"
    if not path.is_file():
        raise PlanGateError("IMPLEMENTATION_PLAN.md missing — cannot bind T3 start")
    text = path.read_text(encoding="utf-8")
    active_id, status = parse_plan_document(text)
    if not active_id:
        raise PlanGateError("could not parse Plan ID from IMPLEMENTATION_PLAN.md")
    if active_id != plan_id:
        raise PlanGateError(
            f"plan_id {plan_id!r} does not match active plan {active_id!r}"
        )
    if not plan_status_allows_dispatch(status):
        raise PlanGateError(
            f"plan {plan_id!r} status {status!r} does not allow T3 dispatch "
            "(need APPROVED / IN PROGRESS / VALIDATING)"
        )
    return {
        "plan_id": plan_id,
        "plan_status": status,
        "binding": "implementation-plan",
        "bypassed_plan_gate": "false",
    }
