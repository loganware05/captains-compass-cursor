"""NorthStar agent router (v1) with wakeability-adjusted availability.

OVA-17 learning (NS-SKILL-001): declared registry ``availability`` must not be
treated as dispatch-ready for expired Cursor Cloud Agent pins. Effective
availability is gated by wakeability (registry field and/or live probe).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

ROUTER_VERSION = "northstar.agent_router.v1"

DEFAULT_WEIGHTS: dict[str, float] = {
    "skill_match": 0.3,
    "category_match": 0.2,
    "repository_familiarity": 0.15,
    "historical_success": 0.15,
    "context_continuity": 0.1,
    "availability": 0.1,
}

# Caps applied to declared availability. expired/unreachable fail closed.
WAKEABILITY_AVAILABILITY_CAP: dict[str, float] = {
    "wakeable": 1.0,
    "unknown": 0.25,
    "expired": 0.0,
    "unreachable": 0.0,
}

WakeabilityProbe = Callable[[Mapping[str, Any]], str]


@dataclass(frozen=True)
class RouteObjective:
    title: str
    category: str
    target_repository: str
    required_skills: Sequence[str] = field(default_factory=tuple)
    skill_scope: str = "sandbox"
    context_agent_id: str | None = None


@dataclass(frozen=True)
class AgentScorecard:
    agent_id: str
    eligible: bool
    filter_failures: tuple[str, ...]
    components: dict[str, float] | None
    score: float | None
    declared_availability: float
    effective_availability: float
    wakeability_status: str
    wakeability_source: str


@dataclass(frozen=True)
class RoutingDecision:
    router_version: str
    objective: dict[str, Any]
    weights: dict[str, float]
    agents: list[AgentScorecard]
    eligible_agent_ids: list[str]
    selected_agent_id: str | None
    selection_rationale: str
    dispatch_ready: bool
    notes: str


def normalize_wakeability(raw: str | None) -> str:
    if not raw:
        return "unknown"
    value = str(raw).strip().lower()
    aliases = {
        "wakeable": "wakeable",
        "ok": "wakeable",
        "available": "wakeable",
        "running": "wakeable",
        "active": "wakeable",
        "expired": "expired",
        "inactive": "expired",
        "stopped": "expired",
        "dead": "expired",
        "unreachable": "unreachable",
        "error": "unreachable",
        "unknown": "unknown",
    }
    return aliases.get(value, "unknown")


def resolve_wakeability(
    agent: Mapping[str, Any],
    *,
    probe: WakeabilityProbe | None = None,
) -> tuple[str, str]:
    """Return ``(wakeability_status, source)``.

    Preference: ``wakeability_status`` → ``cloud_status`` → live probe → unknown.
    """

    explicit = agent.get("wakeability_status")
    if explicit:
        return normalize_wakeability(str(explicit)), "registry.wakeability_status"

    cloud = agent.get("cloud_status")
    if cloud:
        return normalize_wakeability(str(cloud)), "registry.cloud_status"

    if probe is not None:
        return normalize_wakeability(probe(agent)), "live_probe"

    return "unknown", "default_unknown"


def effective_availability(declared: float, wakeability_status: str) -> float:
    declared_f = max(0.0, min(1.0, float(declared)))
    status = normalize_wakeability(wakeability_status)
    cap = WAKEABILITY_AVAILABILITY_CAP.get(status, WAKEABILITY_AVAILABILITY_CAP["unknown"])
    return round(declared_f * cap, 4)


def _skill_match(agent: Mapping[str, Any], objective: RouteObjective) -> float:
    required = [s.lower() for s in objective.required_skills]
    if not required:
        return 1.0
    installed = {
        str(s).lower()
        for s in (
            agent.get("skills")
            or agent.get("installed_skills")
            or agent.get("skills_allowlist")
            or []
        )
    }
    if not installed:
        scope = {str(x).lower() for x in (agent.get("skills_installed_scope") or [])}
        if objective.skill_scope.lower() in scope or "any" in scope:
            return 1.0
        return 0.0
    hits = sum(1 for skill in required if skill in installed)
    return hits / len(required)


def _category_match(agent: Mapping[str, Any], objective: RouteObjective) -> float:
    cats = {str(c).lower() for c in (agent.get("categories") or [])}
    if not objective.category:
        return 1.0
    return 1.0 if objective.category.lower() in cats else 0.0


def _repo_familiarity(agent: Mapping[str, Any], objective: RouteObjective) -> float:
    fam = agent.get("repository_familiarity") or {}
    if not isinstance(fam, Mapping):
        return 0.0
    raw = fam.get(objective.target_repository)
    if raw is None:
        return 0.0
    return max(0.0, min(1.0, float(raw)))


def _historical_success(agent: Mapping[str, Any], objective: RouteObjective) -> float:
    success = agent.get("category_success") or {}
    if isinstance(success, Mapping) and objective.category in success:
        return max(0.0, min(1.0, float(success[objective.category])))
    runs = float(agent.get("historical_runs") or 0)
    if runs <= 0:
        return 0.4
    return max(0.0, min(1.0, 0.5 + min(runs, 10) * 0.05))


def _context_continuity(agent: Mapping[str, Any], objective: RouteObjective) -> float:
    if not objective.context_agent_id:
        return 0.5
    return 1.0 if str(agent.get("id")) == objective.context_agent_id else 0.0


def hard_filter_failures(
    agent: Mapping[str, Any],
    objective: RouteObjective,
    *,
    effective_avail: float,
) -> list[str]:
    failures: list[str] = []
    status = str(agent.get("status") or "").lower()
    if status != "active":
        failures.append("status!=active")
    if effective_avail <= 0:
        failures.append("effective_availability<=0")
    allow_raw = (
        agent.get("repository_allowlist")
        or agent.get("repository_allowlist")
        or []
    )
    allow = {str(r) for r in allow_raw}
    if objective.target_repository not in allow and "*" not in allow:
        failures.append("repository_not_allowlisted")
    cats = {str(c).lower() for c in (agent.get("categories") or [])}
    if objective.category and objective.category.lower() not in cats:
        failures.append("category_unsupported")
    scope = {str(s).lower() for s in (agent.get("skills_installed_scope") or [])}
    if scope and objective.skill_scope.lower() not in scope and "any" not in scope:
        failures.append("skill_scope_mismatch")
    if agent.get("autonomy_budget_ok") is False:
        failures.append("autonomy_budget_blocked")
    return failures


def score_agent(
    agent: Mapping[str, Any],
    objective: RouteObjective,
    *,
    weights: Mapping[str, float] | None = None,
    probe: WakeabilityProbe | None = None,
) -> AgentScorecard:
    merged_weights = dict(DEFAULT_WEIGHTS)
    if weights:
        merged_weights.update({k: float(v) for k, v in weights.items()})

    declared = float(agent.get("availability") if agent.get("availability") is not None else 0.0)
    wake_status, wake_source = resolve_wakeability(agent, probe=probe)
    eff = effective_availability(declared, wake_status)
    failures = hard_filter_failures(agent, objective, effective_avail=eff)
    agent_id = str(agent.get("id") or "")

    if failures:
        return AgentScorecard(
            agent_id=agent_id,
            eligible=False,
            filter_failures=tuple(failures),
            components=None,
            score=None,
            declared_availability=declared,
            effective_availability=eff,
            wakeability_status=wake_status,
            wakeability_source=wake_source,
        )

    components = {
        "skill_match": _skill_match(agent, objective),
        "category_match": _category_match(agent, objective),
        "repository_familiarity": _repo_familiarity(agent, objective),
        "historical_success": _historical_success(agent, objective),
        "context_continuity": _context_continuity(agent, objective),
        "availability": eff,
    }
    score = round(sum(components[key] * merged_weights[key] for key in merged_weights), 4)
    return AgentScorecard(
        agent_id=agent_id,
        eligible=True,
        filter_failures=(),
        components=components,
        score=score,
        declared_availability=declared,
        effective_availability=eff,
        wakeability_status=wake_status,
        wakeability_source=wake_source,
    )


def route_agents(
    agents: Sequence[Mapping[str, Any]],
    objective: RouteObjective,
    *,
    weights: Mapping[str, float] | None = None,
    probe: WakeabilityProbe | None = None,
) -> RoutingDecision:
    cards = [score_agent(agent, objective, weights=weights, probe=probe) for agent in agents]
    eligible = [card for card in cards if card.eligible and card.score is not None]
    eligible.sort(key=lambda card: (-(card.score or 0.0), card.agent_id))
    selected = eligible[0] if eligible else None

    if selected is None:
        rationale = "No eligible agents after hard filters (including wakeability)."
        dispatch_ready = False
        notes = "Fail closed: do not hardcode a dispatcher."
    else:
        rationale = (
            f"Highest AgentScore={selected.score} for {selected.agent_id} "
            f"(wakeability={selected.wakeability_status}/{selected.wakeability_source}, "
            f"effective_availability={selected.effective_availability})."
        )
        dispatch_ready = (
            selected.wakeability_status == "wakeable" and selected.effective_availability > 0
        )
        notes = (
            "Dispatch-ready only when wakeability=wakeable. "
            "Expired/unreachable pins are filtered even if declared availability=1.0. "
            "Captain may authorize First Mate proxy with dual attribution when the "
            "selected agent is not wakeable."
        )

    return RoutingDecision(
        router_version=ROUTER_VERSION,
        objective={
            "title": objective.title,
            "category": objective.category,
            "target_repository": objective.target_repository,
            "required_skills": list(objective.required_skills),
            "skill_scope": objective.skill_scope,
            "context_agent_id": objective.context_agent_id,
        },
        weights=dict(weights or DEFAULT_WEIGHTS),
        agents=cards,
        eligible_agent_ids=[card.agent_id for card in eligible],
        selected_agent_id=selected.agent_id if selected else None,
        selection_rationale=rationale,
        dispatch_ready=dispatch_ready,
        notes=notes,
    )


def decision_to_dict(decision: RoutingDecision) -> dict[str, Any]:
    return {
        "router_version": decision.router_version,
        "objective": decision.objective,
        "weights": decision.weights,
        "agents": [
            {
                "agent_id": card.agent_id,
                "eligible": card.eligible,
                "filter_failures": list(card.filter_failures),
                "components": card.components,
                "score": card.score,
                "declared_availability": card.declared_availability,
                "effective_availability": card.effective_availability,
                "wakeability_status": card.wakeability_status,
                "wakeability_source": card.wakeability_source,
            }
            for card in decision.agents
        ],
        "eligible_agent_ids": decision.eligible_agent_ids,
        "selected_agent_id": decision.selected_agent_id,
        "selection_rationale": decision.selection_rationale,
        "dispatch_ready": decision.dispatch_ready,
        "notes": decision.notes,
    }


def load_registry(
    payload: Mapping[str, Any] | Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(payload, Mapping):
        agents = payload.get("agents")
        if isinstance(agents, list):
            return [dict(agent) for agent in agents if isinstance(agent, Mapping)]
        raise ValueError("registry payload must contain an agents list")
    return [dict(agent) for agent in payload if isinstance(agent, Mapping)]
