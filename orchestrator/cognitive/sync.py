"""Build and persist Cognitive Core project-state snapshots (C1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.cognitive.git_facts import git_branch, git_sha, working_tree_dirty
from orchestrator.cognitive.store import (
    BrainStoreError,
    snapshot_id_for,
    write_snapshot,
)
from orchestrator.status.drift import detect_drift
from orchestrator.status.enabled import status_enabled
from orchestrator.status.snapshot import take_snapshot


def build_project_state(repo_root: Path) -> dict[str, Any]:
    """Collect local-git facts; optionally compose Overseer status snapshot id."""
    sha = git_sha(repo_root)
    branch = git_branch(repo_root)
    dirty = working_tree_dirty(repo_root)
    drift = detect_drift(repo_root)

    sources: list[str] = ["local_git"]
    citations: list[dict[str, str]] = [
        {"kind": "git", "ref": f"HEAD={sha}", "claim_kind": "observed"},
        {
            "kind": "version",
            "ref": f"VERSION={drift.get('northstar_version') or ''}",
            "claim_kind": "observed",
        },
        {
            "kind": "file",
            "ref": "IMPLEMENTATION_PLAN.md",
            "claim_kind": "documented",
        },
        {"kind": "file", "ref": "PROGRESS.md", "claim_kind": "documented"},
    ]

    composed_status_id: str | None = None
    if status_enabled():
        # Optional compose: persist an Overseer snapshot and cite its id.
        # Does not require callers to run `northstar status` separately.
        try:
            status_doc = take_snapshot(
                repo_root,
                persist=True,
                include_explanation=False,
                write_memory=False,
            )
            composed_status_id = str(status_doc.get("snapshot_id") or "") or None
            if composed_status_id:
                sources.append("status_compose")
                citations.append(
                    {
                        "kind": "status_snapshot",
                        "ref": composed_status_id,
                        "claim_kind": "observed",
                    }
                )
        except Exception:
            # Status compose is best-effort; C1 remains local-git authoritative.
            composed_status_id = None

    snapshot: dict[str, Any] = {
        "repository_sha": sha,
        "repository_branch": branch,
        "northstar_version": drift.get("northstar_version") or "",
        "freshness": "fresh",
        "sources": sources,
        "citations": citations,
        "active_plan_id": drift.get("active_plan_id") or "",
        "plan_status": drift.get("plan_status") or "",
        "composed_status_snapshot_id": composed_status_id,
        "skill_count_fs": int(drift.get("skill_count_fs") or 0),
        "working_tree_dirty": dirty,
        "notes": (
            "Cognitive Core C1 project-state snapshot (local Git). "
            "Does not approve plans or mutate authority."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    snapshot["snapshot_id"] = snapshot_id_for(snapshot)
    return snapshot


def sync_project_state(repo_root: Path, *, persist: bool = True) -> dict[str, Any]:
    snapshot = build_project_state(repo_root)
    if persist:
        try:
            write_snapshot(repo_root, snapshot)
        except BrainStoreError:
            raise
    return snapshot
