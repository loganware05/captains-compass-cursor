"""M9 skill promotion lifecycle + Artifact Context tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections
from orchestrator.promotion.advance import (
    PromotionError,
    advance_lifecycle,
    count_successful_experiences_for_skill,
    load_candidate_json,
    write_available_skill_proposal,
    write_staging_candidate,
)
from orchestrator.telemetry.store import write_experience

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_CANDIDATE = (
    ROOT
    / "orchestrator"
    / "providers"
    / "technology_intelligence"
    / "fixtures"
    / "stars-redacted-accessible-forms.json"
)


def _sandbox_candidate() -> dict:
    candidate = load_candidate_json(FIXTURE_CANDIDATE)
    analyzed = advance_lifecycle(candidate, target_stage="ANALYZED")
    secured = advance_lifecycle(
        analyzed,
        target_stage="SECURITY_REVIEWED",
        evidence_paths=[".agent/evidence/security.md"],
    )
    return advance_lifecycle(
        secured,
        target_stage="SANDBOX_TESTED",
        evidence_paths=[".agent/evidence/sandbox.md"],
    )


class M9PromotionTests(unittest.TestCase):
    def test_approved_requires_captain_flag(self) -> None:
        sandbox = _sandbox_candidate()
        with self.assertRaises(PromotionError):
            advance_lifecycle(
                sandbox,
                target_stage="APPROVED",
                evidence_paths=[".agent/evidence/approval.md"],
            )

    def test_approved_with_captain_flag(self) -> None:
        sandbox = _sandbox_candidate()
        approved = advance_lifecycle(
            sandbox,
            target_stage="APPROVED",
            evidence_paths=[".agent/evidence/approval.md"],
            captain_approved=True,
            skill_slug="demo-skill",
        )
        self.assertEqual(approved["lifecycle_stage"], "APPROVED")
        self.assertTrue(approved.get("captain_approved"))
        self.assertFalse(approved["approved_for_execution"])

    def test_available_skill_proposal_not_under_cursor_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sandbox = _sandbox_candidate()
            approved = advance_lifecycle(
                sandbox,
                target_stage="APPROVED",
                evidence_paths=[".agent/evidence/a.md"],
                captain_approved=True,
                skill_slug="demo-skill",
            )
            available = advance_lifecycle(
                approved,
                target_stage="AVAILABLE_SKILL",
                evidence_paths=[".agent/evidence/a.md"],
                captain_approved=True,
                skill_slug="demo-skill",
                repo_root=repo,
            )
            path = write_available_skill_proposal(repo, available, "demo-skill")
            self.assertIn("available-proposals", str(path))
            self.assertFalse((repo / ".cursor" / "skills" / "demo-skill").exists())
            proposal = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(proposal["lifecycle_stage"], "AVAILABLE_SKILL")
            self.assertFalse(proposal["approved_for_execution"])

    def test_proven_requires_two_successful_experiences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sandbox = _sandbox_candidate()
            approved = advance_lifecycle(
                sandbox,
                target_stage="APPROVED",
                evidence_paths=[".agent/evidence/a.md"],
                captain_approved=True,
                skill_slug="demo-skill",
            )
            available = advance_lifecycle(
                approved,
                target_stage="AVAILABLE_SKILL",
                evidence_paths=[".agent/evidence/a.md"],
                captain_approved=True,
                skill_slug="demo-skill",
                repo_root=repo,
            )
            with self.assertRaises(PromotionError):
                advance_lifecycle(
                    available,
                    target_stage="PROVEN_SKILL",
                    evidence_paths=[".agent/evidence/p.md"],
                    captain_approved=True,
                    skill_slug="demo-skill",
                    repo_root=repo,
                )
            for i in range(2):
                write_experience(
                    repo,
                    {
                        "experience_id": f"exp-demo-{i}",
                        "run_id": f"run-demo-{i}",
                        "plan_id": "m9-test",
                        "outcome": "success",
                        "source_instance": "control-test",
                        "skills_used": ["demo-skill"],
                        "summary": f"demo success {i}",
                    },
                )
            self.assertEqual(
                count_successful_experiences_for_skill(repo, "demo-skill"), 2
            )
            proven = advance_lifecycle(
                available,
                target_stage="PROVEN_SKILL",
                evidence_paths=[".agent/evidence/p.md"],
                captain_approved=True,
                skill_slug="demo-skill",
                repo_root=repo,
            )
            self.assertEqual(proven["lifecycle_stage"], "PROVEN_SKILL")
            staging = write_staging_candidate(
                repo,
                available,
                target_stage="PROVEN_SKILL",
                evidence_paths=[".agent/evidence/p.md"],
                captain_approved=True,
                skill_slug="demo-skill",
            )
            self.assertTrue(staging.is_file())


class M9ArtifactContextTests(unittest.TestCase):
    def test_artifact_context_section_always_rendered(self) -> None:
        artifacts = build_capability_plan(
            ROOT,
            "routing artifact evaluator proposal",
            plan_id="m9-artifact-section",
        )
        markdown = render_capability_plan_sections(artifacts)
        self.assertIn("## Artifact Context", markdown)


if __name__ == "__main__":
    unittest.main()
