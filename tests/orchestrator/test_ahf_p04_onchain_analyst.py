"""AHF-P04 On-Chain Analyst hermetic tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from orchestrator.integrations.ai_hedge_fund import get_adapter
from orchestrator.integrations.ai_hedge_fund.onchain_analyst import (
    OnChainAnalyst,
    compose_with_ahf,
    write_analysis_evidence,
)
from orchestrator.integrations.ai_hedge_fund.shadow import maybe_run_ahf_signal_shadow


class OnChainAnalystTests(unittest.TestCase):
    def test_fixture_bullish_net_outflow(self) -> None:
        analysis = OnChainAnalyst().analyze()
        self.assertEqual(analysis.signal, "bullish")
        self.assertFalse(analysis.approved_for_execution)
        self.assertTrue(analysis.evidence)
        self.assertLess(analysis.netflow_btc or 0.0, 0)

    def test_uncertain_without_flow(self) -> None:
        analysis = OnChainAnalyst().analyze({"transaction_count": 1})
        self.assertEqual(analysis.signal, "uncertain")

    def test_compose_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            analysis = OnChainAnalyst().analyze()
            adapter = get_adapter(enabled=True)
            research = adapter.create_research_run(objective="BTC paper allocation")
            prev_shadow = os.environ.get("COMPASS_DECISION_AHF_SHADOW")
            prev_prov = os.environ.get("COMPASS_DECISION_PROVIDER")
            os.environ["COMPASS_DECISION_AHF_SHADOW"] = "1"
            os.environ["COMPASS_DECISION_PROVIDER"] = "file"
            try:
                shadow = maybe_run_ahf_signal_shadow(
                    root,
                    asset="BTC",
                    state=analysis.to_jev_state(),
                    adapter_manifest=research,
                )
                composed = compose_with_ahf(
                    analysis, research_manifest=research, jev_shadow_ref=shadow
                )
                self.assertFalse(composed["approved_for_execution"])
                ref = write_analysis_evidence(root, analysis, composed=composed)
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
