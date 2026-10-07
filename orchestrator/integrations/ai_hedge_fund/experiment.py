"""AHF-P05 portfolio experimentation — multi-arm backtest compare (observe-only).

Arms:
  A) baseline — no on-chain
  B) onchain — OnChainAnalyst + backtest
  C) jev_onchain — on-chain + optional Jev strategy/signal shadow + backtest

Always ``approved_for_execution: false``. Paper sessions require acceptance.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from orchestrator.integrations.ai_hedge_fund.adapter import AiHedgeFundAdapter, get_adapter
from orchestrator.integrations.ai_hedge_fund.evaluators import compare_runs
from orchestrator.integrations.ai_hedge_fund.onchain_analyst import (
    OnChainAnalyst,
    write_analysis_evidence,
)
from orchestrator.integrations.ai_hedge_fund.shadow import (
    maybe_run_ahf_signal_shadow,
    maybe_run_ahf_strategy_shadow,
)

DEFAULT_ARMS_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "experiment_arms.json"
)
EVIDENCE_ROOT_REL = Path(".agent") / "evidence" / "ahf-p05-portfolio-experiment"
ARM_ORDER = ("baseline", "onchain", "jev_onchain")


def experiment_enabled() -> bool:
    raw = os.environ.get("COMPASS_AHF_EXPERIMENT_ENABLED", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_experiment_config(path: Path | str | None = None) -> dict[str, Any]:
    path = Path(path) if path else DEFAULT_ARMS_FIXTURE
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or "arms" not in payload:
        raise ValueError("experiment arms fixture must contain an arms object")
    return payload


def _arm_manifest(
    adapter: AiHedgeFundAdapter,
    *,
    arm: Mapping[str, Any],
    parent_run_id: str | None,
) -> dict[str, Any]:
    """Run fixture backtest then overlay arm-specific metrics/agents."""
    manifest = adapter.run_backtest(strategy=str(arm["id"]))
    results = dict(manifest.get("results") or {})
    results["strategy"] = arm["id"]
    results["arm"] = arm["id"]
    results["arm_label"] = arm.get("label")
    results["metrics"] = dict(arm.get("metrics") or {})
    results["parent_run_id"] = parent_run_id
    results["fixture"] = True
    results["uses_onchain"] = bool(arm.get("uses_onchain"))
    results["uses_jev_shadow"] = bool(arm.get("uses_jev_shadow"))
    manifest["results"] = results
    manifest["selected_agents"] = list(arm.get("agents") or [])
    return manifest


def compare_arm_metrics(arms: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Pairwise deltas vs baseline for investment + orchestration metrics."""
    baseline = arms.get("baseline") or {}
    base_metrics = dict((baseline.get("results") or {}).get("metrics") or {})
    pairwise: dict[str, Any] = {}
    for arm_id, manifest in arms.items():
        if arm_id == "baseline":
            continue
        cmp = compare_runs(dict(baseline), dict(manifest))
        pairwise[arm_id] = cmp
    # Rank by cumulative_return then sharpe
    ranking = sorted(
        arms.keys(),
        key=lambda aid: (
            float(((arms[aid].get("results") or {}).get("metrics") or {}).get("cumulative_return") or 0.0),
            float(((arms[aid].get("results") or {}).get("metrics") or {}).get("sharpe") or 0.0),
        ),
        reverse=True,
    )
    return {
        "baseline_metrics": base_metrics,
        "pairwise_vs_baseline": pairwise,
        "ranking_by_return_then_sharpe": ranking,
    }


def evaluate_acceptance(
    arms: Mapping[str, Mapping[str, Any]],
    acceptance: Mapping[str, Any],
) -> dict[str, Any]:
    """Deterministic gate: preferred winning arm must beat baseline on key deltas."""
    comparison = compare_arm_metrics(arms)
    preference = list(acceptance.get("winning_arm_preference") or ["jev_onchain", "onchain"])
    ranking = list(comparison["ranking_by_return_then_sharpe"])
    winner = next((a for a in preference if a in arms and a != "baseline"), ranking[0] if ranking else None)
    base = comparison["baseline_metrics"]
    win_metrics = dict(((arms.get(winner) or {}).get("results") or {}).get("metrics") or {})
    checks: list[dict[str, Any]] = []

    def _check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    ret_delta = float(win_metrics.get("cumulative_return") or 0.0) - float(
        base.get("cumulative_return") or 0.0
    )
    min_ret = float(acceptance.get("min_cumulative_return_delta_vs_baseline") or 0.0)
    _check(
        "cumulative_return_delta",
        ret_delta >= min_ret,
        f"delta={ret_delta:.6f} min={min_ret}",
    )

    dd_win = float(win_metrics.get("max_drawdown") or 0.0)
    dd_base = float(base.get("max_drawdown") or 0.0)
    dd_slack = float(acceptance.get("max_drawdown_not_worse_than_baseline_by") or 0.0)
    # max_drawdown is negative; "worse" means more negative
    _check(
        "max_drawdown_bound",
        dd_win >= (dd_base - dd_slack),
        f"winner={dd_win} baseline={dd_base} slack={dd_slack}",
    )

    sharpe_delta = float(win_metrics.get("sharpe") or 0.0) - float(base.get("sharpe") or 0.0)
    min_sharpe = float(acceptance.get("min_sharpe_delta_vs_baseline") or 0.0)
    _check(
        "sharpe_delta",
        sharpe_delta >= min_sharpe,
        f"delta={sharpe_delta:.6f} min={min_sharpe}",
    )

    max_to = float(acceptance.get("max_turnover") or 1.0)
    turnover = float(win_metrics.get("turnover") or 0.0)
    _check("turnover_cap", turnover <= max_to, f"turnover={turnover} max={max_to}")

    min_cov = float(acceptance.get("require_evidence_coverage") or 0.0)
    cov = float(win_metrics.get("evidence_coverage") or 0.0)
    _check("evidence_coverage", cov >= min_cov, f"coverage={cov} min={min_cov}")

    passed = all(c["ok"] for c in checks)
    return {
        "passed": passed,
        "winner_arm": winner,
        "checks": checks,
        "comparison": comparison,
        "approved_for_execution": False,
        "paper_eligible": passed,
    }


def write_experiment_evidence(
    repo_root: Path,
    report: Mapping[str, Any],
) -> Path:
    repo_root = Path(repo_root)
    run_id = str(report.get("experiment_id") or f"exp-{uuid.uuid4().hex[:12]}")
    rel = EVIDENCE_ROOT_REL / run_id
    abs_dir = repo_root / rel
    abs_dir.mkdir(parents=True, exist_ok=True)
    path = abs_dir / "experiment.json"
    payload = dict(report)
    payload["approved_for_execution"] = False
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_portfolio_experiment(
    repo_root: Path,
    *,
    objective: str = "BTC paper allocation experiment",
    adapter: AiHedgeFundAdapter | None = None,
    onchain_source: Path | str | Mapping[str, Any] | None = None,
    arms_path: Path | str | None = None,
    require_enabled: bool = True,
    run_paper_if_accepted: bool = False,
) -> dict[str, Any]:
    """Execute the three-arm portfolio experiment (fixture-backed)."""
    if require_enabled and not experiment_enabled():
        raise RuntimeError(
            "AHF portfolio experiment disabled — set COMPASS_AHF_EXPERIMENT_ENABLED=1"
        )

    repo_root = Path(repo_root)
    config = load_experiment_config(arms_path)
    arm_defs = config["arms"]
    acceptance_cfg = dict(config.get("acceptance") or {})

    adapter = adapter or get_adapter(enabled=True)
    research = adapter.create_research_run(objective=objective)
    parent_run_id = research.get("run_id")

    analysis_payload: dict[str, Any] | None = None
    analysis_evidence: str | None = None
    shadow_refs: dict[str, Any] = {}

    # Shared on-chain analysis for arms that need it
    analyst = OnChainAnalyst()
    analysis = analyst.analyze(onchain_source)
    analysis_payload = analysis.to_dict()
    analysis_evidence = str(write_analysis_evidence(repo_root, analysis))

    arm_manifests: dict[str, dict[str, Any]] = {}
    for arm_id in ARM_ORDER:
        arm = arm_defs[arm_id]
        if arm.get("uses_onchain"):
            # provenance only — metrics come from arm fixture
            pass
        if arm.get("uses_jev_shadow"):
            shadow_refs["strategy"] = maybe_run_ahf_strategy_shadow(
                repo_root,
                objective=objective,
                adapter_manifest=research,
                plan_id="ahf-p05-portfolio-experiment",
            )
            shadow_refs["signal"] = maybe_run_ahf_signal_shadow(
                repo_root,
                asset=str(analysis.asset),
                state=analysis.to_jev_state(),
                plan_id="ahf-p05-portfolio-experiment",
            )
        arm_manifests[arm_id] = _arm_manifest(
            adapter, arm=arm, parent_run_id=parent_run_id
        )

    acceptance = evaluate_acceptance(arm_manifests, acceptance_cfg)

    paper: dict[str, Any] | None = None
    paper_blocked_reason: str | None = None
    if run_paper_if_accepted:
        if acceptance.get("paper_eligible"):
            paper = adapter.run_paper_session(
                session_label=f"ahf-p05-{acceptance.get('winner_arm')}"
            )
        else:
            paper_blocked_reason = "acceptance_failed"

    report: dict[str, Any] = {
        "schema": "northstar.ahf_portfolio_experiment.v1",
        "experiment_id": f"exp-{_utc_stamp()}-{uuid.uuid4().hex[:8]}",
        "created_at": _utc_now(),
        "plan_id": "ahf-p05-portfolio-experiment",
        "objective": objective,
        "parent_research_run_id": parent_run_id,
        "arms": {k: v for k, v in arm_manifests.items()},
        "onchain_analysis": analysis_payload,
        "onchain_evidence_path": analysis_evidence,
        "jev_shadow": shadow_refs,
        "acceptance": acceptance,
        "paper_session": paper,
        "paper_blocked_reason": paper_blocked_reason,
        "approved_for_execution": False,
        "authority_mutation": False,
        "provider_note": (
            "Fixture-backed arm metrics; live Jev only when "
            "COMPASS_DECISION_PROVIDER=jev and COMPASS_DECISION_AHF_SHADOW=1"
        ),
    }
    evidence_path = write_experiment_evidence(repo_root, report)
    report["evidence_path"] = str(evidence_path)
    return report
