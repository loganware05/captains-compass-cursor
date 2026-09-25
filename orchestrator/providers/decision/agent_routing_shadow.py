"""Shadow-mode agent routing: DecisionProvider vs hard-filtered router baseline."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from orchestrator.providers.decision.file_provider import (
    decision_agent_routing_shadow_enabled,
    select_decision_provider,
)
from orchestrator.providers.decision.state import assert_state_safe, redact_text
from orchestrator.providers.decision.types import (
    AgentRoutingRequest,
    AgentRoutingResult,
    EligibleAgentSummary,
)
from orchestrator.routing.agent_router import RoutingDecision

EVIDENCE_ROOT_REL = Path(".agent") / "evidence" / "m45-jev-agent-routing"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _summarize_eligible(
    decision: RoutingDecision,
    agents: Sequence[Mapping[str, Any]],
) -> list[EligibleAgentSummary]:
    by_id = {
        str(agent.get("id") or ""): agent
        for agent in agents
        if isinstance(agent, Mapping) and agent.get("id")
    }
    cards = {card.agent_id: card for card in decision.agents}
    out: list[EligibleAgentSummary] = []
    for agent_id in decision.eligible_agent_ids:
        raw = by_id.get(agent_id) or {}
        card = cards.get(agent_id)
        out.append(
            EligibleAgentSummary(
                agent_id=agent_id,
                name=redact_text(str(raw.get("name") or agent_id))[:120],
                categories=tuple(
                    redact_text(str(c))[:80] for c in (raw.get("categories") or [])
                ),
                skill_scopes=tuple(
                    redact_text(str(s))[:80]
                    for s in (raw.get("skills_installed_scope") or [])
                ),
                description=redact_text(str(raw.get("description") or ""))[:400],
                wakeability_status=(card.wakeability_status if card else ""),
                effective_availability=(card.effective_availability if card else 0.0),
                baseline_score=(card.score if card else None),
            )
        )
    return out


def write_agent_routing_evidence(
    repo_root: Path,
    *,
    roster_hash: str,
    result: AgentRoutingResult,
    baseline: dict[str, Any],
    plan_id: str | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    run_id = f"{_utc_stamp()}-{uuid.uuid4().hex[:8]}"
    rel_dir = EVIDENCE_ROOT_REL / "shadow" / run_id
    abs_dir = repo_root / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "northstar.decision_agent_routing.v1",
        "run_id": run_id,
        "plan_id_ref": plan_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "roster_hash": roster_hash,
        "applied": False,
        "baseline": baseline,
        "provider_result": result.to_dict(applied=False),
        "env": {
            "COMPASS_DECISION_PROVIDER": os.environ.get("COMPASS_DECISION_PROVIDER", "stub"),
            "COMPASS_DECISION_AGENT_ROUTING_SHADOW": os.environ.get(
                "COMPASS_DECISION_AGENT_ROUTING_SHADOW", ""
            ),
            "COMPASS_JEV_MODEL_ID": os.environ.get("COMPASS_JEV_MODEL_ID", ""),
        },
    }
    path = abs_dir / "decision-agent-routing.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    rel_path = str(rel_dir / "decision-agent-routing.json")
    return {
        "evidence_id": run_id,
        "evidence_path": rel_path,
        "applied": False,
        "provider": result.provider,
        "model_id": result.model_id,
        "abstain": result.abstain,
        "suggested_agent_id": result.suggested_agent_id,
        "error": result.error,
    }


def maybe_run_agent_routing_shadow(
    repo_root: Path,
    *,
    decision: RoutingDecision,
    agents: Sequence[Mapping[str, Any]],
    plan_id: str | None = None,
) -> dict[str, Any] | None:
    """If agent-routing shadow enabled and provider ≠ stub, write evidence.

    Never mutates ``selected_agent_id`` / ``dispatch_ready``. Provider roster is
    strictly the hard-filtered eligible set.
    """
    if not decision_agent_routing_shadow_enabled():
        return None
    provider = select_decision_provider(repo_root)
    if getattr(provider, "name", "stub") == "stub":
        return None

    eligible = _summarize_eligible(decision, agents)
    state = {
        "objective_title": redact_text(str(decision.objective.get("title") or "")),
        "eligible_agents": [a.to_dict() for a in eligible],
    }
    assert_state_safe(state)
    roster_hash = hashlib.sha256(
        json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    request = AgentRoutingRequest(
        objective_title=redact_text(str(decision.objective.get("title") or ""))[:500],
        objective_category=redact_text(str(decision.objective.get("category") or ""))[:120],
        target_repository=redact_text(
            str(decision.objective.get("target_repository") or "")
        )[:240],
        required_skills=tuple(
            redact_text(str(s))[:120]
            for s in (decision.objective.get("required_skills") or [])
        ),
        eligible_agents=eligible,
        roster_hash=roster_hash,
    )
    result = provider.suggest_agents(request)
    # Invariant: suggested id must be in eligible roster when not abstaining.
    if (
        not result.abstain
        and result.suggested_agent_id
        and result.suggested_agent_id not in decision.eligible_agent_ids
    ):
        result = AgentRoutingResult(
            provider=result.provider,
            model_id=result.model_id,
            ranked=result.ranked,
            suggested_agent_id=None,
            abstain=True,
            abstain_reason="out_of_roster",
            question_revision=result.question_revision,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            raw_answers=result.raw_answers,
            error=result.error,
        )
    baseline = {
        "eligible_agent_ids": list(decision.eligible_agent_ids),
        "selected_agent_id": decision.selected_agent_id,
        "dispatch_ready": decision.dispatch_ready,
    }
    return write_agent_routing_evidence(
        repo_root,
        roster_hash=roster_hash,
        result=result,
        baseline=baseline,
        plan_id=plan_id,
    )
