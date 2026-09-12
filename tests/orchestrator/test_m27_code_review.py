"""M27 NorthStar Code Reviewer — hermetic pipeline tests."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.review.detect import detect, parse_changed_paths_from_diff
from orchestrator.review.investigate import investigate
from orchestrator.review.pipeline import ReviewError, run_code_review
from orchestrator.review.verify import verify_findings
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "code-review"


class DetectTests(unittest.TestCase):
    def test_parse_paths_and_domains(self) -> None:
        diff = (FIXTURES / "sample.diff").read_text(encoding="utf-8")
        paths = parse_changed_paths_from_diff(diff)
        self.assertEqual(paths, ["src/auth/session.py"])
        detection = detect(
            repo_root=ROOT,
            changed_paths=paths,
            diff_text=diff,
            plan_path=FIXTURES / "plan.md",
        )
        self.assertIn("python", detection["domains"])
        self.assertIn("security", detection["domains"])
        self.assertGreaterEqual(len(detection["intent"]["acceptance_criteria"]), 1)
        self.assertIn("code-reviewer", detection["skills_suggested"])


class VerifyTests(unittest.TestCase):
    def test_verify_discards_noise_and_keeps_high_signal(self) -> None:
        candidates = json.loads((FIXTURES / "candidates.json").read_text(encoding="utf-8"))[
            "findings"
        ]
        findings = verify_findings(candidates)
        by_id = {f["id"]: f for f in findings}
        self.assertEqual(by_id["sec-hardcoded-key"]["status"], "verified")
        self.assertEqual(by_id["intent-ac-check"]["status"], "unverified")
        self.assertEqual(by_id["noise-naming"]["status"], "discarded")


class PipelineTests(unittest.TestCase):
    def test_fixture_pipeline_writes_schema_valid_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            session = repo / "src" / "auth" / "session.py"
            session.parent.mkdir(parents=True)
            session.write_text(
                "def create_session(user_id: str) -> dict:\n    return {}\n",
                encoding="utf-8",
            )
            plan = repo / "IMPLEMENTATION_PLAN.md"
            plan.write_text((FIXTURES / "plan.md").read_text(encoding="utf-8"), encoding="utf-8")
            result = run_code_review(
                repo_root=repo,
                run_id="fixture-m27",
                diff_file=FIXTURES / "sample.diff",
                changed_paths=["src/auth/session.py"],
                plan_path=plan,
                candidates_path=FIXTURES / "candidates.json",
                plan_id="m27-northstar-code-reviewer",
            )
            report = result["report"]
            validate_document(report, "code-review-report.schema.json")
            self.assertFalse(report["provenance"]["github_review_posted"])
            self.assertTrue(report["provenance"]["hermetic"])
            self.assertEqual(report["summary"]["verified"], 1)
            self.assertEqual(report["summary"]["discarded"], 1)
            report_path = Path(result["report_path"])
            self.assertTrue(report_path.is_file())
            self.assertTrue((report_path.parent / "report.md").is_file())
            self.assertTrue((report_path.parent / "context-pack.json").is_file())

    def test_non_hermetic_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "a.py").write_text("x=1\n", encoding="utf-8")
            with self.assertRaises(ReviewError):
                run_code_review(
                    repo_root=repo,
                    run_id="nope",
                    changed_paths=["a.py"],
                    hermetic=False,
                )

    def test_investigate_includes_neighbors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "svc" / "auth.py"
            target.parent.mkdir(parents=True)
            target.write_text("TOKEN='plain'\n", encoding="utf-8")
            neighbor = repo / "svc" / "config.py"
            neighbor.write_text("password = 'supersecretvalue'\n", encoding="utf-8")
            detection = detect(repo_root=repo, changed_paths=["svc/auth.py"])
            pack = investigate(repo_root=repo, detection=detection, diff_text="")
            self.assertIn("svc/config.py", pack.get("related_paths") or [])


class CliTests(unittest.TestCase):
    def test_run_code_review_cli(self) -> None:
        script = ROOT / "scripts" / "run-code-review.sh"
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = repo / "src" / "auth" / "session.py"
            path.parent.mkdir(parents=True)
            path.write_text(
                "def create_session(user_id: str) -> dict:\n    return {}\n",
                encoding="utf-8",
            )
            plan = repo / "IMPLEMENTATION_PLAN.md"
            plan.write_text((FIXTURES / "plan.md").read_text(encoding="utf-8"), encoding="utf-8")
            proc = subprocess.run(
                [
                    str(script),
                    "--repo-root",
                    str(repo),
                    "--diff-file",
                    str(FIXTURES / "sample.diff"),
                    "--candidates",
                    str(FIXTURES / "candidates.json"),
                    "--plan",
                    str(plan),
                    "--run-id",
                    "cli-m27",
                    "--changed",
                    "src/auth/session.py",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["run_id"], "cli-m27")
            self.assertFalse(payload["github_review_posted"])


if __name__ == "__main__":
    unittest.main()
