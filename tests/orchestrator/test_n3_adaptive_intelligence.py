"""N3 Adaptive Intelligence Validation — hermetic tests."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.adaptive.enabled import adaptive_intel_enabled, require_adaptive_intel_gate
from orchestrator.adaptive.service import AdaptiveServiceError, run_scorecard
from orchestrator.schemas.validate import ValidationError, validate_document


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_ADAPTIVE_INTEL_ENABLED", None)
            self.assertFalse(adaptive_intel_enabled())
            with self.assertRaises(PermissionError):
                require_adaptive_intel_gate()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_ADAPTIVE_INTEL_ENABLED": "1"}):
            self.assertTrue(adaptive_intel_enabled())


class SchemaTests(unittest.TestCase):
    def test_locks(self) -> None:
        doc = {
            "schema_version": "1",
            "report_id": "adaptive-test",
            "created_at": "2026-10-22T00:00:00Z",
            "phase": "baseline",
            "northstar_version": "1.73.0",
            "metrics": {
                name: {
                    "name": name,
                    "value": 1.0,
                    "unit": "rate",
                    "status": "pass",
                    "summary": "ok",
                    "details": {},
                }
                for name in (
                    "project_state_accuracy",
                    "difficulty_calibration",
                    "routing_effectiveness",
                    "skill_reuse",
                    "review_precision",
                    "context_efficiency",
                    "training_effectiveness",
                )
            },
            "level3_recommendation": "defer",
            "level3_rationale": "test",
            "approved_for_execution": False,
            "authority_mutation": False,
            "auto_applied": False,
        }
        validate_document(doc, "adaptive-intelligence-scorecard.schema.json")
        bad = dict(doc)
        bad["auto_applied"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "adaptive-intelligence-scorecard.schema.json")


class ScorecardTests(unittest.TestCase):
    def test_compare_scorecard(self) -> None:
        env = {
            "COMPASS_ADAPTIVE_INTEL_ENABLED": "1",
            "COMPASS_BRAIN_ENABLED": "1",
            "COMPASS_ASSESS_ENABLED": "1",
            "COMPASS_ROUTE_ENABLED": "1",
            "COMPASS_CONTROL_ROOT": str(ROOT),
        }
        with mock.patch.dict(os.environ, env, clear=False):
            report = run_scorecard(ROOT, phase="compare", persist=True)
        self.assertEqual(report["phase"], "compare")
        self.assertFalse(report["auto_applied"])
        self.assertFalse(report["authority_mutation"])
        self.assertIn(report["level3_recommendation"], {"defer", "consider"})
        self.assertIn("deltas", report)
        self.assertGreaterEqual(
            report["metrics"]["skill_reuse"]["details"]["experience_skill_count"],
            1,
        )
        validate_document(report, "adaptive-intelligence-scorecard.schema.json")

    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_ADAPTIVE_INTEL_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-adaptive-intelligence.sh"),
                "scorecard",
                "--phase",
                "baseline",
                "--repo-root",
                str(ROOT),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_ADAPTIVE_INTEL_ENABLED", proc.stderr)


if __name__ == "__main__":
    unittest.main()
