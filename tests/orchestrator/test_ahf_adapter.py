"""AHF-P01 AI Hedge Fund adapter — hermetic unit tests."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from orchestrator.integrations.ai_hedge_fund import (
    AiHedgeFundAdapter,
    LiveExecutionDenied,
    PINNED_SHA,
    adapter_enabled,
)
from orchestrator.integrations.ai_hedge_fund.policy import assert_research_mode
from orchestrator.integrations.ai_hedge_fund.schemas import validate_manifest
from orchestrator.providers.technology_intelligence.file_provider import (
    FileTechnologyIntelligenceProvider,
)

ROOT = Path(__file__).resolve().parents[2]
TI_FIXTURES = (
    ROOT
    / "orchestrator"
    / "providers"
    / "technology_intelligence"
    / "fixtures"
)


class AhfPolicyTests(unittest.TestCase):
    def test_allowed_modes(self) -> None:
        for mode in ("research", "paper", "backtest"):
            self.assertEqual(assert_research_mode(mode), mode)

    def test_denies_live_mode(self) -> None:
        with self.assertRaises(LiveExecutionDenied):
            assert_research_mode("live")

    def test_denies_broker_token_in_extras(self) -> None:
        with self.assertRaises(LiveExecutionDenied):
            assert_research_mode("paper", extras={"execution": "broker"})

    def test_denies_wallet_token(self) -> None:
        with self.assertRaises(LiveExecutionDenied):
            assert_research_mode("research", extras={"target": "wallet"})


class AhfAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = AiHedgeFundAdapter(enabled=True, require_enabled=True)

    def test_disabled_by_default(self) -> None:
        prev = os.environ.pop("COMPASS_AHF_ADAPTER_ENABLED", None)
        try:
            self.assertFalse(adapter_enabled())
            disabled = AiHedgeFundAdapter(enabled=False)
            with self.assertRaises(LiveExecutionDenied):
                disabled.run_backtest()
        finally:
            if prev is not None:
                os.environ["COMPASS_AHF_ADAPTER_ENABLED"] = prev

    def test_backtest_manifest_invariants(self) -> None:
        result = self.adapter.run_backtest()
        self.assertEqual(result["pinned_sha"], PINNED_SHA)
        self.assertFalse(result["approved_for_execution"])
        self.assertFalse(result["authority_mutation"])
        self.assertEqual(result["operation"], "run_backtest")
        self.assertTrue(result["results"]["fixture"])
        self.assertEqual(validate_manifest(result), [])

    def test_strategy_agents_fixture_only(self) -> None:
        result = self.adapter.run_strategy_agents()
        self.assertFalse(result["results"]["local_invoke"])
        self.assertTrue(result["results"]["opinions"])

    def test_paper_and_ledger(self) -> None:
        paper = self.adapter.run_paper_session()
        ledger = self.adapter.get_decision_ledger()
        self.assertIn("fills", paper["results"])
        self.assertTrue(ledger["results"]["entries"])

    def test_compare_runs(self) -> None:
        left = self.adapter.run_backtest(strategy="baseline")
        # Mutate a copy-like payload for delta by crafting right metrics via second call
        right = self.adapter.run_backtest(strategy="baseline")
        # Force a synthetic improvement for deterministic assertion
        right = dict(right)
        right["results"] = {
            "strategy": "candidate",
            "metrics": {
                "cumulative_return": 0.05,
                "max_drawdown": -0.01,
                "sharpe": 1.2,
                "hit_rate": 0.56,
                "turnover": 0.2,
            },
            "fixture": True,
        }
        compared = self.adapter.compare_runs(left, right)
        deltas = compared["results"]["comparison"]["metric_deltas"]
        self.assertGreater(deltas["cumulative_return"], 0)
        self.assertFalse(compared["approved_for_execution"])

    def test_live_denied_through_adapter(self) -> None:
        with self.assertRaises(LiveExecutionDenied):
            self.adapter.run_backtest(mode="live")

    def test_optional_local_path_recorded_not_executed(self) -> None:
        adapter = AiHedgeFundAdapter(
            enabled=True,
            local_path="/tmp/ai-hedge-fund-checkout",
        )
        result = adapter.create_research_run(objective="BTC paper allocation?")
        self.assertEqual(result["local_path"], "/tmp/ai-hedge-fund-checkout")
        self.assertEqual(result["provider"], "fixture")


class AhfTiFixtureTests(unittest.TestCase):
    def test_file_ti_includes_ahf_candidate(self) -> None:
        provider = FileTechnologyIntelligenceProvider(fixtures_dir=TI_FIXTURES)
        candidates = provider.discover_candidates("paper trading research", {})
        ahf = [c for c in candidates if "ai-hedge-fund" in c.id or "ai-hedge-fund" in c.source_path]
        self.assertTrue(ahf, "expected AHF TI fixture candidate")
        doc = ahf[0].to_dict()
        self.assertFalse(doc["approved_for_execution"])
        self.assertIn("historical-backtesting", doc["capabilities_provided"])


if __name__ == "__main__":
    unittest.main()
