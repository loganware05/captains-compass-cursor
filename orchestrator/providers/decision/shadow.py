"""Shadow-mode compare: DecisionProvider vs deterministic matcher (evidence only)."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from orchestrator.matcher.score import RankedSkill
from orchestrator.providers.decision.file_provider import (
    decision_shadow_enabled,
    select_decision_provider,
)
from orchestrator.providers.decision.state import build_compact_state
from orchestrator.providers.decision.types import SkillSuggestionRequest, SkillSuggestionResult

EVIDENCE_ROOT_REL = Path(".agent") / "evidence" / "m41-jev-decision-service"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _matcher_ids(ranked: Sequence[RankedSkill], *, top_n: int) -> list[str]:
    return [item.skill_id for item in ranked[:top_n]]


def _provider_ids(result: SkillSuggestionResult, *, top_n: int) -> list[str]:
    if result.abstain:
        return []
    if result.suggested_skill_id:
        rest = [r.skill_id for r in result.ranked if r.skill_id != result.suggested_skill_id]
        return [result.suggested_skill_id, *rest][:top_n]
    return [r.skill_id for r in result.ranked[:top_n]]


def disagreement_list(matcher_ids: list[str], provider_ids: list[str]) -> list[dict[str, Any]]:
    """Ordered pairwise disagreements for the compared prefixes."""
    out: list[dict[str, Any]] = []
    width = max(len(matcher_ids), len(provider_ids))
    for idx in range(width):
        left = matcher_ids[idx] if idx < len(matcher_ids) else None
        right = provider_ids[idx] if idx < len(provider_ids) else None
        if left != right:
            out.append({"rank": idx + 1, "matcher": left, "provider": right})
    return out


def write_shadow_evidence(
    repo_root: Path,
    *,
    objective: str,
    matcher_ranking: list[str],
    provider_result: SkillSuggestionResult,
    roster_hash: str,
    provider_ranking: list[str],
    plan_id: str | None = None,
) -> dict[str, Any]:
    """Persist full shadow artifact under `.agent/evidence/` only."""
    repo_root = Path(repo_root)
    run_id = f"{_utc_stamp()}-{uuid.uuid4().hex[:8]}"
    rel_dir = EVIDENCE_ROOT_REL / "shadow" / run_id
    abs_dir = repo_root / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)
    disagreements = disagreement_list(matcher_ranking, provider_ranking)
    payload = {
        "schema": "northstar.decision_shadow.v1",
        "run_id": run_id,
        "plan_id_ref": plan_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "objective": objective,
        "roster_hash": roster_hash,
        "applied": False,
        "matcher_ranking": matcher_ranking,
        "provider_ranking": provider_ranking,
        "disagreements": disagreements,
        "disagreement_count": len(disagreements),
        "provider_result": provider_result.to_dict(),
        "env": {
            "COMPASS_DECISION_PROVIDER": os.environ.get("COMPASS_DECISION_PROVIDER", "stub"),
            "COMPASS_DECISION_SHADOW": os.environ.get("COMPASS_DECISION_SHADOW", ""),
            "COMPASS_JEV_MODEL_ID": os.environ.get("COMPASS_JEV_MODEL_ID", ""),
        },
    }
    # Never embed secrets from env into evidence beyond model id name.
    path = abs_dir / "decision-shadow.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    rel_path = str(rel_dir / "decision-shadow.json")
    return {
        "evidence_id": run_id,
        "evidence_path": rel_path,
        "applied": False,
        "provider": provider_result.provider,
        "model_id": provider_result.model_id,
        "abstain": provider_result.abstain,
        "disagreement_count": len(disagreements),
        "suggested_skill_id": provider_result.suggested_skill_id,
    }


def maybe_run_decision_shadow(
    repo_root: Path,
    *,
    objective: str,
    eligible_skills: list[dict[str, Any]],
    matcher_ranked: Sequence[RankedSkill],
    recommended_skill_ids: list[str],
    top_n: int = 5,
    plan_id: str | None = None,
) -> dict[str, Any] | None:
    """If shadow enabled and provider ≠ stub, write evidence and return path refs.

    Never mutates ``recommended_skill_ids``.
    """
    if not decision_shadow_enabled():
        return None
    provider = select_decision_provider(repo_root)
    if getattr(provider, "name", "stub") == "stub":
        return None

    objective_clean, summaries, roster_hash, _state = build_compact_state(
        objective, eligible_skills
    )
    request = SkillSuggestionRequest(
        objective=objective_clean,
        eligible_skills=summaries,
        roster_hash=roster_hash,
    )
    result = provider.suggest_skills(request)
    matcher_ids = list(recommended_skill_ids) or _matcher_ids(matcher_ranked, top_n=top_n)
    provider_ids = _provider_ids(result, top_n=top_n)
    return write_shadow_evidence(
        repo_root,
        objective=objective_clean,
        matcher_ranking=matcher_ids,
        provider_result=result,
        roster_hash=roster_hash,
        provider_ranking=provider_ids,
        plan_id=plan_id,
    )
