"""Operator service layer for northstar status (M51)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from orchestrator.status.compare import StatusCompareError, compare_since
from orchestrator.status.enabled import require_status_enabled
from orchestrator.status.explain import explain_status
from orchestrator.status.reconcile import draft_reconcile
from orchestrator.status.snapshot import take_snapshot
from orchestrator.status.store import StatusStoreError, list_snapshots


class StatusServiceError(ValueError):
    """Operator-facing status errors."""


def snapshot(repo_root: Path) -> dict[str, Any]:
    require_status_enabled()
    try:
        doc = take_snapshot(repo_root, persist=True, include_explanation=False)
    except StatusStoreError as exc:
        raise StatusServiceError(str(exc)) from exc
    return {"status": "snapshotted", "snapshot": doc}


def explain(repo_root: Path, *, snapshot_id: str = "") -> dict[str, Any]:
    require_status_enabled()
    try:
        doc = explain_status(repo_root, snapshot_id=snapshot_id, persist=True)
    except StatusStoreError as exc:
        raise StatusServiceError(str(exc)) from exc
    return {"status": "explained", "snapshot": doc}


def compare(repo_root: Path, *, since: str) -> dict[str, Any]:
    require_status_enabled()
    try:
        return compare_since(repo_root, since)
    except StatusCompareError as exc:
        raise StatusServiceError(str(exc)) from exc


def reconcile(repo_root: Path, *, snapshot_id: str = "") -> dict[str, Any]:
    require_status_enabled()
    try:
        return draft_reconcile(repo_root, snapshot_id=snapshot_id)
    except StatusStoreError as exc:
        raise StatusServiceError(str(exc)) from exc


def export_csv(repo_root: Path, dest: Path) -> Path:
    require_status_enabled()
    snapshots = list_snapshots(repo_root)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "snapshot_id",
        "northstar_version",
        "repository_sha",
        "skill_count_fs",
        "skill_count_docs",
        "plan_status",
        "finding_count",
        "approved_for_execution",
    ]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for snap in snapshots:
            writer.writerow(
                {
                    "snapshot_id": snap.get("snapshot_id", ""),
                    "northstar_version": snap.get("northstar_version", ""),
                    "repository_sha": snap.get("repository_sha", ""),
                    "skill_count_fs": snap.get("skill_count_fs", ""),
                    "skill_count_docs": snap.get("skill_count_docs", ""),
                    "plan_status": snap.get("plan_status", ""),
                    "finding_count": len(snap.get("findings") or []),
                    "approved_for_execution": snap.get(
                        "approved_for_execution", False
                    ),
                }
            )
    return dest
