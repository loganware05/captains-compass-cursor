"""I2 T3 ExecutionAdapter tests (#251)."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.integrations.t3.enabled import (
    require_t3_exec_enabled,
    t3_exec_enabled,
)
from orchestrator.integrations.t3.plan_gate import PlanGateError, require_plan_binding
from orchestrator.integrations.t3.service import (
    T3ServiceError,
    cancel_execution,
    collect_execution,
    list_capabilities,
    start_execution,
    status_execution,
)
from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.status.development_refs import collect_execution_refs
from orchestrator.status.drift import detect_drift


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_T3_EXEC_ENABLED", None)
            self.assertFalse(t3_exec_enabled())
            with self.assertRaises(PermissionError):
                require_t3_exec_enabled()


class PlanGateTests(unittest.TestCase):
    def test_refuse_mismatched_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "IMPLEMENTATION_PLAN.md").write_text(
                "- Status: **APPROVED**\n\n"
                "| Field | Value |\n|---|---|\n"
                "| Plan ID | `other-plan` |\n",
                encoding="utf-8",
            )
            with self.assertRaises(PlanGateError):
                require_plan_binding(repo, plan_id="i2-t3-execution-adapter")

    def test_fixture_allow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binding = require_plan_binding(
                Path(tmp),
                plan_id="i2-t3-execution-adapter",
                allow_fixture_plan=True,
            )
            self.assertEqual(binding["binding"], "fixture-allow")


class ServiceTests(unittest.TestCase):
    def test_fixture_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with mock.patch.dict(os.environ, {"COMPASS_T3_EXEC_ENABLED": "1"}):
                caps = list_capabilities()
                self.assertEqual(caps["mode"], "fixture")
                started = start_execution(
                    repo,
                    plan_id="i2-t3-execution-adapter",
                    objective="fixture t3 start",
                    allow_fixture_plan=True,
                )
                self.assertFalse(started["bypassed_plan_gate"])
                exec_id = started["execution"]["execution_id"]
                validate_document(started["execution"], "t3-execution-run.schema.json")
                status = status_execution(repo, exec_id)
                self.assertIn(status["execution"]["status"], {"running", "started"})
                collected = collect_execution(repo, exec_id)
                self.assertEqual(collected["execution"]["status"], "completed")
                refs = collect_execution_refs(repo)
                self.assertGreaterEqual(len(refs), 1)
                # Fresh start then cancel
                started2 = start_execution(
                    repo,
                    plan_id="i2-t3-execution-adapter",
                    objective="cancel me",
                    allow_fixture_plan=True,
                )
                cancelled = cancel_execution(repo, started2["execution"]["execution_id"])
                self.assertEqual(cancelled["execution"]["status"], "cancelled")

    def test_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "execution_id": "t3-exec-test",
            "plan_id": "i2-t3-execution-adapter",
            "mode": "fixture",
            "provider": "fixture",
            "model": "",
            "objective": "x",
            "status": "started",
            "thread_ref": "fixture-thread",
            "timeline": [{"at": "2026-11-07T00:00:00Z", "status": "started"}],
            "artifacts": [],
            "collected_summary": "",
            "created_at": "2026-11-07T00:00:00Z",
            "updated_at": "2026-11-07T00:00:00Z",
            "approved_for_execution": False,
            "authority_mutation": False,
            "auto_promoted": False,
            "bypassed_plan_gate": False,
        }
        validate_document(doc, "t3-execution-run.schema.json")
        bad = dict(doc)
        bad["bypassed_plan_gate"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "t3-execution-run.schema.json")

    def test_refuse_without_fixture_allow_when_plan_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"COMPASS_T3_EXEC_ENABLED": "1"}):
                with self.assertRaises(T3ServiceError):
                    start_execution(
                        Path(tmp),
                        plan_id="i2-t3-execution-adapter",
                        objective="no plan file",
                    )


class OverseerTests(unittest.TestCase):
    def test_drift_sees_t3_executions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            for name in (
                "VERSION",
                "PROGRESS.md",
                "PROJECT_CONTEXT.md",
                "DECISIONS.md",
                "TESTING.md",
            ):
                (repo / name).write_text("x\n", encoding="utf-8")
            (repo / "IMPLEMENTATION_PLAN.md").write_text(
                "- Status: **APPROVED**\n\n"
                "| Field | Value |\n|---|---|\n"
                "| Plan ID | `i2-t3-execution-adapter` |\n",
                encoding="utf-8",
            )
            (repo / ".cursor" / "skills").mkdir(parents=True)
            with mock.patch.dict(os.environ, {"COMPASS_T3_EXEC_ENABLED": "1"}):
                start_execution(
                    repo,
                    plan_id="i2-t3-execution-adapter",
                    objective="overseer visibility",
                    allow_fixture_plan=True,
                )
            kinds = {f.get("kind") for f in detect_drift(repo)["findings"]}
            self.assertIn("t3_execution_evidence", kinds)


class CliTests(unittest.TestCase):
    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_T3_EXEC_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-t3-exec.sh"), "list", "--repo-root", str(ROOT)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_T3_EXEC_ENABLED", proc.stderr)


if __name__ == "__main__":
    unittest.main()
