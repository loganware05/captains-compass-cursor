"""AHF-P06 behavioral coupling + execution readiness tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.integrations.ai_hedge_fund.behavioral import (
    assess_execution_readiness,
    coupling_enabled,
    ingest_experiment_outcome,
    run_behavioral_coupling,
)

SAMPLE = (
    Path(__file__).resolve().parents[2]
    / "orchestrator"
    / "integrations"
    / "ai_hedge_fund"
    / "fixtures"
    / "experiment_outcome_sample.json"
)


class CouplingGateTests(unittest.TestCase):
    def test_disabled_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_AHF_BEHAVIOR_COUPLING_ENABLED", None)
            self.assertFalse(coupling_enabled())


class IngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = mock.patch.dict(
            os.environ,
            {"COMPASS_AHF_BEHAVIOR_COUPLING_ENABLED": "1"},
            clear=False,
        )
        self._env.start()

    def tearDown(self) -> None:
        self._env.stop()

    def test_ingest_writes_run_and_experience(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = ingest_experiment_outcome(root, SAMPLE)
            self.assertEqual(result["status"], "ingested")
            self.assertFalse(result["approved_for_execution"])
            self.assertTrue(Path(result["execution_run_path"]).is_file())
            self.assertTrue(Path(result["experience_path"]).is_file())
            run = json.loads(Path(result["execution_run_path"]).read_text(encoding="utf-8"))
            self.assertEqual(run["plan_id"], "ahf-p06-behavioral-coupling")
            self.assertIn("proposal_only", " ".join(run.get("lessons") or []))

    def test_coupling_bundle_and_readiness_deny(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Copy sample into temp so evaluate path is optional
            exp_path = root / "experiment.json"
            exp_path.write_text(SAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
            bundle = run_behavioral_coupling(
                root,
                exp_path,
                run_evaluate=False,
                run_learn=False,
                captain_reported_live_jev=True,
            )
            self.assertFalse(bundle["approved_for_execution"])
            self.assertFalse(bundle["recommend_approved_for_execution"])
            readiness = bundle["readiness"]
            self.assertFalse(readiness["recommend_approved_for_execution"])
            self.assertIn("non_fixture_backtests", readiness["failed_gates"])
            self.assertIn("captain_written_approval", readiness["failed_gates"])
            # Safety gate that must remain true (path still absent)
            live_absent = next(
                c for c in readiness["checks"] if c["gate"] == "live_execution_path_absent"
            )
            self.assertTrue(live_absent["ok"])


class ReadinessTests(unittest.TestCase):
    def test_readiness_never_recommends_true(self) -> None:
        verdict = assess_execution_readiness(
            Path("."),
            SAMPLE,
            captain_reported_live_jev=True,
        )
        self.assertFalse(verdict["recommend_approved_for_execution"])
        self.assertFalse(verdict["approved_for_execution"])
        self.assertEqual(verdict["confidence_band"], "research_operable")


if __name__ == "__main__":
    unittest.main()
