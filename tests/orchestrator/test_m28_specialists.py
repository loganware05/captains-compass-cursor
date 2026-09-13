"""M28 NorthStar Code Reviewer — specialist composition tests."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.review.pipeline import ReviewError, run_code_review
from orchestrator.review.specialists import (
    compose_specialist_candidates,
    emit_adversarial_candidates,
    emit_security_candidates,
    emit_testing_candidates,
)
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "code-review"


class SpecialistEmitterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.diff = (FIXTURES / "sample.diff").read_text(encoding="utf-8")
        self.detection = {
            "changed_paths": ["src/auth/session.py"],
            "domains": ["python", "security"],
            "intent": {
                "non_goals": ["github review posting"],
                "acceptance_criteria": ["Keep reviews hermetic"],
                "plan_path": "IMPLEMENTATION_PLAN.md",
                "excerpt": "Compose specialists without model calls.",
            },
        }
        self.pack = {"diff": self.diff}

    def test_security_emits_secret_finding(self) -> None:
        findings = emit_security_candidates(
            detection=self.detection, context_pack=self.pack
        )
        ids = {f["id"] for f in findings}
        self.assertIn("sec-secret-in-diff", ids)
        self.assertIn("sec-auth-without-tests", ids)

    def test_testing_emits_missing_coverage(self) -> None:
        findings = emit_testing_candidates(
            detection=self.detection, context_pack=self.pack
        )
        self.assertIn("test-missing-for-prod-change", {f["id"] for f in findings})

    def test_adversarial_weak_test(self) -> None:
        pack = {"diff": "def test_ok():\n    assert True\n"}
        detection = {
            "changed_paths": ["tests/test_session.py"],
            "domains": ["python", "tests"],
            "intent": {"non_goals": [], "excerpt": ""},
        }
        findings = emit_adversarial_candidates(detection=detection, context_pack=pack)
        self.assertIn("adv-weak-test", {f["id"] for f in findings})

    def test_compose_dedupes_and_reports_source(self) -> None:
        candidates, skills, source = compose_specialist_candidates(
            detection=self.detection,
            context_pack=self.pack,
            include_heuristics=True,
        )
        self.assertEqual(source, "specialists+heuristics")
        self.assertIn("security-review", skills)
        ids = [c["id"] for c in candidates]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("noise-style-nit", ids)


class SpecialistPipelineTests(unittest.TestCase):
    def test_default_mode_is_specialists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            session = repo / "src" / "auth" / "session.py"
            session.parent.mkdir(parents=True)
            session.write_text(
                "def create_session(user_id: str) -> dict:\n    return {}\n",
                encoding="utf-8",
            )
            plan = repo / "IMPLEMENTATION_PLAN.md"
            plan.write_text(
                (FIXTURES / "plan.md").read_text(encoding="utf-8"), encoding="utf-8"
            )
            result = run_code_review(
                repo_root=repo,
                run_id="fixture-m28-specialists",
                diff_file=FIXTURES / "sample.diff",
                changed_paths=["src/auth/session.py"],
                plan_path=plan,
                plan_id="m28-reviewer-specialist-composition",
            )
            report = result["report"]
            validate_document(report, "code-review-report.schema.json")
            self.assertEqual(report["provenance"]["candidates_source"], "specialists")
            self.assertFalse(report["provenance"]["github_review_posted"])
            self.assertTrue(report["provenance"]["hermetic"])
            self.assertEqual(result["candidates_source"], "specialists")
            by_id = {f["id"]: f for f in result["findings"]}
            self.assertEqual(by_id["sec-secret-in-diff"]["status"], "verified")
            self.assertEqual(by_id["noise-style-nit"]["status"], "discarded")
            self.assertIn("security-review", report["summary"]["skills_invoked"])

    def test_heuristics_mode_escape_hatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "a.py").write_text("x=1\n", encoding="utf-8")
            result = run_code_review(
                repo_root=repo,
                run_id="fixture-m28-heuristics",
                changed_paths=["a.py"],
                diff_text="diff --git a/a.py b/a.py\n+x=1\n",
                candidates_mode="heuristics",
            )
            self.assertEqual(result["candidates_source"], "heuristics")

    def test_invalid_mode_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "a.py").write_text("x=1\n", encoding="utf-8")
            with self.assertRaises(ReviewError):
                run_code_review(
                    repo_root=repo,
                    run_id="bad-mode",
                    changed_paths=["a.py"],
                    candidates_mode="models",
                )

    def test_cli_specialists_mode(self) -> None:
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
            plan.write_text(
                (FIXTURES / "plan.md").read_text(encoding="utf-8"), encoding="utf-8"
            )
            proc = subprocess.run(
                [
                    str(script),
                    "--repo-root",
                    str(repo),
                    "--diff-file",
                    str(FIXTURES / "sample.diff"),
                    "--plan",
                    str(plan),
                    "--run-id",
                    "cli-m28",
                    "--changed",
                    "src/auth/session.py",
                    "--candidates-mode",
                    "specialists",
                    "--plan-id",
                    "m28-reviewer-specialist-composition",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["run_id"], "cli-m28")
            self.assertEqual(payload["candidates_source"], "specialists")
            self.assertFalse(payload["github_review_posted"])


if __name__ == "__main__":
    unittest.main()
