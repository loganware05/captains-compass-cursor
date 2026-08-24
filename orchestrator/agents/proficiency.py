"""Captain-gated subagent proficiency records."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class ProficiencyError(ValueError):
    """Raised when proficiency recording is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def proficiency_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "agents" / "proficiency"


def build_proficiency_record(
    *,
    agent_id: str,
    classifications: list[str],
    proficiency_level: str = "developing",
    skills_trained: list[str] | None = None,
    experience_ids: list[str] | None = None,
    evidence_paths: list[str] | None = None,
    captain_approved: bool = False,
    notes: str = "",
    record_id: str | None = None,
    provenance: dict[str, Any] | None = None,
) -> dict:
    if not classifications:
        raise ProficiencyError("at least one classification is required")
    return {
        "record_id": record_id or f"prof-{uuid4().hex[:12]}",
        "agent_id": agent_id,
        "classifications": list(classifications),
        "proficiency_level": proficiency_level,
        "skills_trained": list(skills_trained or []),
        "experience_ids": list(experience_ids or []),
        "evidence_paths": list(evidence_paths or []),
        "captain_approved": captain_approved,
        "notes": notes,
        "updated_at": _utc_now(),
        "provenance": dict(provenance or {}),
    }


def write_proficiency_record(repo_root: Path, record: dict) -> Path:
    """Write proficiency JSON. Live authoritative use requires captain_approved=true."""
    validate_document(record, "agent-proficiency.schema.json")
    rid = str(record["record_id"])
    if not _SAFE_ID.match(rid):
        raise ProficiencyError(f"unsafe record_id: {rid!r}")
    agent_id = str(record["agent_id"])
    if not _SAFE_ID.match(agent_id):
        raise ProficiencyError(f"unsafe agent_id: {agent_id!r}")
    out_dir = proficiency_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{agent_id}-{rid}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
