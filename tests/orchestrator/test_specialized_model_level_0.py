"""Specialized Model Level 0 local baseline tests."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-specialized-model-tests"
SAMPLE_EXPORT = (
    ROOT / "tests" / "fixtures" / "specialized-model-gold" / "sample-export.json"
)

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.specialized.enabled import (
    require_specialized_model_gate,
    specialized_model_enabled,
)
from orchestrator.specialized.scoring import load_gold_set, score_gold_set
from orchestrator.specialized.service import SpecializedModelServiceError, run_baseline

GATES = {"COMPASS_SPECIALIZED_MODEL_ENABLED": "1"}


def _mk_dir(prefix: str) -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(_FIXTURE_ROOT)))


class GateTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_SPECIALIZED_MODEL_ENABLED", None)
            self.assertFalse(specialized_model_enabled())
            with self.assertRaises(PermissionError):
                require_specialized_model_gate()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, GATES):
            require_specialized_model_gate()


class SchemaTests(unittest.TestCase):
    def _valid_doc(self) -> dict:
        return {
            "schema_version": "1",
            "report_id": "sm0-test",
            "plan_id": "specialized-model-level-0",
            "level": 0,
            "repository_sha": "abc",
            "northstar_version": "1.69.0",
            "gold_set_path": "tests/fixtures/specialized-model-gold/tasks.json",
            "gold_task_count": 24,
            "scores": {
                "retrieval_rate": 1.0,
                "prompt_rate": 1.0,
                "stub_student_rate": 1.0,
                "retrieval_passed": 24,
                "prompt_passed": 24,
                "stub_student_passed": 24,
                "task_total": 24,
            },
            "export_attach": {
                "attached": False,
                "export_id": None,
                "export_path": None,
                "trajectory_count": None,
                "checklist_complete": False,
                "auto_uploaded": False,
            },
            "checklist": {
                "license_reviewed": True,
                "secrets_redacted_ack": True,
                "pii_reviewed": True,
                "provenance_recorded": True,
                "weights_outside_control_repo_ack": True,
            },
            "warnings": [],
            "overall_status": "pass",
            "go_no_go": "go",
            "evidence_path": None,
            "notes": "test",
            "weights_trained": False,
            "auto_uploaded": False,
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": "2026-10-21T00:00:00Z",
        }

    def test_authority_and_weights_locked(self) -> None:
        doc = self._valid_doc()
        validate_document(doc, "specialized-model-baseline-report.schema.json")
        for key in ("weights_trained", "auto_uploaded", "approved_for_execution"):
            bad = dict(doc)
            bad[key] = True
            with self.assertRaises(ValidationError):
                validate_document(bad, "specialized-model-baseline-report.schema.json")


class ScorerTests(unittest.TestCase):
    def test_gold_set_perfect(self) -> None:
        gold = load_gold_set(
            ROOT / "tests" / "fixtures" / "specialized-model-gold" / "tasks.json"
        )
        self.assertEqual(len(gold["tasks"]), 24)
        scores = score_gold_set(gold)
        self.assertEqual(scores["task_total"], 24)
        self.assertEqual(scores["retrieval_passed"], 24)
        self.assertEqual(scores["prompt_passed"], 24)
        self.assertEqual(scores["stub_student_passed"], 24)


class RunnerTests(unittest.TestCase):
    def test_hermetic_baseline(self) -> None:
        evidence = _mk_dir("sm0-ev-")
        try:
            with mock.patch.dict(os.environ, GATES):
                report = run_baseline(
                    ROOT,
                    evidence_dir=evidence,
                    write_evidence=True,
                )
            self.assertIn(report["overall_status"], {"pass", "warn"})
            self.assertEqual(report["level"], 0)
            self.assertFalse(report["weights_trained"])
            self.assertFalse(report["auto_uploaded"])
            self.assertFalse(report["approved_for_execution"])
            self.assertFalse(report["authority_mutation"])
            self.assertEqual(report["gold_task_count"], 24)
            self.assertEqual(report["scores"]["task_total"], 24)
            self.assertFalse(report["export_attach"]["attached"])
            validate_document(report, "specialized-model-baseline-report.schema.json")
            self.assertTrue((evidence / "SUMMARY.md").is_file())
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_attach_export_fixture(self) -> None:
        evidence = _mk_dir("sm0-ex-")
        try:
            with mock.patch.dict(os.environ, GATES):
                report = run_baseline(
                    ROOT,
                    export_path=SAMPLE_EXPORT,
                    evidence_dir=evidence,
                    write_evidence=True,
                )
            self.assertTrue(report["export_attach"]["attached"])
            self.assertTrue(report["export_attach"]["checklist_complete"])
            self.assertEqual(report["export_attach"]["trajectory_count"], 1)
            self.assertFalse(report["export_attach"]["auto_uploaded"])
            self.assertFalse(report["weights_trained"])
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_SPECIALIZED_MODEL_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-specialized-model.sh"),
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
        self.assertIn("COMPASS_SPECIALIZED_MODEL_ENABLED", proc.stderr)

    def test_cli_enable_gates_smoke(self) -> None:
        evidence = _mk_dir("sm0-cli-")
        try:
            env = os.environ.copy()
            env.pop("COMPASS_SPECIALIZED_MODEL_ENABLED", None)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-specialized-model.sh"),
                    "baseline",
                    "--repo-root",
                    str(ROOT),
                    "--enable-gates",
                    "--export-path",
                    str(SAMPLE_EXPORT),
                    "--evidence-dir",
                    str(evidence),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr + proc.stdout[-2000:])
            report = json.loads(proc.stdout)
            self.assertIn(report["overall_status"], {"pass", "warn"})
            self.assertFalse(report["weights_trained"])
            self.assertTrue(report["export_attach"]["attached"])
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_northstar_alias(self) -> None:
        help_out = subprocess.run(
            [str(ROOT / "scripts" / "northstar"), "help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        self.assertIn("specialized", help_out)
        self.assertIn("baseline", help_out)

    def test_missing_export_errors(self) -> None:
        with mock.patch.dict(os.environ, GATES):
            with self.assertRaises(SpecializedModelServiceError):
                run_baseline(
                    ROOT,
                    export_id="train-export-does-not-exist",
                    write_evidence=False,
                )


if __name__ == "__main__":
    unittest.main()
