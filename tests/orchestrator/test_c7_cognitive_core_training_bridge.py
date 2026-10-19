"""C7 Cognitive Core — Training bridge tests."""

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

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.train_bridge.checklist import ChecklistError, require_checklist_complete
from orchestrator.train_bridge.enabled import (
    require_train_bridge_enabled,
    train_bridge_enabled,
)
from orchestrator.train_bridge.service import (
    TrainBridgeServiceError,
    train_export,
    train_review,
)

COMPLETE_CHECKLIST = {
    "export_authorized": True,
    "secrets_redacted_ack": True,
    "license_reviewed": True,
    "pii_reviewed": True,
    "specialized_model_handoff_ack": True,
}


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_TRAIN_BRIDGE_ENABLED", None)
            self.assertFalse(train_bridge_enabled())
            with self.assertRaises(PermissionError):
                require_train_bridge_enabled()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TRAIN_BRIDGE_ENABLED": "1"}):
            self.assertTrue(train_bridge_enabled())


class ChecklistTests(unittest.TestCase):
    def test_incomplete(self) -> None:
        with self.assertRaises(ChecklistError):
            require_checklist_complete(
                {
                    "export_authorized": True,
                    "secrets_redacted_ack": True,
                    "license_reviewed": False,
                    "pii_reviewed": True,
                    "specialized_model_handoff_ack": True,
                }
            )


class SchemaTests(unittest.TestCase):
    def test_manifest_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "export_id": "train-export-test",
            "source": "experiences",
            "run_mode": "fixture",
            "trajectory_count": 0,
            "trajectories": [],
            "permission_checklist": {
                "export_authorized": False,
                "secrets_redacted_ack": False,
                "license_reviewed": False,
                "pii_reviewed": False,
                "specialized_model_handoff_ack": False,
            },
            "dataset_schema_version": "northstar.training-export.v1",
            "citations": [],
            "auto_uploaded": False,
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": "2026-10-19T00:00:00Z",
        }
        validate_document(doc, "training-export-manifest.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "training-export-manifest.schema.json")
        bad2 = dict(doc)
        bad2["auto_uploaded"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad2, "training-export-manifest.schema.json")

    def test_review_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "review_id": "train-review-test",
            "export_id": "train-export-test",
            "trajectory_count": 0,
            "gates": {
                "independent_eval_complete": False,
                "security_review_complete": False,
                "captain_approval_recorded": False,
                "export_checklist_complete": False,
            },
            "ready_for_specialized_model": False,
            "blocking_reasons": ["independent_eval_complete"],
            "citations": [],
            "auto_uploaded": False,
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": "2026-10-19T00:00:00Z",
        }
        validate_document(doc, "training-export-review.schema.json")
        bad = dict(doc)
        bad["authority_mutation"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "training-export-review.schema.json")


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="c7-train-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_export_requires_checklist(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TRAIN_BRIDGE_ENABLED": "1"}):
            with self.assertRaises(TrainBridgeServiceError):
                train_export(
                    ROOT,
                    source="experiences",
                    allow_fixtures=True,
                    checklist={
                        "export_authorized": True,
                        "secrets_redacted_ack": False,
                        "license_reviewed": True,
                        "pii_reviewed": True,
                        "specialized_model_handoff_ack": True,
                    },
                    out_dir=self.tmp,
                )

    def test_refuses_silent_fixture_fallback(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TRAIN_BRIDGE_ENABLED": "1"}, clear=False):
            os.environ.pop("COMPASS_TRAIN_BRIDGE_FIXTURE", None)
            overlay = self.tmp / "empty-repo"
            overlay.mkdir()
            (overlay / "VERSION").write_text("1.66.0-test\n", encoding="utf-8")
            with self.assertRaises(TrainBridgeServiceError) as ctx:
                train_export(
                    overlay,
                    source="experiences",
                    checklist=COMPLETE_CHECKLIST,
                    allow_fixtures=False,
                )
            self.assertIn("fixture", str(ctx.exception).lower())

    def test_hermetic_export_and_review(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TRAIN_BRIDGE_ENABLED": "1"}):
            overlay = self.tmp / "overlay"
            overlay.mkdir()
            (overlay / "VERSION").write_text("1.66.0-test\n", encoding="utf-8")
            out = self.tmp / "exports"
            manifest = train_export(
                overlay,
                source="experiences",
                checklist=COMPLETE_CHECKLIST,
                allow_fixtures=True,
                out_dir=out,
            )
            self.assertEqual(manifest["run_mode"], "fixture")
            self.assertGreaterEqual(manifest["trajectory_count"], 1)
            self.assertFalse(manifest["approved_for_execution"])
            self.assertFalse(manifest["authority_mutation"])
            self.assertFalse(manifest["auto_uploaded"])
            # Canonical store write enables review by id
            store_path = (
                overlay / ".agent" / "training-exports" / f"{manifest['export_id']}.json"
            )
            self.assertTrue(store_path.is_file())
            alt = out / f"{manifest['export_id']}.json"
            self.assertTrue(alt.is_file())

            review = train_review(overlay, export_id=manifest["export_id"])
            self.assertFalse(review["ready_for_specialized_model"])
            self.assertIn("independent_eval_complete", review["blocking_reasons"])

            # Review via --export-path (alt copy)
            review_path = train_review(overlay, export_file=alt)
            self.assertEqual(review_path["export_id"], manifest["export_id"])

            ready = train_review(
                overlay,
                export_id=manifest["export_id"],
                independent_eval_complete=True,
                security_review_complete=True,
                captain_approval_recorded=True,
            )
            self.assertTrue(ready["ready_for_specialized_model"])
            self.assertEqual(ready["blocking_reasons"], [])
            self.assertFalse(ready["authority_mutation"])

    def test_unreviewed_success_not_eligible(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TRAIN_BRIDGE_ENABLED": "1"}):
            exp = {
                "experience_id": "exp-unreviewed",
                "plan_id": "plan-x",
                "objective": "do a thing",
                "outcome": "success",
                "skills_used": [],
                "capabilities_exercised": [],
                "lessons": [],
                "provenance": {},
                "created_at": "2026-10-19T00:00:00Z",
            }
            with mock.patch(
                "orchestrator.train_bridge.service._collect_experiences",
                return_value=([exp], "recorded"),
            ):
                with self.assertRaises(TrainBridgeServiceError):
                    train_export(
                        ROOT,
                        source="experiences",
                        checklist=COMPLETE_CHECKLIST,
                        out_dir=self.tmp / "unreviewed",
                    )

    def test_redacts_secrets_in_trajectory(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TRAIN_BRIDGE_ENABLED": "1"}):
            secret_exp = {
                "experience_id": "exp-secret",
                "plan_id": "plan-secret",
                "run_id": "run-secret",
                "objective": (
                    "Deploy with api_key=sk-abcdefghijklmnopqrstuvwxyz012345 "
                    "and AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG"
                ),
                "outcome": "success",
                "skills_used": ["token=supersecretvalue123"],
                "capabilities_exercised": ["xoxb-1234567890-abcdefghij"],
                "lessons": ["Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig"],
                "provenance": {"reviewed": True},
                "created_at": "2026-10-19T00:00:00Z",
            }
            with mock.patch(
                "orchestrator.train_bridge.service._collect_experiences",
                return_value=([secret_exp], "recorded"),
            ):
                manifest = train_export(
                    ROOT,
                    source="experiences",
                    checklist=COMPLETE_CHECKLIST,
                    out_dir=self.tmp / "redact",
                )
            traj = manifest["trajectories"][0]
            blob = json.dumps(traj)
            self.assertIn("[REDACTED]", blob)
            self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz012345", blob)
            self.assertNotIn("supersecretvalue123", blob)
            self.assertNotIn("wJalrXUtnFEMI/K7MDENG", blob)
            self.assertNotIn("xoxb-1234567890-abcdefghij", blob)
            self.assertNotIn("eyJhbGciOiJIUzI1NiJ9.payload.sig", blob)


class CliTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_TRAIN_BRIDGE_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-train-bridge.sh"),
                "export",
                "--from",
                "experiences",
                "--repo-root",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_TRAIN_BRIDGE_ENABLED", proc.stderr)

    def test_cli_export_review_smoke(self) -> None:
        env = os.environ.copy()
        env["COMPASS_TRAIN_BRIDGE_ENABLED"] = "1"
        with tempfile.TemporaryDirectory(prefix="c7-cli-") as tmp:
            overlay = Path(tmp) / "overlay"
            overlay.mkdir()
            (overlay / "VERSION").write_text("1.66.0-test\n", encoding="utf-8")
            out = Path(tmp) / "exports"
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "northstar"),
                    "train",
                    "export",
                    "--from",
                    "experiences",
                    "--fixture",
                    "--export-authorized",
                    "--secrets-redacted-ack",
                    "--license-reviewed",
                    "--pii-reviewed",
                    "--specialized-model-handoff-ack",
                    "--out",
                    str(out),
                    "--repo",
                    str(overlay),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            manifest = json.loads(proc.stdout)
            self.assertEqual(manifest["run_mode"], "fixture")
            self.assertFalse(manifest["approved_for_execution"])
            self.assertFalse(manifest["auto_uploaded"])
            self.assertGreaterEqual(manifest["trajectory_count"], 1)

            # Review the same export via store id (dual-write)
            proc2 = subprocess.run(
                [
                    str(ROOT / "scripts" / "northstar"),
                    "train",
                    "review",
                    "--export-id",
                    manifest["export_id"],
                    "--repo",
                    str(overlay),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc2.returncode, 0, proc2.stderr)
            review = json.loads(proc2.stdout)
            self.assertFalse(review["ready_for_specialized_model"])

            # Review via --export-path on the --out copy
            alt = out / f"{manifest['export_id']}.json"
            proc3 = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-train-bridge.sh"),
                    "review",
                    "--export-path",
                    str(alt),
                    "--repo-root",
                    str(overlay),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc3.returncode, 0, proc3.stderr)
            self.assertEqual(json.loads(proc3.stdout)["export_id"], manifest["export_id"])


if __name__ == "__main__":
    unittest.main()
