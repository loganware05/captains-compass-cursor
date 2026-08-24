"""Candidate lifecycle promotion helpers (Captain-gated).

Stages: DISCOVERED → ANALYZED → SECURITY_REVIEWED → SANDBOX_TESTED →
APPROVED → AVAILABLE_SKILL → PROVEN_SKILL.

Post-sandbox stages (APPROVED+) require captain_approved=True.
AVAILABLE_SKILL writes install proposals only — never live Skills.
PROVEN_SKILL requires ≥2 successful Experiences by default.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from orchestrator.providers.technology_intelligence.validate import (
    TechnologyIntelligenceValidationError,
    validate_ti_candidates,
)
from orchestrator.registry.yaml_simple import load_simple_yaml
from orchestrator.telemetry.store import list_experiences

STAGE_ORDER = (
    "DISCOVERED",
    "ANALYZED",
    "SECURITY_REVIEWED",
    "SANDBOX_TESTED",
    "APPROVED",
    "AVAILABLE_SKILL",
    "PROVEN_SKILL",
)

# Soft ceiling for stages that do not require --captain-approved
PRE_CAPTAIN_CEILING = "SANDBOX_TESTED"
CANDIDATE_CEILING = "PROVEN_SKILL"

DEFAULT_PROVEN_SUCCESS_THRESHOLD = 2


class PromotionError(ValueError):
    """Raised when candidate promotion is unsafe or invalid."""


def staging_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "capabilities" / "candidates" / "staging"


def available_proposals_dir(repo_root: Path) -> Path:
    return (
        Path(repo_root)
        / ".agent"
        / "capabilities"
        / "candidates"
        / "available-proposals"
    )


def proven_threshold() -> int:
    raw = os.environ.get("COMPASS_PROVEN_SUCCESS_THRESHOLD", "").strip()
    if raw:
        try:
            value = int(raw)
        except ValueError as exc:
            raise PromotionError(
                f"invalid COMPASS_PROVEN_SUCCESS_THRESHOLD: {raw!r}"
            ) from exc
        if value < 1:
            raise PromotionError("COMPASS_PROVEN_SUCCESS_THRESHOLD must be >= 1")
        return value
    return DEFAULT_PROVEN_SUCCESS_THRESHOLD


def _stage_index(stage: str) -> int:
    try:
        return STAGE_ORDER.index(stage)
    except ValueError as exc:
        raise PromotionError(f"unsupported lifecycle_stage: {stage!r}") from exc


def count_successful_experiences_for_skill(
    repo_root: Path,
    skill_slug: str,
    *,
    candidate_id: str | None = None,
) -> int:
    """Count Experiences with outcome=success that reference skill_slug or candidate_id."""
    count = 0
    needles = {skill_slug}
    if candidate_id:
        needles.add(candidate_id)
    for exp in list_experiences(repo_root):
        if exp.get("outcome") != "success":
            continue
        skills = {str(s) for s in (exp.get("skills_used") or [])}
        if skills & needles:
            count += 1
    return count


def advance_lifecycle(
    candidate: dict,
    *,
    target_stage: str,
    evidence_paths: list[str] | None = None,
    captain_approved: bool = False,
    skill_slug: str | None = None,
    repo_root: Path | None = None,
) -> dict:
    """Advance candidate toward target_stage with stage-specific gates."""
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

    if _stage_index(target_stage) > _stage_index(PRE_CAPTAIN_CEILING) and not captain_approved:
        raise PromotionError(
            f"{target_stage} requires --captain-approved "
            f"(stages after {PRE_CAPTAIN_CEILING})"
        )

    # Evidence gates for later stages
    if target_stage in (
        "SECURITY_REVIEWED",
        "SANDBOX_TESTED",
        "APPROVED",
        "AVAILABLE_SKILL",
        "PROVEN_SKILL",
    ):
        paths = list(evidence_paths or candidate.get("evidence_paths") or [])
        if not paths:
            raise PromotionError(
                f"{target_stage} requires at least one evidence_paths entry"
            )

    if target_stage == "PROVEN_SKILL":
        if repo_root is None:
            raise PromotionError("PROVEN_SKILL requires repo_root for Experience lookup")
        slug = skill_slug or str(
            (candidate.get("provenance") or {}).get("skill_slug")
            or candidate.get("id")
            or ""
        )
        if not slug:
            raise PromotionError("PROVEN_SKILL requires skill_slug or candidate id")
        successes = count_successful_experiences_for_skill(
            Path(repo_root),
            slug,
            candidate_id=str(candidate.get("id") or "") or None,
        )
        threshold = proven_threshold()
        if successes < threshold:
            raise PromotionError(
                f"PROVEN_SKILL requires ≥{threshold} successful Experiences "
                f"referencing {slug!r}; found {successes}"
            )

    promoted = dict(candidate)
    promoted["lifecycle_stage"] = target_stage
    promoted["approved_for_execution"] = False
    if evidence_paths:
        promoted["evidence_paths"] = list(evidence_paths)
    if skill_slug:
        provenance = dict(promoted.get("provenance") or {})
        provenance["skill_slug"] = skill_slug
        promoted["provenance"] = provenance
    if captain_approved and _stage_index(target_stage) > _stage_index(PRE_CAPTAIN_CEILING):
        promoted["captain_approved"] = True
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
    captain_approved: bool = False,
    skill_slug: str | None = None,
) -> Path:
    promoted = advance_lifecycle(
        candidate,
        target_stage=target_stage,
        evidence_paths=evidence_paths,
        captain_approved=captain_approved,
        skill_slug=skill_slug,
        repo_root=repo_root,
    )
    validate_ti_candidates([promoted])
    out_dir = staging_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{promoted['id']}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(promoted, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def write_available_skill_proposal(
    repo_root: Path,
    candidate: dict,
    skill_slug: str,
) -> Path:
    """Write AVAILABLE_SKILL install proposal — never under .cursor/skills/."""
    if not skill_slug or "/" in skill_slug or ".." in skill_slug:
        raise PromotionError(f"invalid skill slug: {skill_slug!r}")
    if candidate.get("lifecycle_stage") not in ("APPROVED", "AVAILABLE_SKILL"):
        raise PromotionError(
            "AVAILABLE_SKILL proposal requires candidate at APPROVED or AVAILABLE_SKILL"
        )
    if candidate.get("approved_for_execution") is not False:
        raise PromotionError("candidates must keep approved_for_execution=false")

    out_dir = available_proposals_dir(repo_root) / skill_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    proposal = {
        "kind": "available-skill-proposal",
        "skill_slug": skill_slug,
        "lifecycle_stage": "AVAILABLE_SKILL",
        "candidate_id": candidate.get("id"),
        "approved_for_execution": False,
        "captain_approval_required": True,
        "install_target": f".cursor/skills/{skill_slug}/",
        "notes": (
            "Proposal only — copy into .cursor/skills/ via Captain-reviewed PR; "
            "never auto-install"
        ),
        "evidence_paths": list(candidate.get("evidence_paths") or []),
        "capabilities_provided": list(candidate.get("capabilities_provided") or []),
    }
    path = out_dir / "proposal.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(proposal, handle, indent=2, sort_keys=True)
        handle.write("\n")

    draft_path = out_dir / "capability.yaml"
    lines = [
        f"id: {skill_slug}",
        'version: "0.1.0"',
        "kind: skill",
        "source:",
        "  type: compass-skill",
        f"  path: .cursor/skills/{skill_slug}/SKILL.md",
        "lifecycle_stage: AVAILABLE_SKILL",
        "capabilities_provided:",
    ]
    for cap in proposal["capabilities_provided"]:
        lines.append(f"  - {cap}")
    lines.extend(
        [
            "security_sensitivity: medium",
            "provenance:",
            "  inferred: false",
            f"  from_candidate: {candidate.get('id')}",
            "  captain_approval_required: true",
            "notes: AVAILABLE_SKILL proposal — Captain PR required before registry use",
            "",
        ]
    )
    draft_path.write_text("\n".join(lines), encoding="utf-8")
    load_simple_yaml(draft_path.read_text(encoding="utf-8"))
    return path


def draft_skill_sidecar_proposal(candidate: dict, skill_slug: str) -> dict:
    """Build a draft capability.yaml payload for a Captain-approved Skill PR."""
    if not skill_slug or "/" in skill_slug or ".." in skill_slug:
        raise PromotionError(f"invalid skill slug: {skill_slug!r}")
    stage = candidate.get("lifecycle_stage", "DISCOVERED")
    if stage not in STAGE_ORDER:
        raise PromotionError(f"unsupported lifecycle_stage: {stage!r}")
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
        from orchestrator.providers.technology_intelligence.mapper import (
            candidate_from_stars_shaped,
        )

        doc = candidate_from_stars_shaped(doc).to_dict()
    return doc
