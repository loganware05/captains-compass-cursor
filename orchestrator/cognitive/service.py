"""Operator service layer for northstar brain (C1 + C2 context)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.cognitive.context import build_context
from orchestrator.cognitive.enabled import require_brain_enabled
from orchestrator.cognitive.git_facts import git_sha
from orchestrator.cognitive.store import (
    BrainStoreError,
    load_latest,
    load_snapshot,
)
from orchestrator.cognitive.sync import sync_project_state


class BrainServiceError(ValueError):
    """Operator-facing cognitive core / brain errors."""


def _freshness_for(repo_root: Path, snapshot: dict[str, Any]) -> str:
    current = git_sha(repo_root)
    recorded = str(snapshot.get("repository_sha") or "")
    if current and recorded and current == recorded:
        return "fresh"
    return "stale"


def sync(repo_root: Path) -> dict[str, Any]:
    require_brain_enabled()
    try:
        doc = sync_project_state(repo_root, persist=True)
    except BrainStoreError as exc:
        raise BrainServiceError(str(exc)) from exc
    return {"status": "synced", "snapshot": doc, "freshness": doc.get("freshness")}


def status(repo_root: Path) -> dict[str, Any]:
    require_brain_enabled()
    try:
        doc = load_latest(repo_root)
    except BrainStoreError as exc:
        raise BrainServiceError(str(exc)) from exc
    if doc is None:
        return {
            "status": "no_snapshot",
            "freshness": "stale",
            "repository_sha_head": git_sha(repo_root),
            "snapshot": None,
            "notes": "No project-state snapshot yet — run northstar brain sync",
            "approved_for_execution": False,
            "authority_mutation": False,
        }
    freshness = _freshness_for(repo_root, doc)
    return {
        "status": "ok",
        "freshness": freshness,
        "repository_sha_head": git_sha(repo_root),
        "snapshot": doc,
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def show(repo_root: Path, *, snapshot_id: str) -> dict[str, Any]:
    require_brain_enabled()
    if not snapshot_id.strip():
        raise BrainServiceError("--snapshot-id is required for brain show")
    try:
        doc = load_snapshot(repo_root, snapshot_id.strip())
    except BrainStoreError as exc:
        raise BrainServiceError(str(exc)) from exc
    freshness = _freshness_for(repo_root, doc)
    return {
        "status": "ok",
        "freshness": freshness,
        "repository_sha_head": git_sha(repo_root),
        "snapshot": doc,
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def context(
    repo_root: Path,
    *,
    query: str,
    mode: str = "hybrid",
    top_n: int = 10,
) -> dict[str, Any]:
    """C2 memory/retrieval — compose project-state + knowledge + ADR links."""
    require_brain_enabled()
    try:
        return build_context(repo_root, query, mode=mode, top_n=top_n)
    except ValueError as exc:
        raise BrainServiceError(str(exc)) from exc
