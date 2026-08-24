"""Propose persistent-role promotions from proficiency evidence — staging + PR only."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")

# Tunable promotion gates (Milestone 4)
MIN_PROFICIENCY_LEVELS = frozenset({"proficient", "expert"})
MIN_SUCCESSFUL_EXPERIENCES = 1
PROFICIENCY_RANK = {
    "novice": 0,
    "developing": 1,
    "proficient": 2,
    "expert": 3,
}


class PromotionProposeError(ValueError):
    """Raised when persistent-role proposal generation fails."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def promotions_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "agents" / "promotions"


def proposals_dir(repo_root: Path) -> Path:
    return promotions_dir(repo_root) / "proposals"


def staging_dir(repo_root: Path, agent_id: str) -> Path:
    return promotions_dir(repo_root) / "staging" / agent_id


def registry_path(repo_root: Path) -> Path:
    return promotions_dir(repo_root) / "registry.json"


def load_proficiency_records(repo_root: Path) -> list[dict]:
    root = Path(repo_root) / ".agent" / "agents" / "proficiency"
    if not root.is_dir():
        return []
    records: list[dict] = []
    for path in sorted(root.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            doc = json.load(handle)
        if isinstance(doc, dict):
            records.append(doc)
    return records


def load_persistent_role_registry(repo_root: Path) -> list[dict]:
    path = registry_path(repo_root)
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if isinstance(doc, list):
        return [item for item in doc if isinstance(item, dict)]
    if isinstance(doc, dict):
        roles = doc.get("roles") or []
        return [item for item in roles if isinstance(item, dict)]
    return []


def evaluate_gates(record: dict) -> dict[str, bool]:
    level = str(record.get("proficiency_level") or "")
    experiences = list(record.get("experience_ids") or [])
    return {
        "captain_approved_proficiency": bool(record.get("captain_approved")),
        "proficiency_level_met": level in MIN_PROFICIENCY_LEVELS,
        "experience_count_met": len(experiences) >= MIN_SUCCESSFUL_EXPERIENCES,
    }


def gates_all_passed(gates: dict[str, bool]) -> bool:
    return all(gates.values())


def _draft_agent_markdown(agent_id: str, classifications: list[str], notes: str) -> str:
    classes = ", ".join(classifications) if classifications else "general"
    return f"""---
name: {agent_id}
description: Persistent specialist role draft (staging only — Captain PR required)
---

You are the persistent specialist `{agent_id}`.

Classifications: {classes}

This file is a **staging draft** under `.agent/agents/promotions/staging/`.
Do not treat it as a live `.cursor/agents/` profile until a Captain-approved PR
copies it into the control repository agents directory and reference profiles.

Notes: {notes or "none"}

Constraints:

- Follow Captain Compass approval gates.
- Do not auto-apply matcher weights.
- Do not install Skills without Captain-approved PR.
"""


def _draft_reference_profile(
    agent_id: str,
    classifications: list[str],
    skills_trained: list[str],
) -> dict[str, Any]:
    return {
        "id": agent_id,
        "kind": "agent-profile",
        "version": "1.0.0",
        "lifecycle_stage": "AVAILABLE_SKILL",
        "maturity": "available",
        "confidence": 0.8,
        "categories": list(classifications) or ["orchestration"],
        "tags": list(classifications),
        "capabilities_provided": [
            f"persistent-role:{c}" for c in classifications
        ]
        or ["persistent-role:general"],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": [agent_id],
        "skills_trained": list(skills_trained),
        "source": {
            "type": "compass-agent-staging",
            "path": f".agent/agents/promotions/staging/{agent_id}/agent.md",
        },
        "provenance": {
            "authored_by": "compass",
            "inferred": False,
            "confidence": 0.8,
            "landing_mode": "staging_and_pr_only",
        },
    }


def build_persistent_role_proposal(
    record: dict,
    *,
    proposal_id: str | None = None,
    notes: str = "",
) -> dict:
    gates = evaluate_gates(record)
    if not gates_all_passed(gates):
        failed = [name for name, ok in gates.items() if not ok]
        raise PromotionProposeError(f"promotion gates failed: {', '.join(failed)}")

    agent_id = str(record["agent_id"])
    if not _SAFE_ID.match(agent_id):
        raise PromotionProposeError(f"unsafe agent_id: {agent_id!r}")

    return {
        "proposal_id": proposal_id or f"role-{uuid4().hex[:12]}",
        "kind": "persistent-role-promotion",
        "agent_id": agent_id,
        "proficiency_record_ids": [str(record.get("record_id") or "")],
        "experience_ids": list(record.get("experience_ids") or []),
        "classifications": list(record.get("classifications") or []),
        "proficiency_level": record.get("proficiency_level"),
        "gates_passed": gates,
        "staging_paths": {},
        "landing_mode": "staging_and_pr_only",
        "captain_approval_required": True,
        "notes": notes
        or "Staging drafts only. Open a Captain-reviewed PR to land under .cursor/agents/.",
        "created_at": _utc_now(),
    }


def write_persistent_role_proposal(repo_root: Path, proposal: dict, record: dict) -> Path:
    """Write proposal JSON + staging drafts. Never writes `.cursor/agents/`."""
    if proposal.get("landing_mode") != "staging_and_pr_only":
        raise PromotionProposeError("landing_mode must be staging_and_pr_only")
    if proposal.get("captain_approval_required") is not True:
        raise PromotionProposeError("captain_approval_required must be true")

    agent_id = str(proposal["agent_id"])
    if not _SAFE_ID.match(agent_id):
        raise PromotionProposeError(f"unsafe agent_id: {agent_id!r}")
    pid = str(proposal["proposal_id"])
    if not _SAFE_ID.match(pid):
        raise PromotionProposeError(f"unsafe proposal_id: {pid!r}")

    staging = staging_dir(repo_root, agent_id)
    staging.mkdir(parents=True, exist_ok=True)
    agent_md = staging / "agent.md"
    profile_path = staging / "reference-profile.json"
    agent_md.write_text(
        _draft_agent_markdown(
            agent_id,
            list(proposal.get("classifications") or []),
            str(proposal.get("notes") or ""),
        ),
        encoding="utf-8",
    )
    profile = _draft_reference_profile(
        agent_id,
        list(proposal.get("classifications") or []),
        list(record.get("skills_trained") or []),
    )
    with profile_path.open("w", encoding="utf-8") as handle:
        json.dump(profile, handle, indent=2, sort_keys=True)
        handle.write("\n")

    proposal = dict(proposal)
    proposal["staging_paths"] = {
        "agent_markdown": str(agent_md.relative_to(Path(repo_root))),
        "reference_profile": str(profile_path.relative_to(Path(repo_root))),
    }
    validate_document(proposal, "persistent-role-promotion.schema.json")

    out_dir = proposals_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pid}.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(proposal, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return out_path


def select_proficiency_for_agent(records: list[dict], agent_id: str) -> dict | None:
    matches = [r for r in records if str(r.get("agent_id")) == agent_id]
    if not matches:
        return None
    matches.sort(
        key=lambda r: (
            PROFICIENCY_RANK.get(str(r.get("proficiency_level") or ""), -1),
            1 if r.get("captain_approved") else 0,
            str(r.get("updated_at") or ""),
        ),
        reverse=True,
    )
    return matches[0]
