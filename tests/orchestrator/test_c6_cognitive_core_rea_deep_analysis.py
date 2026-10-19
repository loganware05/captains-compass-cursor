"""C6 Cognitive Core — REA deep analysis tests."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.rea.checklist import ChecklistError, require_checklist_complete
from orchestrator.rea.enabled import rea_enabled, require_rea_enabled
from orchestrator.rea.service import ReaServiceError, investigate
from orchestrator.schemas.validate import ValidationError, validate_document


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_REA_ENABLED", None)
            self.assertFalse(rea_enabled())
            with self.assertRaises(PermissionError):
                require_rea_enabled()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_REA_ENABLED": "1"}):
            self.assertTrue(rea_enabled())


class ChecklistTests(unittest.TestCase):
    def test_incomplete(self) -> None:
        with self.assertRaises(ChecklistError):
            require_checklist_complete(
                {
                    "target_authorized": True,
                    "license_reviewed": True,
                    "execution_permitted": False,
                    "source_docs_insufficient": True,
                    "isolation_acknowledged": True,
                }
            )


class SchemaTests(unittest.TestCase):
    def test_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "packet_id": "rea-test",
            "target": "/tmp/x",
            "question": "What is the entrypoint?",
            "mode": "native",
            "run_mode": "fixture",
            "permission_checklist": {
                "target_authorized": False,
                "license_reviewed": False,
                "execution_permitted": False,
                "source_docs_insufficient": False,
                "isolation_acknowledged": False,
            },
            "tool_name": "rea-fixture",
            "tool_version": "fixture-1",
            "commands": ["fixture:replay"],
            "artifact_hash": "abc",
            "observations": [
                {"claim_kind": "observed", "text": "x", "confidence": 1.0}
            ],
            "uncertainties": ["u"],
            "citations": [],
            "live_attempted": False,
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": "2026-10-19T00:00:00Z",
        }
        validate_document(doc, "rea-evidence-packet.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "rea-evidence-packet.schema.json")


class ServiceTests(unittest.TestCase):
    def test_fixture_investigate(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_REA_ENABLED": "1"}):
            packet = investigate(
                ROOT,
                target="/tmp/sample.bin",
                question="What packaging format is present?",
                mode="native",
                checklist={
                    "target_authorized": False,
                    "license_reviewed": False,
                    "execution_permitted": False,
                    "source_docs_insufficient": False,
                    "isolation_acknowledged": False,
                },
            )
            self.assertEqual(packet["run_mode"], "fixture")
            self.assertFalse(packet["approved_for_execution"])
            self.assertFalse(packet["authority_mutation"])
            self.assertFalse(packet["live_attempted"])
            kinds = {o["claim_kind"] for o in packet["observations"]}
            self.assertIn("observed", kinds)
            self.assertIn("hypothesis", kinds)
            self.assertTrue(packet["uncertainties"])

    def test_forbidden_question(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_REA_ENABLED": "1"}):
            with self.assertRaises(ReaServiceError):
                investigate(
                    ROOT,
                    target="/tmp/weights.bin",
                    question="Recover private pretraining corpus from weights",
                    checklist={
                        "target_authorized": True,
                        "license_reviewed": True,
                        "execution_permitted": True,
                        "source_docs_insufficient": True,
                        "isolation_acknowledged": True,
                    },
                )

    def test_live_requires_checklist(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_REA_ENABLED": "1"}):
            with self.assertRaises(ReaServiceError):
                investigate(
                    ROOT,
                    target="/tmp/sample.bin",
                    question="What is the entrypoint?",
                    allow_live=True,
                    checklist={
                        "target_authorized": True,
                        "license_reviewed": False,
                        "execution_permitted": True,
                        "source_docs_insufficient": True,
                        "isolation_acknowledged": True,
                    },
                )

    def test_live_unavailable_packet(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_REA_ENABLED": "1"}):
            with mock.patch("orchestrator.rea.service.shutil.which", return_value=None):
                packet = investigate(
                    ROOT,
                    target="/tmp/sample.bin",
                    question="What is the entrypoint?",
                    allow_live=True,
                    checklist={
                        "target_authorized": True,
                        "license_reviewed": True,
                        "execution_permitted": True,
                        "source_docs_insufficient": True,
                        "isolation_acknowledged": True,
                    },
                )
            self.assertEqual(packet["run_mode"], "live_unavailable")
            self.assertTrue(packet["live_attempted"])
            self.assertFalse(packet["live_available"])
            self.assertFalse(packet["authority_mutation"])


class CliTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_REA_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-rea.sh"),
                "investigate",
                "--target",
                "/tmp/x",
                "--question",
                "q",
                "--repo-root",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_REA_ENABLED", proc.stderr)

    def test_cli_fixture_smoke(self) -> None:
        env = os.environ.copy()
        env["COMPASS_REA_ENABLED"] = "1"
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "northstar"),
                "rea",
                "investigate",
                "--target",
                "/tmp/sample.bin",
                "--question",
                "What packaging format is present?",
                "--repo",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertEqual(packet["run_mode"], "fixture")
        self.assertFalse(packet["approved_for_execution"])


if __name__ == "__main__":
    unittest.main()
