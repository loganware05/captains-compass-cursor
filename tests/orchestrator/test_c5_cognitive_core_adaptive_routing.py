"""C5 Cognitive Core — Adaptive routing tests."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.route.enabled import require_route_enabled, route_enabled
from orchestrator.route.scoring import select_adapter_class
from orchestrator.route.service import RouteServiceError, model_evaluate, model_route
from orchestrator.schemas.validate import ValidationError, validate_document


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_ROUTE_ENABLED", None)
            self.assertFalse(route_enabled())
            with self.assertRaises(PermissionError):
                require_route_enabled()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_ROUTE_ENABLED": "1"}):
            self.assertTrue(route_enabled())


class ScoringTests(unittest.TestCase):
    def test_local_for_low(self) -> None:
        cls, reasons = select_adapter_class(
            difficulty_band="low",
            difficulty_score=10,
            security_sensitive=False,
            freshness="fresh",
            gap_count=0,
            objective="Update README typo",
        )
        self.assertEqual(cls, "local")
        self.assertTrue(reasons)

    def test_premium_for_security(self) -> None:
        cls, _ = select_adapter_class(
            difficulty_band="low",
            difficulty_score=5,
            security_sensitive=True,
            freshness="fresh",
            gap_count=0,
            objective="Add feature",
        )
        self.assertEqual(cls, "premium")

    def test_stale_bumps(self) -> None:
        cls, reasons = select_adapter_class(
            difficulty_band="low",
            difficulty_score=8,
            security_sensitive=False,
            freshness="stale",
            gap_count=0,
            objective="Small docs fix",
        )
        self.assertEqual(cls, "hosted")
        self.assertTrue(any("bump" in r for r in reasons))


class SchemaTests(unittest.TestCase):
    def test_proposal_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "proposal_id": "route-test",
            "objective": "x",
            "adapter_class": "local",
            "profile_id": "fast-iter",
            "rationale": ["t"],
            "expected_budget": {},
            "fallbacks": [],
            "citations": [],
            "auto_switched": False,
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": "2026-10-17T00:00:00Z",
        }
        validate_document(doc, "model-route-proposal.schema.json")
        bad = dict(doc)
        bad["auto_switched"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "model-route-proposal.schema.json")


class ServiceTests(unittest.TestCase):
    def test_route_and_evaluate(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"COMPASS_ROUTE_ENABLED": "1", "COMPASS_ASSESS_ENABLED": "1"},
        ):
            proposal = model_route(
                ROOT, "Add gated auth and secrets handling for deploy credentials"
            )
            self.assertEqual(proposal["adapter_class"], "premium")
            self.assertFalse(proposal["approved_for_execution"])
            self.assertFalse(proposal["authority_mutation"])
            self.assertFalse(proposal["auto_switched"])
            self.assertTrue(proposal["assessment_id"])
            self.assertEqual(proposal["profile_id"], "reasoning-strong")

            report = model_evaluate(ROOT)
            self.assertGreaterEqual(report["cases_evaluated"], 3)
            self.assertEqual(report["recommended_adapter_class"], "local")
            self.assertFalse(report["authority_mutation"])
            self.assertEqual(report["rankings"][0]["rank"], 1)

    def test_empty_objective(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_ROUTE_ENABLED": "1"}):
            with self.assertRaises(RouteServiceError):
                model_route(ROOT, "  ")


class CliTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_ROUTE_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-model-route.sh"),
                "evaluate",
                "--repo-root",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_ROUTE_ENABLED", proc.stderr)

    def test_cli_smoke(self) -> None:
        env = os.environ.copy()
        env["COMPASS_ROUTE_ENABLED"] = "1"
        env["COMPASS_ASSESS_ENABLED"] = "1"
        route = subprocess.run(
            [
                str(ROOT / "scripts" / "northstar"),
                "model",
                "route",
                "--objective",
                "Fix a typo in TESTING.md",
                "--repo",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(route.returncode, 0, route.stderr)
        payload = json.loads(route.stdout)
        self.assertIn(payload["adapter_class"], {"local", "hosted", "premium"})
        self.assertFalse(payload["auto_switched"])

        evaluate = subprocess.run(
            [
                str(ROOT / "scripts" / "northstar"),
                "model",
                "evaluate",
                "--repo",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(evaluate.returncode, 0, evaluate.stderr)
        report = json.loads(evaluate.stdout)
        self.assertFalse(report["approved_for_execution"])


if __name__ == "__main__":
    unittest.main()
