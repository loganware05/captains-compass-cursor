"""M46 Behavior Intelligence Foundation — hermetic observe-only tests."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.behavior.enabled import behavior_eval_enabled, require_behavior_eval_enabled
from orchestrator.behavior.export import export_csv
from orchestrator.behavior.ledger import (
    build_behavior_evaluation,
    find_by_execution,
    write_behavior_evaluation,
)
from orchestrator.behavior.packet import build_evaluation_packet
from orchestrator.behavior.service import (
    BehaviorEvalServiceError,
    evaluate_execution,
    evaluate_pending,
)
from orchestrator.behavior.signals import BEHAVIOR_SIGNALS, normalize_signals
from orchestrator.behavior.thresholds import (
    DEFAULT_THRESHOLDS,
    signals_crossing_threshold,
    threshold_for_signal,
)
from orchestrator.providers.decision import StubDecisionProvider
from orchestrator.providers.decision.file_provider import FileDecisionProvider
from orchestrator.providers.decision.types import BehaviorEvalRequest
from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.telemetry.store import write_execution_run


FIXTURE_RUN = ROOT / "tests" / "fixtures" / "behavior" / "execution-run-contact.json"


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_BEHAVIOR_EVAL_ENABLED", None)
            self.assertFalse(behavior_eval_enabled())
            with self.assertRaises(PermissionError):
                require_behavior_eval_enabled()

    def test_enabled_truthy(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BEHAVIOR_EVAL_ENABLED": "1"}):
            self.assertTrue(behavior_eval_enabled())


class SchemaTests(unittest.TestCase):
    def test_valid_record(self) -> None:
        packet = {
            "execution_id": "run-x",
            "task_id": "t1",
            "plan_id": "p1",
            "agent": "implementation-agent",
            "model": "coding-strong",
            "skill_ids": ["testing-validation"],
            "repository_sha": "abc",
            "northstar_version": "1.46.0",
            "outcome": "success",
            "objective": "demo",
            "diff_meta": {},
            "evidence": [],
            "content_hash": "h",
            "schema_version": "1",
        }
        record = build_behavior_evaluation(
            packet,
            signals=normalize_signals({"praise": 0.8, "rework_required": 0.2}),
            provider="file",
            model_id="jev-1.13.0",
        )
        validate_document(record, "behavior-evaluation.schema.json")
        self.assertFalse(record["authority_mutation"])

    def test_authority_mutation_must_be_false(self) -> None:
        packet = {
            "execution_id": "run-x",
            "outcome": "success",
            "skill_ids": [],
            "evidence": [],
            "content_hash": "h",
        }
        record = build_behavior_evaluation(
            packet, signals={}, provider="stub", model_id=None
        )
        record["authority_mutation"] = True
        with self.assertRaises(ValidationError):
            validate_document(record, "behavior-evaluation.schema.json")


class ThresholdTests(unittest.TestCase):
    def test_boundary_uses_stricter_floor(self) -> None:
        self.assertEqual(threshold_for_signal("boundary_violation"), 0.40)
        self.assertEqual(threshold_for_signal("unsafe_git_operation"), 0.50)
        self.assertEqual(threshold_for_signal("praise"), 0.70)

    def test_crossings(self) -> None:
        signals = normalize_signals(
            {"boundary_violation": 0.41, "praise": 0.2, "rework_required": 0.71}
        )
        crossings = signals_crossing_threshold(signals, DEFAULT_THRESHOLDS)
        names = {c["signal"] for c in crossings}
        self.assertIn("boundary_violation", names)
        self.assertIn("rework_required", names)
        self.assertNotIn("praise", names)


class PacketAndLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m46-"))
        (self.tmp / ".agent" / "runs").mkdir(parents=True)
        (self.tmp / "VERSION").write_text("1.46.0\n", encoding="utf-8")
        with FIXTURE_RUN.open(encoding="utf-8") as handle:
            self.run_doc = json.load(handle)
        write_execution_run(self.tmp, self.run_doc)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_packet_normalize(self) -> None:
        packet = build_evaluation_packet(self.tmp, "run-fixture-contact-counter")
        self.assertEqual(packet["execution_id"], "run-fixture-contact-counter")
        self.assertEqual(packet["outcome"], "success")
        self.assertIn("content_hash", packet)
        self.assertTrue(packet["skill_ids"])

    def test_dual_ledger_and_idempotent(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_EVAL_ENABLED": "1",
                "COMPASS_DECISION_PROVIDER": "file",
            },
        ):
            first = evaluate_execution(self.tmp, "run-fixture-contact-counter")
            self.assertEqual(first["status"], "written")
            eid = first["record"]["evaluation_id"]
            json_path = self.tmp / ".agent" / "evaluations" / "behavior" / f"{eid}.json"
            ledger = self.tmp / ".agent" / "evaluations" / "behavior" / "ledger.jsonl"
            self.assertTrue(json_path.is_file())
            self.assertTrue(ledger.is_file())
            second = evaluate_execution(self.tmp, "run-fixture-contact-counter")
            self.assertEqual(second["status"], "idempotent")
            self.assertEqual(second["record"]["evaluation_id"], eid)

    def test_csv_export_non_canonical(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_EVAL_ENABLED": "1",
                "COMPASS_DECISION_PROVIDER": "file",
            },
        ):
            evaluate_execution(self.tmp, "run-fixture-contact-counter")
        dest = self.tmp / "out.csv"
        export_csv(self.tmp, dest)
        text = dest.read_text(encoding="utf-8")
        self.assertIn("evaluation_id", text)
        self.assertIn("praise", text)
        # Canonical ledger still present
        self.assertTrue(
            (self.tmp / ".agent" / "evaluations" / "behavior" / "ledger.jsonl").is_file()
        )

    def test_disabled_cli_path(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_BEHAVIOR_EVAL_ENABLED", None)
            with self.assertRaises(PermissionError):
                evaluate_execution(self.tmp, "run-fixture-contact-counter")

    def test_stub_abstains_but_persists(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_EVAL_ENABLED": "1",
                "COMPASS_DECISION_PROVIDER": "stub",
            },
        ):
            result = evaluate_execution(self.tmp, "run-fixture-contact-counter")
        self.assertEqual(result["status"], "written")
        self.assertTrue(result["record"]["abstain"])
        self.assertFalse(result["record"]["authority_mutation"])


class ProviderTests(unittest.TestCase):
    def test_stub_evaluate_behavior(self) -> None:
        provider = StubDecisionProvider()
        result = provider.evaluate_behavior(
            BehaviorEvalRequest(packet={"execution_id": "x", "objective": "y"})
        )
        self.assertTrue(result.abstain)
        self.assertEqual(result.to_dict()["applied"], False)

    def test_file_fixture_contact(self) -> None:
        provider = FileDecisionProvider()
        result = provider.evaluate_behavior(
            BehaviorEvalRequest(
                packet={
                    "execution_id": "run-fixture-contact-counter",
                    "objective": "Add accessible message character counter",
                }
            )
        )
        self.assertFalse(result.abstain)
        self.assertIn("praise", result.signals)
        self.assertGreater(result.signals["praise"], 0.5)
        self.assertEqual(len(result.signals), len(BEHAVIOR_SIGNALS))

    def test_file_malformed_signals_clamped(self) -> None:
        signals = normalize_signals({"praise": 2.5, "rework_required": -1, "nope": 0.9})
        self.assertEqual(signals["praise"], 1.0)
        self.assertEqual(signals["rework_required"], 0.0)
        self.assertNotIn("nope", signals)


class NoMutationTests(unittest.TestCase):
    def test_evaluate_does_not_touch_routing_or_skills(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="m46-nomut-"))
        try:
            (tmp / ".agent" / "runs").mkdir(parents=True)
            (tmp / "VERSION").write_text("1.46.0\n", encoding="utf-8")
            with FIXTURE_RUN.open(encoding="utf-8") as handle:
                run_doc = json.load(handle)
            write_execution_run(tmp, run_doc)
            skills_before = sorted(p.name for p in (ROOT / ".cursor" / "skills").iterdir())
            with mock.patch.dict(
                os.environ,
                {
                    "COMPASS_BEHAVIOR_EVAL_ENABLED": "1",
                    "COMPASS_DECISION_PROVIDER": "file",
                },
            ):
                evaluate_execution(tmp, "run-fixture-contact-counter")
            skills_after = sorted(p.name for p in (ROOT / ".cursor" / "skills").iterdir())
            self.assertEqual(skills_before, skills_after)
            # No routing proposal written into control repo by evaluate
            self.assertFalse((tmp / ".agent" / "routing").exists())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
