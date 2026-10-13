"""Persist Cognitive Core project-state snapshots (C1)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.providers.decision.state import redact_text
from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA_VERSION = "1"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class BrainStoreError(ValueError):
    """Raised when project-state persistence is unsafe or invalid."""


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def project_state_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "project-state"


def snapshots_dir(repo_root: Path) -> Path:
    return project_state_root(repo_root) / "snapshots"


def latest_path(repo_root: Path) -> Path:
    return project_state_root(repo_root) / "latest.json"


def evidence_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "c1-cognitive-core-source-of-truth"


def ensure_layout(repo_root: Path) -> None:
    for path in (snapshots_dir(repo_root), evidence_root(repo_root)):
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise BrainStoreError(f"unsafe {label}: {value!r}")
    return value


def _write_json(path: Path, doc: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    return path


def write_snapshot(repo_root: Path, snapshot: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(snapshot)
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = SCHEMA_VERSION
    payload.setdefault("created_at", _utc_now())
    if payload.get("notes"):
        payload["notes"] = redact_text(str(payload["notes"]))
    citations = []
    for item in payload.get("citations") or []:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        entry["ref"] = redact_text(str(entry.get("ref") or ""))
        citations.append(entry)
    payload["citations"] = citations
    try:
        validate_document(payload, "project-state-snapshot.schema.json")
    except ValidationError as exc:
        raise BrainStoreError(str(exc)) from exc
    sid = _safe_id(str(payload["snapshot_id"]), label="snapshot_id")
    path = snapshots_dir(repo_root) / f"{sid}.json"
    _write_json(path, payload)
    pointer = {
        "snapshot_id": sid,
        "repository_sha": payload.get("repository_sha") or "",
        "northstar_version": payload.get("northstar_version") or "",
        "freshness": payload.get("freshness") or "fresh",
        "path": str(path.relative_to(Path(repo_root))),
        "created_at": payload["created_at"],
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    _write_json(latest_path(repo_root), pointer)
    _write_json(evidence_root(repo_root) / f"{sid}-summary.json", pointer)
    snapshot.clear()
    snapshot.update(payload)
    return path


def load_snapshot(repo_root: Path, snapshot_id: str) -> dict[str, Any]:
    path = snapshots_dir(repo_root) / f"{_safe_id(snapshot_id, label='snapshot_id')}.json"
    if not path.is_file():
        raise BrainStoreError(f"snapshot not found: {snapshot_id}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "project-state-snapshot.schema.json")
    return doc


def load_latest(repo_root: Path) -> dict[str, Any] | None:
    path = latest_path(repo_root)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        return None
    sid = str(doc.get("snapshot_id") or "")
    if not sid:
        return None
    return load_snapshot(repo_root, sid)


def snapshot_id_for(payload: dict[str, Any]) -> str:
    material = {
        "repository_sha": payload.get("repository_sha"),
        "northstar_version": payload.get("northstar_version"),
        "sources": payload.get("sources"),
        "active_plan_id": payload.get("active_plan_id"),
        "skill_count_fs": payload.get("skill_count_fs"),
    }
    digest = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:12]
    return f"pstate-{digest}"
