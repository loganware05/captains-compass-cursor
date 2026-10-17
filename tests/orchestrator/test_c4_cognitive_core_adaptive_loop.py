"""C4 Cognitive Core — Adaptive Development Loop tests."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-c4-tests"

from orchestrator.cycle.enabled import cycle_enabled, require_cycle_enabled
from orchestrator.cycle.service import (
    CycleServiceError,
    cycle_begin,
    cycle_checkpoint,
    cycle_close,
    learning_review,
)
from orchestrator.schemas.validate import ValidationError, validate_document


def _mk_tmp(prefix: str) -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(_FIXTURE_ROOT)))


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_CYCLE_ENABLED", None)
            self.assertFalse(cycle_enabled())
            with self.assertRaises(PermissionError):
                require_cycle_enabled()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_CYCLE_ENABLED": "1"}):
            self.assertTrue(cycle_enabled())


class SchemaTests(unittest.TestCase):
    def test_cycle_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "execution_id": "cycle-test",
            "phase": "begun",
            "status": "active",
            "objective": "x",
            "plan_id": "p",
            "checkpoints": [],
            "draft_proposals": [],
            "citations": [],
            "approved_for_execution": False,
            "authority_mutation": False,
            "created_at": "2026-10-17T00:00:00Z",
            "updated_at": "2026-10-17T00:00:00Z",
        }
        validate_document(doc, "cycle-state.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "cycle-state.schema.json")

    def test_learning_review_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "review_id": "learning-review-test",
            "cycles_scanned": 0,
            "open_proposals": [],
            "citations": [],
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": "2026-10-17T00:00:00Z",
        }
        validate_document(doc, "learning-review.schema.json")
        bad = dict(doc)
        bad["authority_mutation"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "learning-review.schema.json")


class LifecycleTests(unittest.TestCase):
    def test_begin_requires_assess_flag(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"COMPASS_CYCLE_ENABLED": "1"},
            clear=False,
        ):
            os.environ.pop("COMPASS_ASSESS_ENABLED", None)
            with self.assertRaises(CycleServiceError):
                cycle_begin(ROOT, "Add gated cycle begin for adaptive loop")

    def test_full_lifecycle(self) -> None:
        tmp = _mk_tmp("c4-life-")
        # Use control ROOT for assess (Skills/registry) but store cycle under tmp
        # by pointing repo_root to a hybrid: symlink key dirs is heavy — use ROOT
        # and write into ROOT/.agent/cycles then clean via unique execution id.
        with mock.patch.dict(
            os.environ,
            {"COMPASS_CYCLE_ENABLED": "1", "COMPASS_ASSESS_ENABLED": "1"},
        ):
            begun = cycle_begin(
                ROOT,
                "Add hermetic adaptive cycle controller for Cognitive Core C4",
                plan_id="c4-cognitive-core-adaptive-loop",
            )
            self.assertEqual(begun["phase"], "begun")
            self.assertEqual(begun["status"], "active")
            self.assertFalse(begun["approved_for_execution"])
            self.assertFalse(begun["authority_mutation"])
            self.assertFalse(begun["remaining_work_forecast"]["scope_expanded"])
            self.assertIn("assessment", begun)
            self.assertTrue(begun["assessment"]["assessment_id"])
            exec_id = begun["execution_id"]

            cp1 = cycle_checkpoint(
                ROOT,
                exec_id,
                checkpoint_key="impl-1",
                outcome="in_progress",
                retries=1,
                skills=["implementation-planning"],
            )
            self.assertEqual(cp1["phase"], "checkpointed")
            self.assertEqual(len(cp1["checkpoints"]), 1)

            # Idempotent checkpoint
            cp2 = cycle_checkpoint(
                ROOT,
                exec_id,
                checkpoint_key="impl-1",
                outcome="failed",
                retries=9,
            )
            self.assertEqual(len(cp2["checkpoints"]), 1)
            self.assertEqual(cp2["checkpoints"][0]["retries"], 1)

            closed = cycle_close(ROOT, exec_id, outcome="success")
            self.assertEqual(closed["phase"], "closed")
            self.assertEqual(closed["status"], "closed")
            self.assertTrue(closed["execution_run_id"])
            self.assertTrue(closed["experience_id"])
            self.assertTrue(closed["draft_proposals"])
            for draft in closed["draft_proposals"]:
                self.assertFalse(draft["auto_promoted"])

            # Idempotent close
            closed2 = cycle_close(ROOT, exec_id, outcome="failed")
            self.assertEqual(closed2["execution_run_id"], closed["execution_run_id"])

            review = learning_review(ROOT)
            self.assertFalse(review["approved_for_execution"])
            self.assertFalse(review["authority_mutation"])
            self.assertGreaterEqual(review["cycles_scanned"], 1)
            kinds = {p["kind"] for p in review["open_proposals"]}
            self.assertIn("learning_review", kinds)

        # Cleanup cycle artifact written under control repo
        cycle_path = ROOT / ".agent" / "cycles" / f"{exec_id}.json"
        if cycle_path.is_file():
            cycle_path.unlink()
        # leave runs/experience gitignored
        _ = tmp


class CliTests(unittest.TestCase):
    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_CYCLE_ENABLED", None)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-cycle.sh"), "review", "--repo-root", str(ROOT)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_CYCLE_ENABLED", proc.stderr)

    def test_cli_lifecycle_smoke(self) -> None:
        env = os.environ.copy()
        env["COMPASS_CYCLE_ENABLED"] = "1"
        env["COMPASS_ASSESS_ENABLED"] = "1"
        begin = subprocess.run(
            [
                str(ROOT / "scripts" / "northstar"),
                "cycle",
                "begin",
                "--objective",
                "CLI smoke adaptive cycle for C4",
                "--plan-id",
                "c4-cli-smoke",
                "--repo",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(begin.returncode, 0, begin.stderr)
        payload = json.loads(begin.stdout)
        exec_id = payload["execution_id"]
        try:
            cp = subprocess.run(
                [
                    str(ROOT / "scripts" / "northstar"),
                    "cycle",
                    "checkpoint",
                    "--execution-id",
                    exec_id,
                    "--checkpoint-key",
                    "cli-1",
                    "--repo",
                    str(ROOT),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(cp.returncode, 0, cp.stderr)
            close = subprocess.run(
                [
                    str(ROOT / "scripts" / "northstar"),
                    "cycle",
                    "close",
                    "--execution-id",
                    exec_id,
                    "--outcome",
                    "success",
                    "--repo",
                    str(ROOT),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(close.returncode, 0, close.stderr)
            closed = json.loads(close.stdout)
            self.assertEqual(closed["status"], "closed")
            review = subprocess.run(
                [
                    str(ROOT / "scripts" / "northstar"),
                    "learning",
                    "review",
                    "--repo",
                    str(ROOT),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(review.returncode, 0, review.stderr)
            packet = json.loads(review.stdout)
            self.assertFalse(packet["authority_mutation"])
        finally:
            path = ROOT / ".agent" / "cycles" / f"{exec_id}.json"
            if path.is_file():
                path.unlink()


if __name__ == "__main__":
    unittest.main()
