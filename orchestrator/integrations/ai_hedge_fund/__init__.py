"""NorthStar read-only adapter for virattt/ai-hedge-fund (AHF-P01).

Authority: research / paper / backtest only. Never grants
``approved_for_execution``. Live broker / wallet / signing paths are denied.
"""

from __future__ import annotations

from orchestrator.integrations.ai_hedge_fund.adapter import (
    AiHedgeFundAdapter,
    adapter_enabled,
    get_adapter,
)
from orchestrator.integrations.ai_hedge_fund.onchain_analyst import (
    OnChainAnalyst,
    compose_with_ahf,
    write_analysis_evidence,
)
from orchestrator.integrations.ai_hedge_fund.experiment import (
    evaluate_acceptance,
    experiment_enabled,
    run_portfolio_experiment,
    write_experiment_evidence,
)
from orchestrator.integrations.ai_hedge_fund.behavioral import (
    assess_execution_readiness,
    coupling_enabled,
    ingest_experiment_outcome,
    run_behavioral_coupling,
)
from orchestrator.integrations.ai_hedge_fund.policy import (
    ALLOWED_MODES,
    LiveExecutionDenied,
    assert_research_mode,
)
from orchestrator.integrations.ai_hedge_fund.schemas import (
    PINNED_REPO,
    PINNED_SHA,
    RunManifest,
)
from orchestrator.integrations.ai_hedge_fund.shadow import (
    maybe_run_ahf_signal_shadow,
    maybe_run_ahf_strategy_shadow,
)

__all__ = [
    "ALLOWED_MODES",
    "AiHedgeFundAdapter",
    "LiveExecutionDenied",
    "OnChainAnalyst",
    "PINNED_REPO",
    "PINNED_SHA",
    "RunManifest",
    "adapter_enabled",
    "assess_execution_readiness",
    "assert_research_mode",
    "coupling_enabled",
    "compose_with_ahf",
    "evaluate_acceptance",
    "experiment_enabled",
    "get_adapter",
    "ingest_experiment_outcome",
    "run_behavioral_coupling",
    "run_portfolio_experiment",
    "write_experiment_evidence",
    "maybe_run_ahf_signal_shadow",
    "maybe_run_ahf_strategy_shadow",
    "write_analysis_evidence",
]
