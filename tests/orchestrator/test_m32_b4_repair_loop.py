"""Tests for B4 repair loop (M32)."""

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

    def test_captain_authorized_fix_prepares_submit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = start_repair(
                repo_root=Path(tmp),
                report_path=FIXTURE,
                finding_id="sec-hardcoded-key",
                allowlist_path=ALLOWLIST,
                captain_authorized_fix=True,
                run_id="repair-authorized",
            )
            self.assertEqual(result["stage"], "fix_authorized_prepare_submit")
            self.assertTrue(result["submit"]["prepared"])
            self.assertFalse(result["submit"]["auto_merge"])


if __name__ == "__main__":
    unittest.main()
