"""Tests for B4 repair loop (M32 + supervised FIX→SUBMIT)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.repair.loop import RepairError, start_repair

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "repair" / "sandbox-report.json"
ALLOWLIST = ROOT / "templates" / "agent" / "review" / "github-allowlist.yml"


class RepairLoopTests(unittest.TestCase):
    def test_start_repair_packet_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = start_repair(
                repo_root=repo,
                report_path=FIXTURE,
                finding_id="sec-hardcoded-key",
                allowlist_path=ALLOWLIST,
                run_id="repair-sec-hardcoded-key",
            )
            self.assertEqual(result["stage"], "packet_ready")
            self.assertFalse(result["locks"]["captain_fix_authorized"])
            self.assertFalse(result["submit"]["auto_merge"])
            self.assertFalse(result["submit"]["prepared"])
            evidence = repo / ".agent" / "evidence" / "repair" / "repair-sec-hardcoded-key"
            self.assertTrue((evidence / "repair-run.json").is_file())
            self.assertTrue((evidence / "dispatch-packet.json").is_file())

    def test_refuse_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RepairError):
                start_repair(
                    repo_root=Path(tmp),
                    report_path=FIXTURE,
                    finding_id="intent-ac-check",
                    allowlist_path=ALLOWLIST,
                )

    def test_refuse_non_allowlisted_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RepairError):
                start_repair(
                    repo_root=Path(tmp),
                    report_path=FIXTURE,
                    finding_id="sec-hardcoded-key",
                    allowlist_path=ALLOWLIST,
                    repository_override="acme/not-allowlisted",
                )

    def test_captain_authorized_reaches_submit_prepared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = start_repair(
                repo_root=repo,
                report_path=FIXTURE,
                finding_id="sec-hardcoded-key",
                allowlist_path=ALLOWLIST,
                captain_authorized_fix=True,
                run_id="repair-authorized",
            )
            self.assertEqual(result["stage"], "submit_prepared")
            self.assertTrue(result["submit"]["prepared"])
            self.assertFalse(result["submit"]["auto_merge"])
            self.assertIsNotNone(result["fix"])
            self.assertIs(result["fix"]["applied"], False)
            self.assertIsNotNone(result["test"])
            self.assertEqual(result["test"]["status"], "recorded")
            helper = result["submit"]["draft_pr"]["helper"]
            self.assertEqual(helper["argv"][0], "gh")
            self.assertIn("--draft", helper["argv"])
            self.assertFalse(result["submit"]["draft_pr"]["opened"])
            self.assertIs(result["locks"]["auto_promoted"], False)
            evidence = repo / ".agent" / "evidence" / "repair" / "repair-authorized"
            self.assertTrue((evidence / "fix-record.json").is_file())
            self.assertTrue((evidence / "test-record.json").is_file())
            self.assertTrue((evidence / "draft-pr-helper.json").is_file())

    def test_unauthorized_cannot_open_draft_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RepairError) as ctx:
                start_repair(
                    repo_root=Path(tmp),
                    report_path=FIXTURE,
                    finding_id="sec-hardcoded-key",
                    allowlist_path=ALLOWLIST,
                    captain_authorized_fix=False,
                    open_draft_pr=True,
                )
            self.assertIn("requires --captain-authorized-fix", str(ctx.exception))

    def test_open_draft_pr_flag_requests_helper_without_execute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = start_repair(
                repo_root=Path(tmp),
                report_path=FIXTURE,
                finding_id="sec-hardcoded-key",
                allowlist_path=ALLOWLIST,
                captain_authorized_fix=True,
                open_draft_pr=True,
                run_id="repair-draft-requested",
            )
            self.assertEqual(result["stage"], "submit_prepared")
            self.assertTrue(result["submit"]["draft_pr"]["requested"])
            self.assertFalse(result["submit"]["draft_pr"]["opened"])
            self.assertFalse(result["submit"]["draft_pr"].get("executed", False))
            self.assertFalse(result["submit"]["auto_merge"])


if __name__ == "__main__":
    unittest.main()
