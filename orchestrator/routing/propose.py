"""Build routing proposals from Experience fixtures — never mutates matcher WEIGHTS."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.matcher.score import get_weights
from orchestrator.routing.decomposition import build_decomposition_hints, merge_decomposition_hints
from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class RoutingError(ValueError):
    """Raised when routing proposal generation fails."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def proposals_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "routing" / "proposals"


def load_experiences(paths: list[Path]) -> list[dict]:
    docs: list[dict] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            doc = json.load(handle)
        if not isinstance(doc, dict):
            raise RoutingError(f"experience must be object: {path}")
        docs.append(doc)
    return docs


def build_routing_proposal(
    experiences: list[dict],
    *,
    proposal_id: str | None = None,
    notes: str = "",
) -> dict:
    """Derive informational skill confidence deltas; matcher suggestions copy current WEIGHTS."""
    skill_counts: dict[str, dict[str, int]] = {}
    experience_ids: list[str] = []
    for exp in experiences:
        eid = str(exp.get("experience_id") or "")
        if eid:
            experience_ids.append(eid)
        outcome = exp.get("outcome", "pending")
        for skill in exp.get("skills_used") or []:
            skill = str(skill)
            bucket = skill_counts.setdefault(skill, {"success": 0, "other": 0})
            if outcome == "success":
                bucket["success"] += 1
            else:
                bucket["other"] += 1

    deltas: list[dict[str, Any]] = []
    for skill_id, counts in sorted(skill_counts.items()):
        total = counts["success"] + counts["other"]
        if total == 0:
            continue
        # Bounded informational delta (±0.05 max per skill in M3)
        raw = (counts["success"] - counts["other"]) / total
        delta = round(max(-0.05, min(0.05, raw * 0.05)), 4)
        deltas.append(
            {
                "skill_id": skill_id,
                "delta": delta,
                "rationale": (
                    f"From {total} Experience(s): success={counts['success']} "
                    f"other={counts['other']} (proposal-only; not applied)"
                ),
            }
        )

    decomposition_hints = build_decomposition_hints(experiences)
    weight_suggestions = merge_decomposition_hints(get_weights(), decomposition_hints)

    return {
        "proposal_id": proposal_id or f"route-{uuid4().hex[:12]}",
        "kind": "routing-proposal",
        "based_on_experiences": experience_ids,
        "skill_confidence_deltas": deltas,
        "decomposition_hints": decomposition_hints,
        "matcher_weight_suggestions": weight_suggestions,
        "auto_apply": False,
        "captain_approved": False,
        "notes": notes
        or (
            "Proposal-only until Captain sets captain_approved=true and runs "
            "apply-routing-proposal.sh under autonomy budget"
        ),
        "created_at": _utc_now(),
        "captain_approval_required": True,
    }


def write_routing_proposal(repo_root: Path, proposal: dict) -> Path:
    if proposal.get("auto_apply") is not False:
        raise RoutingError("auto_apply must be false")
    validate_document(proposal, "routing-proposal.schema.json")
    pid = str(proposal["proposal_id"])
    if not _SAFE_ID.match(pid):
        raise RoutingError(f"unsafe proposal_id: {pid!r}")
    out_dir = proposals_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{pid}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(proposal, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
