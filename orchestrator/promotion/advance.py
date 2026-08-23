"""Candidate lifecycle promotion helpers (Captain-gated)."""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator.providers.technology_intelligence.validate import (
    TechnologyIntelligenceValidationError,
    validate_ti_candidates,
)
from orchestrator.registry.yaml_simple import load_simple_yaml


class PromotionError(ValueError):
    """Raised when candidate promotion is unsafe or invalid."""


def staging_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "capabilities" / "candidates" / "staging"


def advance_to_analyzed(candidate: dict) -> dict:
    validate_ti_candidates([candidate])
    if candidate.get("approved_for_execution") is not False:
        raise PromotionError("candidates must keep approved_for_execution=false")
    stage = candidate.get("lifecycle_stage", "DISCOVERED")
    if stage not in ("DISCOVERED", "ANALYZED"):
        raise PromotionError(f"unsupported lifecycle_stage for M2 promotion: {stage!r}")
    promoted = dict(candidate)
    promoted["lifecycle_stage"] = "ANALYZED"
    promoted["approved_for_execution"] = False
    return promoted


def write_staging_candidate(repo_root: Path, candidate: dict) -> Path:
    promoted = advance_to_analyzed(candidate)
    validate_ti_candidates([promoted])
    out_dir = staging_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{promoted['id']}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(promoted, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def draft_skill_sidecar_proposal(candidate: dict, skill_slug: str) -> dict:
    """Build a draft capability.yaml payload for a Captain-approved Skill PR."""
    if not skill_slug or "/" in skill_slug or ".." in skill_slug:
        raise PromotionError(f"invalid skill slug: {skill_slug!r}")
    promoted = advance_to_analyzed(candidate)
    return {
        "id": skill_slug,
        "version": promoted.get("version", "0.1.0"),
        "kind": "skill",
        "source": {
            "type": "compass-skill",
            "path": f".cursor/skills/{skill_slug}/SKILL.md",
        },
        "lifecycle_stage": "AVAILABLE_SKILL",
        "capabilities_provided": list(promoted.get("capabilities_provided") or []),
        "security_sensitivity": "medium",
        "provenance": {
            "inferred": False,
            "from_candidate": promoted.get("id"),
            "discovery_signal": promoted.get("discovery_signal", ""),
            "captain_approval_required": True,
        },
        "notes": (
            "Draft from candidate promotion — requires Captain-approved PR before registry use"
        ),
    }


def write_skill_sidecar_draft(repo_root: Path, candidate: dict, skill_slug: str) -> Path:
    """Write draft capability.yaml under staging/skills/<slug>/ (not live Skills)."""
    draft = draft_skill_sidecar_proposal(candidate, skill_slug)
    out_dir = (
        Path(repo_root)
        / ".agent"
        / "capabilities"
        / "candidates"
        / "skill-drafts"
        / skill_slug
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "capability.yaml"
    lines = [
        f"id: {draft['id']}",
        f'version: "{draft["version"]}"',
        "kind: skill",
        "source:",
        "  type: compass-skill",
        f"  path: .cursor/skills/{skill_slug}/SKILL.md",
        "lifecycle_stage: AVAILABLE_SKILL",
        "capabilities_provided:",
    ]
    for cap in draft["capabilities_provided"]:
        lines.append(f"  - {cap}")
    lines.extend(
        [
            "security_sensitivity: medium",
            "provenance:",
            "  inferred: false",
            f"  from_candidate: {draft['provenance']['from_candidate']}",
            "  captain_approval_required: true",
            f"notes: {draft['notes']}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    # Round-trip parse check with simple YAML loader
    load_simple_yaml(path.read_text(encoding="utf-8"))
    return path


def load_candidate_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise TechnologyIntelligenceValidationError("candidate file must be a JSON object")
    # Allow redacted Stars-shaped fixtures by normalizing through CandidateCapability
    if doc.get("kind") != "candidate" or "approved_for_execution" not in doc:
        from orchestrator.providers.technology_intelligence.file_provider import (
            _candidate_from_stars_shaped,
        )

        doc = _candidate_from_stars_shaped(doc).to_dict()
    return doc
