"""AHF-P02 DecisionProvider shadow — hermetic tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from orchestrator.integrations.ai_hedge_fund import get_adapter
from orchestrator.integrations.ai_hedge_fund.shadow import (
    maybe_run_ahf_signal_shadow,
    maybe_run_ahf_strategy_shadow,
)
from orchestrator.providers.decision.file_provider import (
    FileDecisionProvider,
    decision_ahf_shadow_enabled,
)
from orchestrator.providers.decision.types import (
    AhfSignalRequest,
    AhfStrategyRequest,
    EligibleAhfAgentSummary,
)


class AhfDecisionProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = FileDecisionProvider()
        self.agents = [
            EligibleAhfAgentSummary("warren_buffett", "Warren Buffett", "value"),
            EligibleAhfAgentSummary("cathie_wood", "Cathie Wood", "growth"),
            EligibleAhfAgentSummary("risk", "Risk", "risk"),
        ]

    def test_strategy_fixture(self) -> None:
        result = self.provider.suggest_ahf_strategies(
            AhfStrategyRequest(
                objective="BTC paper allocation research",
                mandate="paper",
                eligible_agents=self.agents,
                roster_hash="abc",
            )
        )
        self.assertFalse(result.abstain)
        self.assertEqual(result.suggested_agent_id, "warren_buffett")
        self.assertFalse(result.to_dict().get("applied"))

    def test_signal_fixture(self) -> None:
        result = self.provider.triage_ahf_signal(
            AhfSignalRequest(
                asset="BTC",
                state={"price_change_24h": 2.8, "exchange_netflow": -1000},
                state_hash="deadbeef",
            )
        )
        self.assertFalse(result.abstain)
        self.assertEqual(result.signal, "bullish")
        self.assertTrue(result.escalate)


class AhfShadowOrchestrationTests(unittest.TestCase):
    def test_shadow_flag_default_off(self) -> None:
        prev = os.environ.pop("COMPASS_DECISION_AHF_SHADOW", None)
        try:
            self.assertFalse(decision_ahf_shadow_enabled())
        finally:
            if prev is not None:
                os.environ["COMPASS_DECISION_AHF_SHADOW"] = prev

    def test_strategy_shadow_writes_evidence_without_mutating_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adapter = get_adapter(enabled=True)
            baseline = adapter.create_research_run(objective="BTC paper allocation")
            baseline_agents = list(baseline["selected_agents"])
            prev_shadow = os.environ.get("COMPASS_DECISION_AHF_SHADOW")
            prev_prov = os.environ.get("COMPASS_DECISION_PROVIDER")
            os.environ["COMPASS_DECISION_AHF_SHADOW"] = "1"
            os.environ["COMPASS_DECISION_PROVIDER"] = "file"
            try:
                ref = maybe_run_ahf_strategy_shadow(
                    root,
                    objective="BTC paper allocation",
                    adapter_manifest=baseline,
                )
                self.assertIsNotNone(ref)
                assert ref is not None
                self.assertFalse(ref["applied"])
                evidence = root / ref["evidence_path"]
                self.assertTrue(evidence.is_file())
                # Adapter selection unchanged
                again = adapter.create_research_run(objective="BTC paper allocation")
                self.assertEqual(again["selected_agents"], baseline_agents)
            finally:
                if prev_shadow is None:
                    os.environ.pop("COMPASS_DECISION_AHF_SHADOW", None)
                else:
                    os.environ["COMPASS_DECISION_AHF_SHADOW"] = prev_shadow
                if prev_prov is None:
                    os.environ.pop("COMPASS_DECISION_PROVIDER", None)
                else:
                    os.environ["COMPASS_DECISION_PROVIDER"] = prev_prov

    def test_signal_shadow_writes_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prev_shadow = os.environ.get("COMPASS_DECISION_AHF_SHADOW")
            prev_prov = os.environ.get("COMPASS_DECISION_PROVIDER")
            os.environ["COMPASS_DECISION_AHF_SHADOW"] = "1"
            os.environ["COMPASS_DECISION_PROVIDER"] = "file"
            try:
                ref = maybe_run_ahf_signal_shadow(
                    root,
                    asset="BTC",
                    state={
                        "price_change_24h": 2.8,
                        "exchange_netflow": -18420,
                        "agent_votes": {"technical": "bullish"},
                    },
                )
                self.assertIsNotNone(ref)
                assert ref is not None
                self.assertEqual(ref.get("signal"), "bullish")
                self.assertFalse(ref["applied"])
                self.assertTrue((root / ref["evidence_path"]).is_file())
            finally:
                if prev_shadow is None:
                    os.environ.pop("COMPASS_DECISION_AHF_SHADOW", None)
                else:
                    os.environ["COMPASS_DECISION_AHF_SHADOW"] = prev_shadow
                if prev_prov is None:
                    os.environ.pop("COMPASS_DECISION_PROVIDER", None)
                else:
                    os.environ["COMPASS_DECISION_PROVIDER"] = prev_prov


if __name__ == "__main__":
    unittest.main()
