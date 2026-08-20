"""End-to-end capability resolution: intent inference + Skill ranking."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from orchestrator.intent.infer_capabilities import IntentResult, infer_capabilities
from orchestrator.matcher.score import RankedSkill, find_capability_gaps, rank_skills
from orchestrator.registry.load import load_registry, registry_skills


@dataclass
class ResolveResult:
    intent: IntentResult
    ranked_skills: list[RankedSkill]
    capability_gaps: list[str]
    recommended_skill_ids: list[str] = field(default_factory=list)


def resolve_capabilities(
    repo_root: Path,
    objective: str,
    context: dict | None = None,
    *,
    top_n: int = 5,
    preferred_profile: str | None = None,
) -> ResolveResult:
    repo_root = Path(repo_root)
    context = dict(context or {})
    registry = load_registry(repo_root)
    skills = registry_skills(registry)

    intent = infer_capabilities(objective, context)
    ranked = rank_skills(
        skills,
        intent.required_capabilities,
        stacks=intent.stacks,
        security_sensitive=intent.security_sensitive,
        preferred_profile=preferred_profile,
    )
    gaps = find_capability_gaps(intent.required_capabilities, skills)
    recommended = [item.skill_id for item in ranked[:top_n]]

    return ResolveResult(
        intent=intent,
        ranked_skills=ranked,
        capability_gaps=gaps,
        recommended_skill_ids=recommended,
    )


def resolve_to_dict(repo_root: Path, objective: str, context: dict | None = None) -> dict:
    result = resolve_capabilities(repo_root, objective, context)
    return {
        "objective": result.intent.objective,
        "domains_detected": result.intent.domains_detected,
        "security_sensitive": result.intent.security_sensitive,
        "stacks": result.intent.stacks,
        "required_capabilities": result.intent.required_capabilities,
        "capability_gaps": result.capability_gaps,
        "recommended_skill_ids": result.recommended_skill_ids,
        "ranked_skills": [
            {
                "skill_id": item.skill_id,
                "score": item.score,
                "scoring_breakdown": item.scoring_breakdown,
            }
            for item in result.ranked_skills
        ],
    }
