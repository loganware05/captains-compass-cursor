"""AHF-P05 portfolio experimentation harness tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.integrations.ai_hedge_fund.adapter import AiHedgeFundAdapter
from orchestrator.integrations.ai_hedge_fund.experiment import (
    evaluate_acceptance,
    experiment_enabled,
    load_experiment_config,
    run_portfolio_experiment,
)


class ExperimentGateTests(unittest.TestCase):
    def test_disabled_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_AHF_EXPERIMENT_ENABLED", None)
            self.assertFalse(experiment_enabled())

    def test_enabled_flag(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_AHF_EXPERIMENT_ENABLED": "1"}):
            self.assertTrue(experiment_enabled())


class ExperimentRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = mock.patch.dict(
            os.environ,
            {
                "COMPASS_AHF_ADAPTER_ENABLED": "1",
                "COMPASS_AHF_EXPERIMENT_ENABLED": "1",
                "COMPASS_DECISION_PROVIDER": "file",
                "COMPASS_DECISION_AHF_SHADOW": "1",
            },
            clear=False,
        )
        self._env.start()

    def tearDown(self) -> None:
        self._env.stop()

    def test_three_arms_and_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = run_portfolio_experiment(
                root,
                objective="AHF-P05 unit test",
                run_paper_if_accepted=True,
            )
            self.assertFalse(report["approved_for_execution"])
            self.assertIn("baseline", report["arms"])
            self.assertIn("onchain", report["arms"])
            self.assertIn("jev_onchain", report["arms"])
            self.assertTrue(report["acceptance"]["passed"])
            self.assertEqual(report["acceptance"]["winner_arm"], "jev_onchain")
            self.assertIsNotNone(report["paper_session"])
            self.assertIsNone(report["paper_blocked_reason"])
            evidence = Path(report["evidence_path"])
            self.assertTrue(evidence.is_file())
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            self.assertFalse(payload["approved_for_execution"])
            # Jev shadow attempted under arm C
            self.assertIn("strategy", report["jev_shadow"])
            self.assertIn("signal", report["jev_shadow"])

    def test_paper_blocked_when_acceptance_fails(self) -> None:
        cfg = load_experiment_config()
        # Force impossible return delta
        cfg["acceptance"]["min_cumulative_return_delta_vs_baseline"] = 10.0
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            arms_path = root / "arms.json"
            arms_path.write_text(json.dumps(cfg), encoding="utf-8")
            report = run_portfolio_experiment(
                root,
                arms_path=arms_path,
                run_paper_if_accepted=True,
            )
            self.assertFalse(report["acceptance"]["passed"])
            self.assertIsNone(report["paper_session"])
            self.assertEqual(report["paper_blocked_reason"], "acceptance_failed")

    def test_require_enabled_raises(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_AHF_EXPERIMENT_ENABLED": "0"}):
            with self.assertRaises(RuntimeError):
                run_portfolio_experiment(Path("."), require_enabled=True)


class AcceptanceUnitTests(unittest.TestCase):
    def test_evaluate_acceptance_from_config(self) -> None:
        cfg = load_experiment_config()
        adapter = AiHedgeFundAdapter(enabled=True, require_enabled=False)
        # Build minimal arm manifests
        arms = {}
        for arm_id, arm in cfg["arms"].items():
            m = adapter.run_backtest(strategy=arm_id)
            m["results"]["metrics"] = dict(arm["metrics"])
            arms[arm_id] = m
        result = evaluate_acceptance(arms, cfg["acceptance"])
        self.assertTrue(result["passed"])
        self.assertEqual(result["winner_arm"], "jev_onchain")
        self.assertFalse(result["approved_for_execution"])


if __name__ == "__main__":
    unittest.main()
