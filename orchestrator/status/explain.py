"""Explain a Project Overseer snapshot (M51)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.status.providers.stub import StubStatusProvider
from orchestrator.status.snapshot import take_snapshot
from orchestrator.status.store import StatusStoreError, load_snapshot, write_snapshot


def explain_status(
    repo_root: Path,
    *,
    snapshot_id: str = "",
    persist: bool = True,
) -> dict[str, Any]:
    provider = StubStatusProvider()
    if snapshot_id:
        try:
            snapshot = load_snapshot(repo_root, snapshot_id)
        except StatusStoreError as exc:
            raise StatusStoreError(str(exc)) from exc
    else:
        snapshot = take_snapshot(
            repo_root, persist=False, include_explanation=False
        )
    snapshot["explanation"] = provider.explain(snapshot)
    snapshot["provider"] = {"name": provider.name, "model": ""}
    if persist:
        write_snapshot(repo_root, snapshot)
    return snapshot
