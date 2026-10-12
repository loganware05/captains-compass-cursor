"""Explain a Project Overseer snapshot (M51/M52)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.status.memory import write_overseer_memory
from orchestrator.status.providers.http import HttpStatusProviderError
from orchestrator.status.providers.select import (
    StatusProviderSelectError,
    select_status_provider,
)
from orchestrator.status.snapshot import take_snapshot
from orchestrator.status.store import StatusStoreError, load_snapshot, write_snapshot


def explain_status(
    repo_root: Path,
    *,
    snapshot_id: str = "",
    persist: bool = True,
    write_memory: bool = True,
) -> dict[str, Any]:
    try:
        provider = select_status_provider()
    except StatusProviderSelectError as exc:
        raise StatusStoreError(str(exc)) from exc
    if snapshot_id:
        try:
            snapshot = load_snapshot(repo_root, snapshot_id)
        except StatusStoreError as exc:
            raise StatusStoreError(str(exc)) from exc
    else:
        snapshot = take_snapshot(
            repo_root, persist=False, include_explanation=False
        )
    try:
        snapshot["explanation"] = provider.explain(snapshot)
    except HttpStatusProviderError as exc:
        raise StatusStoreError(str(exc)) from exc
    snapshot["provider"] = {
        "name": getattr(provider, "name", "unknown"),
        "model": getattr(provider, "model", "") or "",
    }
    if persist:
        write_snapshot(repo_root, snapshot)
    if write_memory:
        write_overseer_memory(repo_root, snapshot)
    return snapshot
