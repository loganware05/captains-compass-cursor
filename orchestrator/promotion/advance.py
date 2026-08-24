"""Candidate lifecycle promotion helpers (Captain-gated).

Candidate ceiling for M3: SANDBOX_TESTED (never APPROVED via this module).
"""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator.providers.technology_intelligence.validate import (
    TechnologyIntelligenceValidationError,
    validate_ti_candidates,
)
from orchestrator.registry.yaml_simple import load_simple_yaml

STAGE_ORDER = (
    "DISCOVERED",
    "ANALYZED",
    "SECURITY_REVIEWED",
    "SANDBOX_TESTED",
)

# M3 candidate ceiling — Skill APPROVED requires Captain PR outside this path
CANDIDATE_CEILING = "SANDBOX_TESTED"


class PromotionError(ValueError):
    """Raised when candidate promotion is unsafe or invalid."""


def staging_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "capabilities" / "candidates" / "staging"


def _stage_index(stage: str) -> int:
    try:
        return STAGE_ORDER.index(stage)
    except ValueError as exc:
        raise PromotionError(f"unsupported lifecycle_stage: {stage!r}") from exc


def advance_lifecycle(
    candidate: dict,
    *,
    target_stage: str,
    evidence_paths: list[str] | None = None,
) -> dict:
    """Advance candidate toward target_stage without exceeding SANDBOX_TESTED."""
    validate_ti_candidates([candidate])
    if candidate.get("approved_for_execution") is not False:
        raise PromotionError("candidates must keep approved_for_execution=false")
    if target_stage not in STAGE_ORDER:
        raise PromotionError(f"unsupported target stage: {target_stage!r}")
    if _stage_index(target_stage) > _stage_index(CANDIDATE_CEILING):
        raise PromotionError(
            f"candidate promotion ceiling is {CANDIDATE_CEILING}; "
            f"cannot advance to {target_stage!r}"
        )

    current = candidate.get("lifecycle_stage", "DISCOVERED")
    if current not in STAGE_ORDER:
        raise PromotionError(f"unsupported lifecycle_stage for promotion: {current!r}")
    if _stage_index(target_stage) < _stage_index(current):
        raise PromotionError(
            f"cannot regress lifecycle from {current!r} to {target_stage!r}"
        )

    # Evidence gates for later stages
    if target_stage in ("SECURITY_REVIEWED", "SANDBOX_TESTED"):
        paths = list(evidence_paths or candidate.get("evidence_paths") or [])
        if not paths:
            raise PromotionError(
                f"{target_stage} requires at least one evidence_paths entry"
            )

    promoted = dict(candidate)
    promoted["lifecycle_stage"] = target_stage
    promoted["approved_for_execution"] = False
    if evidence_paths:
        promoted["evidence_paths"] = list(evidence_paths)
    return promoted


def advance_to_analyzed(candidate: dict) -> dict:
    """Backward-compatible helper: advance to ANALYZED."""
    return advance_lifecycle(candidate, target_stage="ANALYZED")


def write_staging_candidate(
    repo_root: Path,
    candidate: dict,
    *,
    target_stage: str = "ANALYZED",
    evidence_paths: list[str] | None = None,
) -> Path:
    promoted = advance_lifecycle(
        candidate, target_stage=target_stage, evidence_paths=evidence_paths
    )
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
    stage = candidate.get("lifecycle_stage", "DISCOVERED")
    if stage not in STAGE_ORDER:
        raise PromotionError(f"unsupported lifecycle_stage: {stage!r}")
    # Ensure at least ANALYZED before drafting a Skill sidecar proposal
    if stage == "DISCOVERED":
        promoted = advance_lifecycle(candidate, target_stage="ANALYZED")
    else:
        promoted = dict(candidate)
        promoted["approved_for_execution"] = False
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
            "candidate_stage": promoted.get("lifecycle_stage"),
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
    load_simple_yaml(path.read_text(encoding="utf-8"))
    return path


def load_candidate_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise TechnologyIntelligenceValidationError("candidate file must be a JSON object")
    if doc.get("kind") != "candidate" or "approved_for_execution" not in doc:
        from orchestrator.providers.technology_intelligence.file_provider import (
            _candidate_from_stars_shaped,
        )

        doc = _candidate_from_stars_shaped(doc).to_dict()
    return doc
