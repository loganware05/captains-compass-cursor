"""M44 DecisionProvider review triage shadow — hermetic tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.providers.decision.change_state import build_review_change_summary
from orchestrator.providers.decision.file_provider import (
    FileDecisionProvider,
    decision_review_shadow_enabled,
)
from orchestrator.providers.decision.review_shadow import (
    EVIDENCE_ROOT_REL,
    maybe_run_review_triage_shadow,
)
from orchestrator.providers.decision.types import ReviewTriageRequest
from orchestrator.review.pipeline import run_code_review

ROOT = Path(__file__).resolve().parents[2]


class ReviewShadowEnvTests(unittest.TestCase):
    def test_default_off(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_DECISION_REVIEW_SHADOW", None)
            self.assertFalse(decision_review_shadow_enabled())


class ChangeStateTests(unittest.TestCase):
    def test_path_flags_auth(self) -> None:
        summary, digest, state = build_review_change_summary(
            changed_paths=["src/auth/session.ts", "README.md"],
            domains=["security"],
            specialist_skill_ids=["security-review"],
            candidate_count=2,
            objective="Harden session tokens",
        )
        self.assertTrue(summary.path_flags["touches_authz"])
        self.assertTrue(digest)
        self.assertIn("change", state)


class FileTriageTests(unittest.TestCase):
    def test_auth_fixture(self) -> None:
        provider = FileDecisionProvider()
        summary, digest, _ = build_review_change_summary(
            changed_paths=["apps/api/auth/login.ts"],
            domains=["security"],
        )
        result = provider.triage_review(
            ReviewTriageRequest(change=summary, change_hash=digest)
        )
        self.assertFalse(result.abstain)
        self.assertEqual(result.investigation_priority, "high")
        self.assertEqual(result.specialist_security_warranted, "yes")

    def test_docs_fixture(self) -> None:
        provider = FileDecisionProvider()
        summary, digest, _ = build_review_change_summary(
            changed_paths=["docs/README.md"],
            domains=["general"],
        )
        result = provider.triage_review(
            ReviewTriageRequest(change=summary, change_hash=digest)
        )
        self.assertFalse(result.abstain)
        self.assertEqual(result.investigation_priority, "low")
        self.assertEqual(result.specialist_security_warranted, "no")


class ReviewShadowIntegrationTests(unittest.TestCase):
    def test_shadow_writes_evidence_without_mutating_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            env = {
                "COMPASS_DECISION_PROVIDER": "file",
                "COMPASS_DECISION_REVIEW_SHADOW": "1",
            }
            with mock.patch.dict(os.environ, env):
                ref = maybe_run_review_triage_shadow(
                    repo,
                    changed_paths=["src/auth/tokens.py"],
                    domains=["security"],
                    specialist_skill_ids=["security-review"],
                    candidate_count=3,
                    plan_id="m44-test",
                )
            self.assertIsNotNone(ref)
            assert ref is not None
            self.assertFalse(ref["applied"])
            evidence = repo / ref["evidence_path"]
            self.assertTrue(evidence.is_file())
            self.assertTrue(str(ref["evidence_path"]).startswith(str(EVIDENCE_ROOT_REL)))
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "northstar.decision_review_triage.v1")
            self.assertFalse(payload["applied"])

    def test_pipeline_default_unchanged_and_no_triage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
            subprocess_init = __import__("subprocess").run
            subprocess_init(
                ["git", "init"],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            subprocess_init(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            subprocess_init(
                ["git", "config", "user.name", "test"],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            subprocess_init(
                ["git", "add", "."],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            subprocess_init(
                ["git", "commit", "-m", "init"],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            with mock.patch.dict(
                os.environ,
                {
                    "COMPASS_DECISION_PROVIDER": "stub",
                    "COMPASS_DECISION_REVIEW_SHADOW": "",
                },
                clear=False,
            ):
                os.environ.pop("COMPASS_DECISION_REVIEW_SHADOW", None)
                first = run_code_review(
                    repo_root=repo,
                    diff_text="+print('hi')\n",
                    changed_paths=["src/app.py"],
                    candidates_mode="heuristics",
                    boundary_check=False,
                )
                second = run_code_review(
                    repo_root=repo,
                    diff_text="+print('hi')\n",
                    changed_paths=["src/app.py"],
                    candidates_mode="heuristics",
                    boundary_check=False,
                )
            self.assertIsNone(first.get("decision_review_triage"))
            self.assertEqual(first["findings"], second["findings"])

    def test_pipeline_shadow_does_not_change_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "auth.py").write_text("TOKEN = 'x'\n", encoding="utf-8")
            diff = "diff --git a/src/auth.py b/src/auth.py\n+TOKEN = 'x'\n"
            with mock.patch.dict(
                os.environ,
                {
                    "COMPASS_DECISION_PROVIDER": "stub",
                    "COMPASS_DECISION_REVIEW_SHADOW": "",
                },
                clear=False,
            ):
                os.environ.pop("COMPASS_DECISION_REVIEW_SHADOW", None)
                baseline = run_code_review(
                    repo_root=repo,
                    diff_text=diff,
                    changed_paths=["src/auth.py"],
                    candidates_mode="heuristics",
                    boundary_check=False,
                )
            baseline_findings = list(baseline["findings"])
            with mock.patch.dict(
                os.environ,
                {
                    "COMPASS_DECISION_PROVIDER": "file",
                    "COMPASS_DECISION_REVIEW_SHADOW": "1",
                },
            ):
                shadowed = run_code_review(
                    repo_root=repo,
                    diff_text=diff,
                    changed_paths=["src/auth.py"],
                    candidates_mode="heuristics",
                    boundary_check=False,
                    plan_id="m44-pipeline",
                )
            self.assertEqual(shadowed["findings"], baseline_findings)
            self.assertIsNotNone(shadowed.get("decision_review_triage"))
            assert shadowed["decision_review_triage"] is not None
            self.assertFalse(shadowed["decision_review_triage"].get("applied"))
            evidence = repo / shadowed["decision_review_triage"]["evidence_path"]
            self.assertTrue(evidence.is_file())


class CiReviewShadowUnsetTests(unittest.TestCase):
    def test_ci_workflow_does_not_enable_review_shadow(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertNotIn("COMPASS_DECISION_REVIEW_SHADOW", workflow)


if __name__ == "__main__":
    unittest.main()
