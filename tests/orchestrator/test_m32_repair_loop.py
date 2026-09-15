"""M32 / B4 repair loop tests — hermetic FIND→PROVE→SUBMIT metadata."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.repair import RepairError, prove_finding, start_repair

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "repair"
SAMPLE_REPORT = (
    ROOT
    / ".agent"
    / "evidence"
    / "m28-reviewer-specialist-composition"
    / "bitcoin-style-demo"
    / "report.json"
)


class ProveTests(unittest.TestCase):
    def test_verified_high_passes(self) -> None:
        report = json.loads(SAMPLE_REPORT.read_text(encoding="utf-8"))
        finding = next(f for f in report["findings"] if f["id"] == "sec-secret-in-diff")
        result = prove_finding(finding, severity_floor="medium")
        self.assertTrue(result["ok"])

    def test_discarded_refused(self) -> None:
        report = json.loads(SAMPLE_REPORT.read_text(encoding="utf-8"))
        finding = next(f for f in report["findings"] if f["id"] == "noise-style-nit")
        result = prove_finding(finding, severity_floor="medium")
        self.assertFalse(result["ok"])

    def test_below_floor_refused(self) -> None:
        finding = {
            "id": "x",
            "status": "verified",
            "severity": "low",
            "evidence_paths": ["a.py"],
        }
        result = prove_finding(finding, severity_floor="medium")
        self.assertFalse(result["ok"])


class StartRepairTests(unittest.TestCase):
    def test_dry_run_writes_evidence_never_merges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report_dst = (
                repo
                / ".agent"
                / "evidence"
                / "code-review"
                / "m28-bitcoin-style-demo"
                / "report.json"
            )
            report_dst.parent.mkdir(parents=True)
            shutil.copy(SAMPLE_REPORT, report_dst)
            result = start_repair(
                repo_root=repo,
                report_path=report_dst,
                finding_id="sec-secret-in-diff",
                target_repository="loganware05/captain-compass-sandbox",
                registry_path=FIXTURES / "agent-registry.json",
                captain_approve_dispatch=True,
                prepare_pr=True,
            )
            self.assertTrue(result["ok"])
            self.assertFalse(result["merged"])
            self.assertFalse(result["auto_merge"])
            self.assertFalse(result["pr_created"])
            self.assertTrue(result["dispatch_authorized"])
            evidence = Path(result["evidence_dir"])
            for name in (
                "intake.json",
                "prove.json",
                "objective.json",
                "dispatch-packet.json",
                "fix-plan.json",
                "test-plan.json",
                "pr-metadata.json",
                "result.json",
                "SUMMARY.md",
            ):
                self.assertTrue((evidence / name).is_file(), name)
            pr_meta = json.loads((evidence / "pr-metadata.json").read_text(encoding="utf-8"))
            self.assertIs(pr_meta["auto_merge"], False)
            self.assertIs(pr_meta["merged"], False)
            self.assertIs(pr_meta["draft"], True)
            packet = json.loads((evidence / "dispatch-packet.json").read_text(encoding="utf-8"))
            self.assertIs(packet["live_dispatch_invoked"], False)

    def test_unverified_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report_dst = repo / "report.json"
            shutil.copy(SAMPLE_REPORT, report_dst)
            with self.assertRaises(RepairError):
                start_repair(
                    repo_root=repo,
                    report_path=report_dst,
                    finding_id="noise-style-nit",
                )

    def test_prepare_pr_refuses_non_allowlisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report_dst = repo / "report.json"
            shutil.copy(SAMPLE_REPORT, report_dst)
            with self.assertRaises(RepairError):
                start_repair(
                    repo_root=repo,
                    report_path=report_dst,
                    finding_id="sec-secret-in-diff",
                    target_repository="someone/not-allowlisted",
                    prepare_pr=True,
                )

    def test_cli_repair_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report_dst = repo / "report.json"
            shutil.copy(SAMPLE_REPORT, report_dst)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-repair.sh"),
                    "--repo-root",
                    str(repo),
                    "--report",
                    str(report_dst),
                    "--finding-id",
                    "sec-secret-in-diff",
                    "--target-repository",
                    "loganware05/captain-compass-sandbox",
                    "--registry",
                    str(FIXTURES / "agent-registry.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["merged"])
            self.assertFalse(payload["dispatch_authorized"])  # no captain flag


if __name__ == "__main__":
    unittest.main()
