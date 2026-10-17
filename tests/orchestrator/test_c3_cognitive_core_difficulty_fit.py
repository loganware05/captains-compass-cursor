"""C3 Cognitive Core — difficulty / capability-fit assessment tests."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-c3-tests"
BACKTEST = ROOT / "tests" / "fixtures" / "assess-backtest" / "cases.json"

from orchestrator.assess.enabled import assess_enabled, require_assess_enabled
from orchestrator.assess.scoring import WEIGHTS, band_for, combine_difficulty
from orchestrator.assess.service import AssessServiceError, assess_project
from orchestrator.schemas.validate import ValidationError, validate_document


def _mk_fixture_dir(prefix: str) -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(_FIXTURE_ROOT)))


def _seed_mini_repo(repo: Path) -> None:
    (repo / "VERSION").write_text("1.62.0\n", encoding="utf-8")
    for name in (
        "AGENTS.md",
        "PROJECT_CONTEXT.md",
        "DECISIONS.md",
        "PROGRESS.md",
        "TESTING.md",
        "IMPLEMENTATION_PLAN.md",
    ):
        (repo / name).write_text(f"# {name}\n", encoding="utf-8")
    # Point registry compile at control Skills by copying symlink or using control root.
    # Tests call assess_project against ROOT (control) for real Skills.


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_ASSESS_ENABLED", None)
            self.assertFalse(assess_enabled())
            with self.assertRaises(PermissionError):
                require_assess_enabled()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_ASSESS_ENABLED": "1"}):
            self.assertTrue(assess_enabled())


class ScoringTests(unittest.TestCase):
    def test_weights_sum_to_one(self) -> None:
        self.assertAlmostEqual(sum(WEIGHTS.values()), 1.0, places=6)

    def test_bands(self) -> None:
        self.assertEqual(band_for(10), "low")
        self.assertEqual(band_for(40), "moderate")
        self.assertEqual(band_for(60), "high")
        self.assertEqual(band_for(90), "very_high")

    def test_combine(self) -> None:
        factors = {k: 40.0 for k in WEIGHTS}
        self.assertEqual(combine_difficulty(factors), 40.0)


class SchemaTests(unittest.TestCase):
    def test_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "assessment_id": "assess-test",
            "objective": "x",
            "difficulty_score": 12.0,
            "band": "low",
            "confidence": 0.5,
            "factors": {k: 10.0 for k in WEIGHTS},
            "weights": dict(WEIGHTS),
            "citations": [],
            "recommendations": {},
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(doc, "project-difficulty-assessment.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "project-difficulty-assessment.schema.json")
        bad2 = dict(doc)
        bad2["authority_mutation"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad2, "project-difficulty-assessment.schema.json")


class AssessServiceTests(unittest.TestCase):
    def test_gate_required(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_ASSESS_ENABLED", None)
            with self.assertRaises(PermissionError):
                assess_project(ROOT, "anything")

    def test_empty_objective(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_ASSESS_ENABLED": "1"}):
            with self.assertRaises(AssessServiceError):
                assess_project(ROOT, "  ")

    def test_assess_control_repo(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_ASSESS_ENABLED": "1"}):
            doc = assess_project(
                ROOT,
                "Add gated project difficulty assessment with security review",
            )
        validate_document(doc, "project-difficulty-assessment.schema.json")
        self.assertFalse(doc["approved_for_execution"])
        self.assertFalse(doc["authority_mutation"])
        self.assertIn(doc["band"], {"low", "moderate", "high", "very_high"})
        self.assertEqual(doc["weights"], WEIGHTS)
        cite_kinds = {c["kind"] for c in doc["citations"]}
        self.assertTrue(cite_kinds & {"git", "skill", "capability", "task_graph"})
        self.assertGreater(doc["task_count"], 0)

    def test_cli(self) -> None:
        env = os.environ.copy()
        env["COMPASS_ASSESS_ENABLED"] = "1"
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-assess.sh"),
                "project",
                "--objective",
                "Update TESTING.md with assess commands",
                "--repo-root",
                str(ROOT),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("difficulty_score", payload)
        self.assertFalse(payload["authority_mutation"])

    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_ASSESS_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-assess.sh"),
                "project",
                "--objective",
                "x",
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_ASSESS_ENABLED", proc.stderr)


class BacktestTests(unittest.TestCase):
    def test_backtest_bands(self) -> None:
        spec = json.loads(BACKTEST.read_text(encoding="utf-8"))
        cases = spec["cases"]
        self.assertGreaterEqual(len(cases), 5)
        failures: list[str] = []
        with mock.patch.dict(os.environ, {"COMPASS_ASSESS_ENABLED": "1"}):
            for case in cases:
                doc = assess_project(ROOT, case["objective"])
                if doc["band"] not in case["expected_bands"]:
                    failures.append(
                        f"{case['id']}: got {doc['band']} "
                        f"score={doc['difficulty_score']} "
                        f"expected={case['expected_bands']}"
                    )
        self.assertEqual(failures, [], "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
