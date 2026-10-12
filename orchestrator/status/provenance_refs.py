"""Bounded read-only provenance refs for Project Overseer snapshots (M54)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.behavior.provenance.store import list_provenance, provenance_dir

MAX_PROVENANCE_REFS = 10


def collect_provenance_refs(
    repo_root: Path, *, limit: int = MAX_PROVENANCE_REFS
) -> list[dict[str, str]]:
    """Return newest-first provenance refs (empty if store missing)."""
    items = list_provenance(Path(repo_root))
    if not items:
        return []
    # Newest by created_at then provenance_id
    items = sorted(
        items,
        key=lambda d: (
            str(d.get("created_at") or ""),
            str(d.get("provenance_id") or ""),
        ),
        reverse=True,
    )
    root = provenance_dir(Path(repo_root))
    out: list[dict[str, str]] = []
    for item in items[: max(0, limit)]:
        pid = str(item.get("provenance_id") or "")
        if not pid:
            continue
        out.append(
            {
                "provenance_id": pid,
                "execution_id": str(item.get("execution_id") or ""),
                "path": str(root / f"{pid}.json"),
                "prompt_bundle_hash": str(item.get("prompt_bundle_hash") or ""),
            }
        )
    return out


def attach_provenance_refs(snapshot: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Mutate snapshot in place with provenance_refs; return snapshot."""
    snapshot["provenance_refs"] = collect_provenance_refs(repo_root)
    return snapshot
