"""Gated plan approve/reject writers for Open UI actions.

UI buttons emit intent only. Promoting IMPLEMENTATION_PLAN.md to APPROVED
requires COMPASS_CAPTAIN_APPROVE=1 (same as plan-approval-check.sh).
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from typing import Any


class ApprovalError(PermissionError):
    """Captain attestation missing or plan write refused."""


def captain_approve_enabled() -> bool:
    raw = (os.environ.get("COMPASS_CAPTAIN_APPROVE") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def apply_plan_decision(
    repo_root: Path,
    *,
    decision: str,
    feedback: str = "",
    approved_by: str = "Captain",
) -> dict[str, Any]:
    """Apply approve or reject to IMPLEMENTATION_PLAN.md.

    - approve: requires COMPASS_CAPTAIN_APPROVE=1; sets Status APPROVED + approval record
    - reject: always allowed when Open UI gate is on; sets Status REJECTED / AWAITING APPROVAL
      with feedback note (does not unlock product edits)
    """
    decision_n = decision.strip().lower()
    plan_path = Path(repo_root) / "IMPLEMENTATION_PLAN.md"
    if not plan_path.is_file():
        raise ApprovalError(f"missing {plan_path}")

    text = plan_path.read_text(encoding="utf-8")

    if decision_n in {"approve", "approved"}:
        if not captain_approve_enabled():
            raise ApprovalError(
                "UI APPROVE denied — set COMPASS_CAPTAIN_APPROVE=1 "
                "(Captain attestation required; Open UI never auto-approves)"
            )
        text = _set_status(text, "APPROVED")
        text = _set_approval_record(
            text,
            approved_by=approved_by,
            approval_date=date.today().isoformat(),
            notes="Approved via Open UI PlanApprovalCard (Captain attestation).",
        )
        plan_path.write_text(text, encoding="utf-8")
        return {
            "ok": True,
            "decision": "approve",
            "plan_path": str(plan_path),
            "status": "APPROVED",
            "committed_required": True,
            "message": (
                "Plan marked APPROVED in working tree. Commit IMPLEMENTATION_PLAN.md "
                "before product-source edits (plan-approval-check requires committed status)."
            ),
        }

    if decision_n in {"reject", "rejected", "reject_with_feedback"}:
        note = (feedback or "Rejected via Open UI.").strip()
        text = _set_status(text, "AWAITING APPROVAL")
        text = _append_feedback(text, note)
        plan_path.write_text(text, encoding="utf-8")
        session = Path(repo_root) / ".agent" / "sessions"
        session.mkdir(parents=True, exist_ok=True)
        feedback_path = session / "openui-plan-reject.md"
        feedback_path.write_text(
            f"# Open UI plan rejection\n\nDate: {date.today().isoformat()}\n\n{note}\n",
            encoding="utf-8",
        )
        return {
            "ok": True,
            "decision": "reject",
            "plan_path": str(plan_path),
            "status": "AWAITING APPROVAL",
            "feedback_path": str(feedback_path),
            "message": "Plan returned to AWAITING APPROVAL; product edits remain locked.",
        }

    raise ApprovalError(f"unknown decision: {decision}")


def _set_status(text: str, status: str) -> str:
    text = re.sub(
        r"(?im)^(-\s*Status:\s*)\*\*?[^*\n]+\*\*?",
        rf"\1**{status}**",
        text,
        count=1,
    )
    text = re.sub(
        r"(?im)^(\|\s*Status\s*\|\s*)([^|]+)(\|)",
        rf"\1**{status}** \3",
        text,
        count=1,
    )
    return text


def _set_approval_record(
    text: str,
    *,
    approved_by: str,
    approval_date: str,
    notes: str,
) -> str:
    def repl_by(m: re.Match[str]) -> str:
        return f"| {m.group(1)} | {approved_by} |"

    def repl_date(m: re.Match[str]) -> str:
        return f"| {m.group(1)} | {approval_date} |"

    def repl_notes(m: re.Match[str]) -> str:
        return f"| {m.group(1)} | {notes} |"

    text = re.sub(
        r"(?im)^\|\s*(Approved by)\s*\|\s*([^|]*)\|",
        repl_by,
        text,
        count=1,
    )
    text = re.sub(
        r"(?im)^\|\s*(Approval date)\s*\|\s*([^|]*)\|",
        repl_date,
        text,
        count=1,
    )
    text = re.sub(
        r"(?im)^\|\s*(Notes)\s*\|\s*([^|]*)\|",
        repl_notes,
        text,
        count=1,
    )
    return text


def _append_feedback(text: str, note: str) -> str:
    block = (
        "\n\n## Open UI rejection feedback\n\n"
        f"{note}\n"
    )
    if "## Open UI rejection feedback" in text:
        return re.sub(
            r"(?s)## Open UI rejection feedback\n\n.*",
            f"## Open UI rejection feedback\n\n{note}\n",
            text,
            count=1,
        )
    return text.rstrip() + block
