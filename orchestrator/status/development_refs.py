"""Bounded read-only development evidence refs for Project Overseer (I1+)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_INCIDENT_REFS = 10
MAX_CONVERSATION_REFS = 10


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


def attach_development_refs(snapshot: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Attach incident_refs + conversation_refs; return snapshot."""
    snapshot["incident_refs"] = collect_incident_refs(repo_root)
    snapshot["conversation_refs"] = collect_conversation_refs(repo_root)
    return snapshot
