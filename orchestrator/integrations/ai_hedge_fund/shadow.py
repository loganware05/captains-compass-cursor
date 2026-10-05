"""AHF-P02 shadow orchestration — DecisionProvider beside AHF adapter (observe-only)."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from orchestrator.providers.decision.file_provider import (
    decision_ahf_shadow_enabled,
    select_decision_provider,
)
from orchestrator.providers.decision.state import assert_state_safe, redact_text
from orchestrator.providers.decision.types import (
    AhfSignalRequest,
    AhfSignalResult,
    AhfStrategyRequest,
    AhfStrategyResult,
    EligibleAhfAgentSummary,
)

EVIDENCE_ROOT_REL = Path(".agent") / "evidence" / "ahf-p02-jev-shadow"

DEFAULT_AHF_AGENTS: tuple[EligibleAhfAgentSummary, ...] = (
    EligibleAhfAgentSummary(
        agent_id="warren_buffett",
        name="Warren Buffett",
        description="Value / quality investor agent",
    ),
    EligibleAhfAgentSummary(
        agent_id="cathie_wood",
        name="Cathie Wood",
        description="Growth / innovation investor agent",
    ),
    EligibleAhfAgentSummary(
        agent_id="risk",
        name="Risk Agent",
        description="Portfolio risk and exposure specialist",
    ),
)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _roster_hash(agents: Sequence[EligibleAhfAgentSummary]) -> str:
    payload = json.dumps(
        [a.to_dict() for a in agents], sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _state_hash(state: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(state), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def write_ahf_shadow_evidence(
    repo_root: Path,
    *,
    kind: str,
    baseline: dict[str, Any],
    provider_result: dict[str, Any],
    plan_id: str | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    run_id = f"{_utc_stamp()}-{uuid.uuid4().hex[:8]}"
    rel_dir = EVIDENCE_ROOT_REL / "shadow" / run_id
    abs_dir = repo_root / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "northstar.decision_ahf_shadow.v1",
        "kind": kind,
        "run_id": run_id,
        "plan_id_ref": plan_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "applied": False,
        "baseline": baseline,
        "provider_result": provider_result,
        "env": {
            "COMPASS_DECISION_PROVIDER": os.environ.get("COMPASS_DECISION_PROVIDER", "stub"),
            "COMPASS_DECISION_AHF_SHADOW": os.environ.get("COMPASS_DECISION_AHF_SHADOW", ""),
            "COMPASS_JEV_MODEL_ID": os.environ.get("COMPASS_JEV_MODEL_ID", ""),
        },
    }
    path = abs_dir / f"decision-ahf-{kind}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {
        "run_id": run_id,
        "evidence_path": str(rel_dir / f"decision-ahf-{kind}.json"),
        "applied": False,
        "kind": kind,
    }


def agents_from_adapter_opinions(
    opinions: Sequence[Mapping[str, Any]] | None,
) -> list[EligibleAhfAgentSummary]:
    if not opinions:
        return list(DEFAULT_AHF_AGENTS)
    out: list[EligibleAhfAgentSummary] = []
    for item in opinions:
        agent_id = str(item.get("agent") or item.get("agent_id") or "").strip()
        if not agent_id:
            continue
        out.append(
            EligibleAhfAgentSummary(
                agent_id=agent_id,
                name=redact_text(str(item.get("name") or agent_id))[:120],
                description=redact_text(str(item.get("description") or ""))[:400],
                baseline_signal=redact_text(str(item.get("signal") or ""))[:40],
            )
        )
    return out or list(DEFAULT_AHF_AGENTS)


def maybe_run_ahf_strategy_shadow(
    repo_root: Path,
    *,
    objective: str,
    mandate: str = "paper",
    adapter_manifest: Mapping[str, Any] | None = None,
    eligible_agents: Sequence[EligibleAhfAgentSummary] | None = None,
    plan_id: str | None = "ahf-p02-jev-shadow",
) -> dict[str, Any] | None:
    """Observe-only strategy selection beside an AHF adapter run."""
    if not decision_ahf_shadow_enabled():
        return None
    agents = list(eligible_agents) if eligible_agents is not None else list(DEFAULT_AHF_AGENTS)
    roster = _roster_hash(agents)
    market = {}
    if adapter_manifest and isinstance(adapter_manifest.get("results"), dict):
        market = dict(adapter_manifest.get("results") or {})
    request = AhfStrategyRequest(
        objective=redact_text(objective)[:500],
        mandate=redact_text(mandate)[:120],
        eligible_agents=agents,
        roster_hash=roster,
        market_snapshot={
            "fixture": bool(market.get("fixture")),
            "selected_agents_baseline": list(
                (adapter_manifest or {}).get("selected_agents") or []
            )[:12],
        },
    )
    assert_state_safe(request.to_dict())
    provider = select_decision_provider(repo_root)
    result: AhfStrategyResult = provider.suggest_ahf_strategies(request)
    baseline = {
        "selected_agents": list((adapter_manifest or {}).get("selected_agents") or []),
        "adapter_run_id": (adapter_manifest or {}).get("run_id"),
        "adapter_operation": (adapter_manifest or {}).get("operation"),
    }
    ref = write_ahf_shadow_evidence(
        repo_root,
        kind="strategy",
        baseline=baseline,
        provider_result=result.to_dict(applied=False),
        plan_id=plan_id,
    )
    # Never mutate adapter selection — shadow only.
    ref["suggested_agent_id"] = result.suggested_agent_id
    ref["abstain"] = result.abstain
    return ref


def maybe_run_ahf_signal_shadow(
    repo_root: Path,
    *,
    asset: str,
    state: Mapping[str, Any],
    adapter_manifest: Mapping[str, Any] | None = None,
    plan_id: str | None = "ahf-p02-jev-shadow",
) -> dict[str, Any] | None:
    """Observe-only signal triage beside normalized market/on-chain state."""
    if not decision_ahf_shadow_enabled():
        return None
    compact = {
        key: state[key]
        for key in (
            "price_change_24h",
            "exchange_netflow",
            "whale_balance_change",
            "stablecoin_supply_change_7d",
            "agent_votes",
        )
        if key in state
    }
    request = AhfSignalRequest(
        asset=redact_text(asset)[:32],
        state=compact,
        state_hash=_state_hash(compact),
    )
    assert_state_safe(request.to_dict())
    provider = select_decision_provider(repo_root)
    result: AhfSignalResult = provider.triage_ahf_signal(request)
    baseline = {
        "adapter_run_id": (adapter_manifest or {}).get("run_id"),
        "adapter_operation": (adapter_manifest or {}).get("operation"),
        "state_keys": sorted(compact.keys()),
    }
    ref = write_ahf_shadow_evidence(
        repo_root,
        kind="signal",
        baseline=baseline,
        provider_result=result.to_dict(applied=False),
        plan_id=plan_id,
    )
    ref["signal"] = result.signal
    ref["escalate"] = result.escalate
    ref["abstain"] = result.abstain
    return ref
