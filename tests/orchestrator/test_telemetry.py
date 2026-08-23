"""Milestone 2 telemetry store and recorder tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.telemetry.record import (
    build_execution_run,
    experience_from_run,
    record_workstream,
)
from orchestrator.telemetry.store import (
    TelemetryStoreError,
    list_experiences,
    load_execution_run,
    load_experience,
    write_execution_run,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "experience" / "contact-counter.json"


class ExperienceSchemaTests(unittest.TestCase):
    def test_fixture_validates(self) -> None:
        doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
        validate_document(doc, "experience.schema.json")

    def test_missing_required_fails(self) -> None:
        with self.assertRaises(ValidationError):
            validate_document({"experience_id": "x"}, "experience.schema.json")


class TelemetryStoreTests(unittest.TestCase):
    def test_round_trip_run_and_experience(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = build_execution_run(
                plan_id="plan-demo",
                outcome="success",
                objective="Demo",
                skills=["testing-validation"],
                provenance={"branch": "feature/demo"},
            )
            exp = experience_from_run(run, source_instance="control-test")
            run["experience_id"] = exp["experience_id"]
            write_execution_run(repo, run)
            from orchestrator.telemetry.store import write_experience

            write_experience(repo, exp)
            loaded_run = load_execution_run(repo, run["run_id"])
            loaded_exp = load_experience(repo, exp["experience_id"])
            self.assertEqual(loaded_run["plan_id"], "plan-demo")
            self.assertEqual(loaded_exp["source_instance"], "control-test")
            self.assertEqual(len(list_experiences(repo)), 1)

    def test_rejects_path_traversal_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = build_execution_run(plan_id="plan-demo", run_id="../evil")
            with self.assertRaises(TelemetryStoreError):
                write_execution_run(repo, run)

    def test_record_workstream_writes_both(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            paths = record_workstream(
                repo,
                plan_id="m2-demo",
                outcome="success",
                skills=["execution-telemetry"],
                source_instance="control-live",
            )
            self.assertTrue(paths["execution_run"].is_file())
            self.assertTrue(paths["experience"].is_file())


if __name__ == "__main__":
    unittest.main()
