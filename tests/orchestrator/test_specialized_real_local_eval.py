"""Specialized real local eval — student protocol tests (#305)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.integrations.transport import HttpResponse, RecordingTransport
from orchestrator.specialized.lora import evaluate_lora
from orchestrator.specialized.scoring import load_gold_set, score_gold_set
from orchestrator.specialized.service import run_baseline
from orchestrator.specialized.student import (
    FixtureMapStudent,
    GoldStubStudent,
    HttpStudent,
    resolve_student,
)
from orchestrator.schemas.validate import validate_document

GATES = {"COMPASS_SPECIALIZED_MODEL_ENABLED": "1"}
GOLD = ROOT / "tests" / "fixtures" / "specialized-model-gold" / "tasks.json"


class StudentResolveTests(unittest.TestCase):
    def test_default_is_stub(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_SPECIALIZED_STUDENT", None)
            os.environ.pop("COMPASS_SPECIALIZED_STUDENT_URL", None)
            student = resolve_student()
            self.assertEqual(student.mode, "stub")
            self.assertIsInstance(student, GoldStubStudent)

    def test_http_student_https_only(self) -> None:
        with self.assertRaises(ValueError):
            HttpStudent("http://example.test/student")


class ScoringLocalTests(unittest.TestCase):
    def test_stub_path_unchanged(self) -> None:
        gold = load_gold_set(GOLD)
        scores = score_gold_set(gold)
        self.assertEqual(scores["student_mode"], "stub")
        self.assertEqual(scores["stub_student_rate"], 1.0)
        self.assertNotIn("local_student_rate", scores)

    def test_fixture_local_student_scores(self) -> None:
        gold = load_gold_set(GOLD)
        # Perfect answers: reuse stub text as local answers.
        answers = {
            str(t["id"]): str(t.get("stub_student_answer") or "")
            for t in gold["tasks"]
        }
        scores = score_gold_set(gold, student=FixtureMapStudent(answers))
        self.assertEqual(scores["student_mode"], "local")
        self.assertEqual(scores["local_student_rate"], 1.0)
        self.assertEqual(scores["stub_student_rate"], 1.0)

    def test_weak_local_student_recorded(self) -> None:
        gold = load_gold_set(GOLD)
        answers = {str(t["id"]): "nope" for t in gold["tasks"]}
        scores = score_gold_set(gold, student=FixtureMapStudent(answers))
        self.assertEqual(scores["local_student_rate"], 0.0)
        self.assertEqual(scores["stub_student_rate"], 1.0)


class BaselineLocalTests(unittest.TestCase):
    def test_baseline_local_holds_when_trailing(self) -> None:
        gold = load_gold_set(GOLD)
        answers = {str(t["id"]): "nope" for t in gold["tasks"]}
        with mock.patch.dict(os.environ, GATES):
            with tempfile.TemporaryDirectory() as tmp:
                report = run_baseline(
                    ROOT,
                    gold_path=GOLD,
                    write_evidence=True,
                    evidence_dir=Path(tmp),
                    student=FixtureMapStudent(answers),
                )
        self.assertEqual(report["scores"]["student_mode"], "local")
        self.assertEqual(report["go_no_go"], "hold")
        self.assertEqual(report["scores"]["local_student_rate"], 0.0)
        validate_document(report, "specialized-model-baseline-report.schema.json")

    def test_baseline_stub_default_still_go(self) -> None:
        with mock.patch.dict(os.environ, GATES, clear=False):
            os.environ.pop("COMPASS_SPECIALIZED_STUDENT", None)
            os.environ.pop("COMPASS_SPECIALIZED_STUDENT_URL", None)
            with tempfile.TemporaryDirectory() as tmp:
                report = run_baseline(
                    ROOT, gold_path=GOLD, write_evidence=True, evidence_dir=Path(tmp)
                )
        self.assertEqual(report["scores"]["student_mode"], "stub")
        self.assertEqual(report["go_no_go"], "go")
        validate_document(report, "specialized-model-baseline-report.schema.json")


class HttpStudentTests(unittest.TestCase):
    def test_recording_transport_roundtrip(self) -> None:
        transport = RecordingTransport(
            {
                ("POST", "https://student.example.test/v1/answer"): HttpResponse(
                    status=200,
                    headers={"content-type": "application/json"},
                    body=b'{"answer":"policy candidate approval gate"}',
                )
            }
        )
        student = HttpStudent(
            "https://student.example.test/v1/answer", transport=transport
        )
        gold = load_gold_set(GOLD)
        task = gold["tasks"][0]
        # Force keywords that match our canned answer loosely.
        task = dict(task)
        task["expected_keywords"] = ["policy", "candidate"]
        self.assertIn("policy", student.answer(task).lower())
        self.assertEqual(len(transport.calls), 1)


class LoraEvaluateLocalTests(unittest.TestCase):
    def test_evaluate_records_local_mode(self) -> None:
        gold = load_gold_set(GOLD)
        answers = {str(t["id"]): "nope" for t in gold["tasks"]}
        with mock.patch.dict(os.environ, GATES):
            with tempfile.TemporaryDirectory() as tmp:
                report = evaluate_lora(
                    ROOT,
                    gold_path=GOLD,
                    dry_run=True,
                    write_evidence=True,
                    evidence_dir=Path(tmp),
                    student=FixtureMapStudent(answers),
                )
        self.assertEqual(report["comparison"]["student_mode"], "local")
        self.assertEqual(report["baseline_scores"]["local_student_rate"], 0.0)
        validate_document(report, "specialized-model-lora-run.schema.json")


if __name__ == "__main__":
    unittest.main()
