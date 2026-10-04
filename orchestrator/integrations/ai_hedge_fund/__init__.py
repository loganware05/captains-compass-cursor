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

__all__ = [
    "ALLOWED_MODES",
    "AiHedgeFundAdapter",
    "LiveExecutionDenied",
    "PINNED_REPO",
    "PINNED_SHA",
    "RunManifest",
    "adapter_enabled",
    "assert_research_mode",
    "get_adapter",
]
