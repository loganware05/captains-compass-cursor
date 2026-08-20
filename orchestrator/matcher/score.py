"""Deterministic Skill ranking against required capabilities."""

from __future__ import annotations

from dataclasses import dataclass

WEIGHTS = {
    "capability_overlap": 0.45,
    "stack_match": 0.20,
    "lifecycle_stage": 0.15,
    "security_bonus": 0.10,
    "agent_affinity": 0.10,
}

LIFECYCLE_SCORES = {
    "PROVEN_SKILL": 1.0,
    "AVAILABLE_SKILL": 0.7,
    "APPROVED": 0.6,
    "SANDBOX_TESTED": 0.5,
    "SECURITY_REVIEWED": 0.4,
    "ANALYZED": 0.3,
    "DISCOVERED": 0.0,
}

SECURITY_SKILL_IDS = frozenset(
    {
        "security-review",
        "dependency-supply-chain",
    }
)


@dataclass
class RankedSkill:
    skill_id: str
    score: float
    scoring_breakdown: list[dict[str, str | float]]


def _overlap_score(required: set[str], provided: set[str]) -> float:
    if not required:
        return 0.0
    if not provided:
        return 0.0
    return len(required & provided) / len(required)


def _stack_score(required_stacks: set[str], compatible_stacks: set[str]) -> float:
    if not required_stacks:
        return 0.5
    if "any" in compatible_stacks:
        return 0.6
    if not compatible_stacks:
        return 0.0
    return len(required_stacks & compatible_stacks) / len(required_stacks)


def _lifecycle_score(stage: str | None) -> float:
    return LIFECYCLE_SCORES.get(stage or "", 0.0)


def _security_bonus(skill_id: str, security_sensitive: bool) -> float:
    if not security_sensitive:
        return 0.0
    if skill_id in SECURITY_SKILL_IDS:
        return 1.0
    return 0.0


def _affinity_score(skill: dict, preferred_profile: str | None) -> float:
    if not preferred_profile:
        return 0.5
    affinities = set(skill.get("agent_affinity") or [])
    if preferred_profile in affinities:
        return 1.0
    return 0.0


def is_eligible_skill(skill: dict) -> bool:
    """Candidates and non-skills are never ranked for execution."""
    if skill.get("kind") != "skill":
        return False
    if skill.get("approved_for_execution") is False:
        return False
    lifecycle = skill.get("lifecycle_stage", "")
    if lifecycle == "DISCOVERED":
        return False
    return True


def score_skill(
    skill: dict,
    required_capabilities: list[str],
    *,
    stacks: list[str] | None = None,
    security_sensitive: bool = False,
    preferred_profile: str | None = None,
) -> RankedSkill:
    skill_id = str(skill["id"])
    provided = set(skill.get("capabilities_provided") or [])
    required = set(required_capabilities)
    required_stacks = set(stacks or [])
    compatible = set(skill.get("compatible_stacks") or [])

    overlap = _overlap_score(required, provided)
    stack = _stack_score(required_stacks, compatible)
    lifecycle = _lifecycle_score(skill.get("lifecycle_stage"))
    security = _security_bonus(skill_id, security_sensitive)
    affinity = _affinity_score(skill, preferred_profile)

    total = (
        overlap * WEIGHTS["capability_overlap"]
        + stack * WEIGHTS["stack_match"]
        + lifecycle * WEIGHTS["lifecycle_stage"]
        + security * WEIGHTS["security_bonus"]
        + affinity * WEIGHTS["agent_affinity"]
    )

    breakdown = [
        {
            "factor": "capability_overlap",
            "score": round(overlap * WEIGHTS["capability_overlap"], 4),
            "note": f"matched {len(required & provided)}/{len(required) or 0} required",
        },
        {
            "factor": "stack_match",
            "score": round(stack * WEIGHTS["stack_match"], 4),
            "note": f"stacks={sorted(required_stacks)} compatible={sorted(compatible)}",
        },
        {
            "factor": "lifecycle_stage",
            "score": round(lifecycle * WEIGHTS["lifecycle_stage"], 4),
            "note": str(skill.get("lifecycle_stage", "unknown")),
        },
        {
            "factor": "security_bonus",
            "score": round(security * WEIGHTS["security_bonus"], 4),
            "note": f"security_sensitive={security_sensitive}",
        },
        {
            "factor": "agent_affinity",
            "score": round(affinity * WEIGHTS["agent_affinity"], 4),
            "note": f"preferred_profile={preferred_profile or 'none'}",
        },
    ]

    return RankedSkill(
        skill_id=skill_id,
        score=round(total, 4),
        scoring_breakdown=breakdown,
    )


def rank_skills(
    skills: list[dict],
    required_capabilities: list[str],
    *,
    stacks: list[str] | None = None,
    security_sensitive: bool = False,
    preferred_profile: str | None = None,
    min_score: float = 0.0,
) -> list[RankedSkill]:
    ranked: list[RankedSkill] = []
    for skill in skills:
        if not is_eligible_skill(skill):
            continue
        result = score_skill(
            skill,
            required_capabilities,
            stacks=stacks,
            security_sensitive=security_sensitive,
            preferred_profile=preferred_profile,
        )
        if result.score >= min_score:
            ranked.append(result)
    ranked.sort(key=lambda item: (-item.score, item.skill_id))
    return ranked


def find_capability_gaps(required_capabilities: list[str], skills: list[dict]) -> list[str]:
    """Return required capabilities no eligible Skill provides."""
    provided: set[str] = set()
    for skill in skills:
        if not is_eligible_skill(skill):
            continue
        provided.update(skill.get("capabilities_provided") or [])
    return [cap for cap in required_capabilities if cap not in provided]
