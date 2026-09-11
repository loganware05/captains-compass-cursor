"""M24 Linear Skills Learning Loop ledger + northstar launcher."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.integrations.skills_ledger import (
    SkillsLedgerError,
    build_ledger_for_run,
    empty_ledger,
    sync_learning_run_ledger,
)

ROOT = Path(__file__).resolve().parents[2]
NORTHSTAR = ROOT / "scripts" / "northstar"


class M24EmptyLedgerTests(unittest.TestCase):
    def test_empty_ledger_authoritative_approval_false(self) -> None:
        ledger = empty_ledger()
        self.assertIs(ledger["authoritative_approval"], False)
        self.assertEqual(ledger["provider"], "linear")
        self.assertIsNone(ledger["parent_issue_id"])

    def test_build_ledger_for_run_forces_authoritative_approval_false(self) -> None:
        report = {
            "run_id": "test-run",
            "ledger": {"authoritative_approval": True, "parent_issue_id": "OVA-5"},
        }
        ledger = build_ledger_for_run(report)
        self.assertIs(ledger["authoritative_approval"], False)
        self.assertEqual(ledger["parent_issue_id"], "OVA-5")


class M24SyncLedgerTests(unittest.TestCase):
    def test_fixtures_sync_writes_placeholder_parent_and_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_path = Path(tmp) / "run-abc.json"
            run_path.write_text(
                json.dumps({"run_id": "run-abc", "approved_for_execution": False}) + "\n",
                encoding="utf-8",
            )
            report = sync_learning_run_ledger(run_path, mode="fixtures")
            self.assertEqual(report["ledger"]["parent_issue_id"], "fixture-parent-run-abc")
            self.assertIs(report["ledger"]["authoritative_approval"], False)
            sibling = run_path.with_name("run-abc.ledger.json")
            self.assertTrue(sibling.is_file())
            sibling_data = json.loads(sibling.read_text(encoding="utf-8"))
            self.assertEqual(sibling_data["parent_issue_id"], "fixture-parent-run-abc")
            on_disk = json.loads(run_path.read_text(encoding="utf-8"))
            self.assertIn("ledger", on_disk)

    def test_link_mode_requires_parent_issue_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_path = Path(tmp) / "run.json"
            run_path.write_text(json.dumps({"run_id": "r1"}) + "\n", encoding="utf-8")
            with self.assertRaises(SkillsLedgerError) as ctx:
                sync_learning_run_ledger(run_path, mode="link")
            self.assertIn("parent-issue-id", str(ctx.exception))

    def test_link_mode_allowlists_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_path = Path(tmp) / "run.json"
            run_path.write_text(json.dumps({"run_id": "r1"}) + "\n", encoding="utf-8")
            with self.assertRaises(SkillsLedgerError) as ctx:
                sync_learning_run_ledger(
                    run_path,
                    mode="link",
                    parent_issue_id="OVA-5",
                    project_id="not-allowlisted-project",
                    project_name="Evil Project",
                )
            self.assertIn("allowlisted", str(ctx.exception))

            report = sync_learning_run_ledger(
                run_path,
                mode="link",
                parent_issue_id="OVA-5",
                project_id="c62f65bf-a376-4716-b958-0d874730a391",
                project_name="NorthStar Skills Learning Loop",
            )
            self.assertEqual(report["ledger"]["parent_issue_id"], "OVA-5")
            self.assertEqual(
                report["ledger"]["project_id"],
                "c62f65bf-a376-4716-b958-0d874730a391",
            )

    def test_refuses_approved_for_execution_true(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_path = Path(tmp) / "run.json"
            run_path.write_text(
                json.dumps({"run_id": "r1", "approved_for_execution": True}) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(SkillsLedgerError) as ctx:
                sync_learning_run_ledger(run_path, mode="fixtures")
            self.assertIn("approved_for_execution", str(ctx.exception))


class M24NorthstarLauncherTests(unittest.TestCase):
    def test_northstar_help_exits_zero(self) -> None:
        self.assertTrue(NORTHSTAR.is_file())
        proc = subprocess.run(
            [str(NORTHSTAR), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("northstar skills", proc.stdout.lower() + proc.stderr.lower())

    def test_northstar_skills_learn_without_repo_exits_nonzero(self) -> None:
        proc = subprocess.run(
            [str(NORTHSTAR), "skills", "learn", "--objective", "x"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        combined = proc.stdout + proc.stderr
        self.assertIn("--repo", combined)


if __name__ == "__main__":
    unittest.main()
