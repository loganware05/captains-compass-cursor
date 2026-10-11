"""Draft proposal-only reconcile actions from a snapshot (M51)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from orchestrator.status.explain import explain_status
from orchestrator.status.store import write_proposal


def _proposal_id(snapshot_id: str, actions: list[dict[str, Any]]) -> str:
    material = f"{snapshot_id}|{len(actions)}|{actions}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
    return f"srec-{digest}"


def draft_reconcile(
    repo_root: Path,
    *,
    snapshot_id: str = "",
) -> dict[str, Any]:
    snapshot = explain_status(
        repo_root, snapshot_id=snapshot_id, persist=True
    )
    actions: list[dict[str, Any]] = []
    for finding in snapshot.get("findings") or []:
        if finding.get("severity") not in {"warn", "error"}:
            continue
        kind = str(finding.get("kind") or "unknown")
        target = "PROJECT_CONTEXT.md"
        if kind == "version_progress_mismatch":
            target = "PROGRESS.md"
        elif kind == "missing_memory_docs":
            target = "project memory docs"
        elif kind.startswith("plan_"):
            target = "IMPLEMENTATION_PLAN.md / PROGRESS.md"
        elif kind == "skill_count_mismatch":
            target = "PROJECT_CONTEXT.md"
        actions.append(
            {
                "action_id": f"act-{finding.get('finding_id')}",
                "target": target,
                "summary": (
                    f"Review and update {target} to resolve: "
                    f"{finding.get('summary')}"
                ),
                "finding_ids": [str(finding.get("finding_id") or "")],
                "suggested_patch": (
                    "# proposal-only — do not auto-apply\n"
                    f"# finding: {finding.get('finding_id')}\n"
                    f"# {finding.get('summary')}\n"
                ),
            }
        )
    sid = str(snapshot.get("snapshot_id") or "")
    proposal = {
        "proposal_id": _proposal_id(sid, actions),
        "snapshot_id": sid,
        "applied": False,
        "actions": actions,
        "notes": (
            "Proposal-only reconcile draft. Captain must apply via reviewed PR. "
            "M51 never rewrites project memory automatically."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    path = write_proposal(repo_root, proposal)
    return {
        "status": "reconcile_drafted",
        "proposal": proposal,
        "path": str(path),
        "applied": False,
    }
