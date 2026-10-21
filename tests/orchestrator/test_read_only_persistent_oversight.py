"""Read-only persistent oversight composer tests."""

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
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-oversight-tests"

from orchestrator.oversight.enabled import require_oversight_status_gate
from orchestrator.oversight.service import OversightServiceError, run_oversight
from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.status.enabled import status_enabled

GATES = {
    "COMPASS_STATUS_ENABLED": "1",
    "COMPASS_BRAIN_ENABLED": "1",
}


def _mk_dir(prefix: str) -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(_FIXTURE_ROOT)))


class GateTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_STATUS_ENABLED", None)
            self.assertFalse(status_enabled())
            with self.assertRaises(PermissionError):
                require_oversight_status_gate()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            require_oversight_status_gate()


class SchemaTests(unittest.TestCase):
    def test_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "run_id": "oversight-test",
            "plan_id": "read-only-persistent-oversight",
            "repository_sha": "abc",
            "northstar_version": "1.68.0",
            "since_sha": None,
            "steps": [
                {
                    "id": "status-snapshot",
                    "status": "pass",
                    "summary": "ok",
                    "details": {},
                }
            ],
            "brain_synced": False,
            "snapshot_id": "psnap-test",
            "compare_status": "skipped",
            "proposal_id": "srec-test",
            "proposal_path": None,
            "proposal_applied": False,
            "finding_count": 0,
            "action_count": 0,
            "warnings": [],
            "overall_status": "pass",
            "evidence_path": None,
            "notes": "test",
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": "2026-10-21T00:00:00Z",
        }
        validate_document(doc, "oversight-run.schema.json")
        bad = dict(doc)
        bad["proposal_applied"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "oversight-run.schema.json")
        bad2 = dict(doc)
        bad2["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad2, "oversight-run.schema.json")


class RunnerTests(unittest.TestCase):
    def test_hermetic_run_control_repo(self) -> None:
        evidence = _mk_dir("ov-ev-")
        try:
            with mock.patch.dict(os.environ, GATES):
                report = run_oversight(
                    ROOT,
                    evidence_dir=evidence,
                    write_evidence=True,
                )
            self.assertIn(report["overall_status"], {"pass", "warn"})
            self.assertFalse(report["approved_for_execution"])
            self.assertFalse(report["authority_mutation"])
            self.assertFalse(report["proposal_applied"])
            self.assertTrue(report["brain_synced"])
            self.assertTrue(report.get("snapshot_id"))
            self.assertTrue(report.get("proposal_id"))
            step_ids = [s["id"] for s in report["steps"]]
            self.assertEqual(
                step_ids,
                [
                    "brain-sync",
                    "status-snapshot",
                    "status-compare",
                    "status-reconcile",
                ],
            )
            validate_document(report, "oversight-run.schema.json")
            self.assertTrue((evidence / "SUMMARY.md").is_file())
            runs = ROOT / ".agent" / "status" / "oversight-runs"
            self.assertTrue(runs.is_dir())
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_skip_brain(self) -> None:
        evidence = _mk_dir("ov-skip-")
        try:
            with mock.patch.dict(
                os.environ, {"COMPASS_STATUS_ENABLED": "1"}, clear=False
            ):
                os.environ.pop("COMPASS_BRAIN_ENABLED", None)
                report = run_oversight(
                    ROOT,
                    include_brain=False,
                    evidence_dir=evidence,
                    write_evidence=True,
                )
            self.assertFalse(report["brain_synced"])
            self.assertEqual(report["steps"][0]["status"], "skipped")
            self.assertFalse(report["proposal_applied"])
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_STATUS_ENABLED", None)
        env.pop("COMPASS_BRAIN_ENABLED", None)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-oversight.sh"), "--repo-root", str(ROOT)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_STATUS_ENABLED", proc.stderr)

    def test_cli_enable_gates_smoke(self) -> None:
        evidence = _mk_dir("ov-cli-")
        try:
            env = os.environ.copy()
            env.pop("COMPASS_STATUS_ENABLED", None)
            env.pop("COMPASS_BRAIN_ENABLED", None)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-oversight.sh"),
                    "--repo-root",
                    str(ROOT),
                    "--enable-gates",
                    "--evidence-dir",
                    str(evidence),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertIn(proc.returncode, {0}, msg=proc.stderr + proc.stdout[-2000:])
            report = json.loads(proc.stdout)
            self.assertIn(report["overall_status"], {"pass", "warn"})
            self.assertFalse(report["proposal_applied"])
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_northstar_aliases(self) -> None:
        help_out = subprocess.run(
            [str(ROOT / "scripts" / "northstar"), "help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        self.assertIn("oversight", help_out)
        self.assertIn("post-merge", help_out)


if __name__ == "__main__":
    unittest.main()
