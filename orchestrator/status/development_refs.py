"""Bounded read-only development evidence refs for Project Overseer (I1+)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_INCIDENT_REFS = 10
MAX_CONVERSATION_REFS = 10
MAX_EXECUTION_REFS = 10
MAX_RESEARCH_REFS = 10
MAX_EXPLAINER_REFS = 10


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return doc if isinstance(doc, dict) else None


def collect_incident_refs(
    repo_root: Path, *, limit: int = MAX_INCIDENT_REFS
) -> list[dict[str, str]]:
    """Newest-ish Sentry incident packet refs (empty if store missing)."""
    root = Path(repo_root) / ".agent" / "incidents" / "sentry"
    if not root.is_dir():
        return []
    items: list[tuple[str, dict[str, Any], Path]] = []
    for path in sorted(root.glob("*.json")):
        doc = _read_json(path)
        if not doc:
            continue
        packet_id = str(doc.get("packet_id") or path.stem)
        retrieved = str(doc.get("retrieved_at") or "")
        items.append((retrieved, doc, path))
    items.sort(key=lambda t: (t[0], t[1].get("packet_id") or ""), reverse=True)
    out: list[dict[str, str]] = []
    for _, doc, path in items[: max(0, limit)]:
        packet_id = str(doc.get("packet_id") or "")
        if not packet_id:
            continue
        out.append(
            {
                "packet_id": packet_id,
                "issue_id": str(doc.get("issue_id") or ""),
                "title": str(doc.get("title") or "")[:160],
                "severity": str(doc.get("severity") or ""),
                "mode": str(doc.get("mode") or ""),
                "path": str(path),
                "claim_kind": "external",
            }
        )
    return out


def collect_conversation_refs(
    repo_root: Path, *, limit: int = MAX_CONVERSATION_REFS
) -> list[dict[str, str]]:
    """Newest-ish conversation trajectory refs (empty if store missing)."""
    root = Path(repo_root) / ".agent" / "conversations" / "trajectories"
    if not root.is_dir():
        return []
    items: list[tuple[str, dict[str, Any], Path]] = []
    for path in sorted(root.glob("*.json")):
        doc = _read_json(path)
        if not doc:
            continue
        ingested = str(doc.get("ingested_at") or "")
        items.append((ingested, doc, path))
    items.sort(key=lambda t: (t[0], t[1].get("trajectory_id") or ""), reverse=True)
    out: list[dict[str, str]] = []
    for _, doc, path in items[: max(0, limit)]:
        traj_id = str(doc.get("trajectory_id") or "")
        if not traj_id:
            continue
        out.append(
            {
                "trajectory_id": traj_id,
                "conversation_id": str(doc.get("conversation_id") or ""),
                "model_or_source": str(doc.get("model_or_source") or ""),
                "path": str(path),
                "claim_kind": "external",
            }
        )
    return out


def collect_execution_refs(
    repo_root: Path, *, limit: int = MAX_EXECUTION_REFS
) -> list[dict[str, str]]:
    """Newest-ish T3 execution run refs (empty if store missing)."""
    root = Path(repo_root) / ".agent" / "executions" / "t3"
    if not root.is_dir():
        return []
    items: list[tuple[str, dict[str, Any], Path]] = []
    for path in sorted(root.glob("*.json")):
        doc = _read_json(path)
        if not doc:
            continue
        updated = str(doc.get("updated_at") or doc.get("created_at") or "")
        items.append((updated, doc, path))
    items.sort(key=lambda t: (t[0], t[1].get("execution_id") or ""), reverse=True)
    out: list[dict[str, str]] = []
    for _, doc, path in items[: max(0, limit)]:
        exec_id = str(doc.get("execution_id") or "")
        if not exec_id:
            continue
        out.append(
            {
                "execution_id": exec_id,
                "plan_id": str(doc.get("plan_id") or ""),
                "status": str(doc.get("status") or ""),
                "mode": str(doc.get("mode") or ""),
                "provider": str(doc.get("provider") or ""),
                "path": str(path),
                "claim_kind": "observed",
            }
        )
    return out


def collect_research_refs(
    repo_root: Path, *, limit: int = MAX_RESEARCH_REFS
) -> list[dict[str, str]]:
    """Newest-ish Apify research packet refs (empty if store missing)."""
    root = Path(repo_root) / ".agent" / "research" / "apify"
    if not root.is_dir():
        return []
    items: list[tuple[str, dict[str, Any], Path]] = []
    for path in sorted(root.glob("*.json")):
        doc = _read_json(path)
        if not doc:
            continue
        created = str(doc.get("created_at") or "")
        items.append((created, doc, path))
    items.sort(key=lambda t: (t[0], t[1].get("packet_id") or ""), reverse=True)
    out: list[dict[str, str]] = []
    for _, doc, path in items[: max(0, limit)]:
        packet_id = str(doc.get("packet_id") or "")
        if not packet_id:
            continue
        out.append(
            {
                "packet_id": packet_id,
                "query": str(doc.get("query") or "")[:160],
                "mode": str(doc.get("mode") or ""),
                "provider": str(doc.get("provider") or ""),
                "path": str(path),
                "claim_kind": "external",
            }
        )
    return out


def collect_explainer_refs(
    repo_root: Path, *, limit: int = MAX_EXPLAINER_REFS
) -> list[dict[str, str]]:
    """Newest-ish Scrimba explainer packet refs (empty if store missing)."""
    root = Path(repo_root) / ".agent" / "explainers"
    if not root.is_dir():
        return []
    items: list[tuple[str, dict[str, Any], Path]] = []
    for path in sorted(root.glob("*.json")):
        doc = _read_json(path)
        if not doc:
            continue
        created = str(doc.get("created_at") or "")
        items.append((created, doc, path))
    items.sort(key=lambda t: (t[0], t[1].get("packet_id") or ""), reverse=True)
    out: list[dict[str, str]] = []
    for _, doc, path in items[: max(0, limit)]:
        packet_id = str(doc.get("packet_id") or "")
        if not packet_id:
            continue
        out.append(
            {
                "packet_id": packet_id,
                "topic": str(doc.get("topic") or "")[:160],
                "mode": str(doc.get("mode") or ""),
                "provider": str(doc.get("provider") or ""),
                "path": str(path),
                "claim_kind": "external",
            }
        )
    return out


def attach_development_refs(snapshot: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Attach incident/conversation/execution/research/explainer refs."""
    snapshot["incident_refs"] = collect_incident_refs(repo_root)
    snapshot["conversation_refs"] = collect_conversation_refs(repo_root)
    snapshot["execution_refs"] = collect_execution_refs(repo_root)
    snapshot["research_refs"] = collect_research_refs(repo_root)
    snapshot["explainer_refs"] = collect_explainer_refs(repo_root)
    return snapshot
