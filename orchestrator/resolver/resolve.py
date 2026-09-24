"""End-to-end capability resolution: intent inference + Skill ranking."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from orchestrator.intent.infer_capabilities import IntentResult, infer_capabilities
from orchestrator.matcher.score import RankedSkill, find_capability_gaps, rank_skills
from orchestrator.registry.load import load_registry, registry_skills


@dataclass
class ResolveResult:
    intent: IntentResult
    ranked_skills: list[RankedSkill]
    capability_gaps: list[str]
    recommended_skill_ids: list[str] = field(default_factory=list)
    decision_shadow: dict[str, Any] | None = None


def resolve_capabilities(
    repo_root: Path,
    objective: str,
    context: dict | None = None,
    *,
    top_n: int = 5,
    preferred_profile: str | None = None,
    plan_id: str | None = None,
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

    decision_shadow: dict[str, Any] | None = None
    try:
        from orchestrator.providers.decision.shadow import maybe_run_decision_shadow

        skills_by_id = {
            str(skill.get("id") or ""): skill
            for skill in skills
            if isinstance(skill, dict) and skill.get("id")
        }
        eligible_docs = [
            skills_by_id[item.skill_id]
            for item in ranked
            if item.skill_id in skills_by_id
        ]
        decision_shadow = maybe_run_decision_shadow(
            repo_root,
            objective=objective,
            eligible_skills=eligible_docs,
            matcher_ranked=ranked,
            recommended_skill_ids=list(recommended),
            top_n=top_n,
            plan_id=plan_id or context.get("plan_id"),
        )
    except Exception as exc:  # noqa: BLE001 — shadow must never break resolve
        decision_shadow = {
            "applied": False,
            "error": f"decision shadow withheld: {exc}",
            "evidence_path": None,
            "evidence_id": None,
        }

    return ResolveResult(
        intent=intent,
        ranked_skills=ranked,
        capability_gaps=gaps,
        recommended_skill_ids=recommended,
        decision_shadow=decision_shadow,
    )


def resolve_to_dict(repo_root: Path, objective: str, context: dict | None = None) -> dict:
    result = resolve_capabilities(repo_root, objective, context)
    payload = {
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
    if result.decision_shadow is not None:
        # Path/ID reference only — full artifact lives under .agent/evidence/
        payload["decision_shadow"] = {
            "evidence_id": result.decision_shadow.get("evidence_id"),
            "evidence_path": result.decision_shadow.get("evidence_path"),
            "applied": False,
            "provider": result.decision_shadow.get("provider"),
            "model_id": result.decision_shadow.get("model_id"),
            "abstain": result.decision_shadow.get("abstain"),
            "disagreement_count": result.decision_shadow.get("disagreement_count"),
            "suggested_skill_id": result.decision_shadow.get("suggested_skill_id"),
            "error": result.decision_shadow.get("error"),
        }
    return payload
