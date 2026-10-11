"""Build and persist Project Overseer snapshots (M51)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from orchestrator.status.drift import detect_drift
from orchestrator.status.providers.stub import StubStatusProvider
from orchestrator.status.store import (
    StatusStoreError,
    snapshot_id_for,
    write_snapshot,
)


def _git_sha(repo_root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def build_snapshot(
    repo_root: Path,
    *,
    provider: StubStatusProvider | None = None,
    include_explanation: bool = False,
) -> dict[str, Any]:
    drift = detect_drift(repo_root)
    provider = provider or StubStatusProvider()
    snapshot: dict[str, Any] = {
        "repository_sha": _git_sha(repo_root),
        "northstar_version": drift.get("northstar_version") or "",
        "memory_docs": drift.get("memory_docs") or {},
        "skill_count_fs": int(drift.get("skill_count_fs") or 0),
        "skill_count_docs": drift.get("skill_count_docs"),
        "active_plan_id": drift.get("active_plan_id") or "",
        "plan_status": drift.get("plan_status") or "",
        "progress_plan_id": drift.get("progress_plan_id") or "",
        "findings": list(drift.get("findings") or []),
        "provider": {"name": provider.name, "model": ""},
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    snapshot["snapshot_id"] = snapshot_id_for(snapshot)
    if include_explanation:
        snapshot["explanation"] = provider.explain(snapshot)
    return snapshot


def take_snapshot(
    repo_root: Path,
    *,
    persist: bool = True,
    include_explanation: bool = False,
) -> dict[str, Any]:
    snapshot = build_snapshot(
        repo_root, include_explanation=include_explanation
    )
    if persist:
        try:
            write_snapshot(repo_root, snapshot)
        except StatusStoreError:
            raise
    return snapshot
