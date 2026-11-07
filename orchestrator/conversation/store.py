"""Persist conversation trajectories under .agent/conversations/."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,160}$")


class ConversationStoreError(ValueError):
    """Raised when conversation store IO fails."""


def conversations_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "conversations"


def trajectories_dir(repo_root: Path) -> Path:
    return conversations_root(repo_root) / "trajectories"


def incoming_dir(repo_root: Path) -> Path:
    return conversations_root(repo_root) / "incoming"


def ingest_log_dir(repo_root: Path) -> Path:
    return conversations_root(repo_root) / "ingest-log"


def exemplar_drafts_dir(repo_root: Path) -> Path:
    return conversations_root(repo_root) / "exemplar-drafts"


def ensure_layout(repo_root: Path) -> None:
    for path in (
        trajectories_dir(repo_root),
        incoming_dir(repo_root),
        ingest_log_dir(repo_root),
        exemplar_drafts_dir(repo_root),
    ):
        path.mkdir(parents=True, exist_ok=True)


def assert_safe_id(value: str, label: str = "trajectory_id") -> None:
    if not value or not _SAFE_ID.match(value):
        raise ConversationStoreError(f"unsafe {label}: {value!r}")


def write_trajectory(repo_root: Path, doc: dict[str, Any]) -> Path:
    validate_document(doc, "conversation-trajectory.schema.json")
    traj_id = str(doc["trajectory_id"])
    assert_safe_id(traj_id)
    ensure_layout(repo_root)
    path = trajectories_dir(repo_root) / f"{traj_id}.json"
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_trajectory(repo_root: Path, trajectory_id: str) -> dict[str, Any]:
    assert_safe_id(trajectory_id)
    path = trajectories_dir(repo_root) / f"{trajectory_id}.json"
    if not path.is_file():
        raise ConversationStoreError(f"trajectory not found: {trajectory_id}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConversationStoreError(str(exc)) from exc
    validate_document(doc, "conversation-trajectory.schema.json")
    return doc


def list_trajectory_docs(repo_root: Path) -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    out: list[dict[str, Any]] = []
    for path in sorted(trajectories_dir(repo_root).glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            validate_document(doc, "conversation-trajectory.schema.json")
            out.append(doc)
        except Exception:
            continue
    return out


def write_ingest_log(repo_root: Path, log_id: str, payload: dict[str, Any]) -> Path:
    assert_safe_id(log_id, "log_id")
    ensure_layout(repo_root)
    path = ingest_log_dir(repo_root) / f"{log_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_exemplar_draft(repo_root: Path, draft_id: str, payload: dict[str, Any]) -> Path:
    assert_safe_id(draft_id, "draft_id")
    ensure_layout(repo_root)
    path = exemplar_drafts_dir(repo_root) / f"{draft_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
