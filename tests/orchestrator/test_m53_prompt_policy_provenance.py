"""M53 Prompt/Policy Provenance + Behavior Exemplars — hermetic tests."""

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

from orchestrator.behavior.enabled import provenance_enabled, require_provenance_enabled
from orchestrator.behavior.exemplars.service import draft_exemplar, list_exemplars
from orchestrator.behavior.ledger import build_behavior_evaluation, write_behavior_evaluation
from orchestrator.behavior.provenance.service import (
    ProvenanceServiceError,
    build_provenance_record,
    capture_from_evaluation,
    capture_from_execution,
    list_provenance,
)
from orchestrator.schemas.validate import ValidationError, validate_document


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_PROVENANCE_ENABLED", None)
            self.assertFalse(provenance_enabled())
            with self.assertRaises(PermissionError):
                require_provenance_enabled()

    def test_enabled_truthy(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_PROVENANCE_ENABLED": "1"}):
            self.assertTrue(provenance_enabled())


class SchemaTests(unittest.TestCase):
    def test_provenance_schema_locks(self) -> None:
        doc = {
            "provenance_id": "prov-test",
            "schema_version": "1",
            "created_at": "2026-10-11T00:00:00Z",
            "execution_id": "exec-1",
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(doc, "execution-provenance.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "execution-provenance.schema.json")

    def test_exemplar_auto_promoted_must_be_false(self) -> None:
        doc = {
            "exemplar_id": "ex-test",
            "schema_version": "1",
            "created_at": "2026-10-11T00:00:00Z",
            "polarity": "positive",
            "summary": "prefer evidence",
            "auto_promoted": False,
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(doc, "behavior-exemplar.schema.json")
        bad = dict(doc)
        bad["auto_promoted"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "behavior-exemplar.schema.json")


class ProvenanceServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m53-prov-"))
        (self.tmp / "VERSION").write_text("1.58.0\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_capture_requires_gate(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_PROVENANCE_ENABLED", None)
            with self.assertRaises(PermissionError):
                capture_from_execution(self.tmp, "exec-missing")

    def test_capture_from_evaluation_best_effort(self) -> None:
        packet = {
            "execution_id": "exec-m53-1",
            "task_id": "task-1",
            "agent": "implementation-agent",
            "skill_ids": ["testing-validation"],
            "outcome": "success",
            "objective": "m53",
            "repository_sha": "abc",
            "northstar_version": "1.58.0",
            "evidence": [],
        }
        record = build_behavior_evaluation(
            packet,
            signals={"praise": 0.9},
            provider="stub",
            model_id="stub",
            prompt_bundle_hash="sha256:bundle",
            evaluation_id="beval-m53-0001",
        )
        write_behavior_evaluation(self.tmp, record)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_PROVENANCE_ENABLED", None)
            self.assertIsNone(capture_from_evaluation(self.tmp, record))
        with mock.patch.dict(os.environ, {"COMPASS_PROVENANCE_ENABLED": "1"}):
            info = capture_from_evaluation(self.tmp, record)
            self.assertIsNotNone(info)
            assert info is not None
            self.assertFalse(info["provenance"]["authority_mutation"])
            self.assertEqual(info["provenance"]["prompt_bundle_hash"], "sha256:bundle")
            listed = list_provenance(self.tmp)
            self.assertEqual(listed["count"], 1)

    def test_build_partial_fields_ok(self) -> None:
        doc = build_provenance_record(
            self.tmp,
            execution_id="exec-partial",
            packet={"execution_id": "exec-partial", "skill_ids": ["x"]},
        )
        self.assertEqual(doc["execution_id"], "exec-partial")
        self.assertTrue(doc["provenance_id"].startswith("prov-"))
        self.assertFalse(doc["approved_for_execution"])


class ExemplarServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m53-ex-"))
        (self.tmp / "VERSION").write_text("1.58.0\n", encoding="utf-8")
        packet = {
            "execution_id": "exec-ex-1",
            "agent": "implementation-agent",
            "skill_ids": [],
            "outcome": "success",
            "objective": "ex",
            "repository_sha": "abc",
            "northstar_version": "1.58.0",
            "evidence": [],
        }
        self.record = build_behavior_evaluation(
            packet,
            signals={"praise": 0.8},
            provider="stub",
            model_id="stub",
            evaluation_id="beval-ex-0001",
        )
        write_behavior_evaluation(self.tmp, self.record)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_draft_positive_not_auto_promoted(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_PROVENANCE_ENABLED": "1"}):
            result = draft_exemplar(
                self.tmp,
                polarity="positive",
                evaluation_id="beval-ex-0001",
            )
            self.assertFalse(result["auto_promoted"])
            self.assertFalse(result["exemplar"]["auto_promoted"])
            self.assertEqual(result["exemplar"]["polarity"], "positive")
            path = Path(result["path"])
            self.assertTrue(path.is_file())
            listed = list_exemplars(self.tmp, polarity="positive")
            self.assertEqual(listed["count"], 1)
            # Canonical skills dir must not be created by exemplar draft.
            self.assertFalse((self.tmp / ".cursor" / "skills").exists())

    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_PROVENANCE_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-provenance.sh"),
                "list",
                "--repo-root",
                str(self.tmp),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_PROVENANCE_ENABLED", proc.stderr)

    def test_cli_draft_and_list(self) -> None:
        env = os.environ.copy()
        env["COMPASS_PROVENANCE_ENABLED"] = "1"
        env["PYTHONPATH"] = str(ROOT)
        draft = subprocess.run(
            [
                str(ROOT / "scripts" / "run-provenance.sh"),
                "examples-draft",
                "--polarity",
                "negative",
                "--evaluation-id",
                "beval-ex-0001",
                "--repo-root",
                str(self.tmp),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(draft.returncode, 0, draft.stderr)
        payload = json.loads(draft.stdout)
        self.assertFalse(payload["exemplar"]["auto_promoted"])
        listed = subprocess.run(
            [
                str(ROOT / "scripts" / "run-provenance.sh"),
                "examples-list",
                "--repo-root",
                str(self.tmp),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(listed.returncode, 0, listed.stderr)
        body = json.loads(listed.stdout)
        self.assertGreaterEqual(body["count"], 1)


if __name__ == "__main__":
    unittest.main()
