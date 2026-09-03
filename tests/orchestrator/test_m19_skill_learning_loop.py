"""M19 skill learning loop tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.learning.drafts import write_unified_skill_draft
from orchestrator.learning.export import (
    LearningExportError,
    export_categorized_to_staging,
)
from orchestrator.learning.loop import LearningLoopError, run_skill_learning_loop
from orchestrator.learning.sandbox_harness import (
    SandboxHarnessError,
    run_fixture_sandbox_harness,
)
from orchestrator.learning.similarity import find_similar_skills, jaccard, tokenize
from orchestrator.providers.technology_intelligence.github_stars_provider import (
    load_recorded_starred_fixtures,
)
from orchestrator.providers.technology_intelligence.stars_categorization import (
    run_batch_categorization,
)
from orchestrator.promotion.advance import advance_lifecycle

ROOT = Path(__file__).resolve().parents[2]
LABELS = ROOT / "tests" / "fixtures" / "ti" / "github-stars-labels" / "manual-labels.json"
STARRED = ROOT / "tests" / "fixtures" / "ti" / "github-stars-recorded"


class SkillLearningLoopTests(unittest.TestCase):
    def test_export_and_draft_and_harness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            repos = load_recorded_starred_fixtures(STARRED)
            run_batch_categorization(
                repo, repos, labels_path=LABELS, source="fixtures:test"
            )
            exported = export_categorized_to_staging(
                repo, "accessible react forms", top_n=1
            )
            self.assertEqual(len(exported), 1)
            candidate = exported[0]["candidate"]
            self.assertIs(candidate["approved_for_execution"], False)
            slug = exported[0]["skill_slug"]
            drafts = write_unified_skill_draft(repo, candidate, slug)
            self.assertTrue(drafts["skill_md"].is_file())
            self.assertTrue(drafts["capability_yaml"].is_file())
            result = run_fixture_sandbox_harness(
                repo, candidate, skill_slug=slug, control_root=ROOT
            )
            self.assertTrue(result["passed"])
            self.assertEqual(result["lifecycle_stage"], "SANDBOX_TESTED")
            staged = json.loads(Path(result["staging_candidate"]).read_text(encoding="utf-8"))
            self.assertEqual(staged["lifecycle_stage"], "SANDBOX_TESTED")
            self.assertIs(staged["approved_for_execution"], False)

    def test_harness_rejects_approved_for_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            candidate = {
                "id": "bad",
                "version": "0.1.0",
                "kind": "candidate",
                "source": {"type": "external-candidate", "path": "x", "provenance_url": ""},
                "capabilities_provided": ["x"],
                "approved_for_execution": True,
                "lifecycle_stage": "ANALYZED",
                "discovery_signal": "test",
                "notes": "",
            }
            draft = repo / ".agent" / "capabilities" / "candidates" / "skill-drafts" / "from-stars-bad"
            draft.mkdir(parents=True)
            (draft / "SKILL.md").write_text("---\nname: from-stars-bad\ndescription: x\n---\n", encoding="utf-8")
            (draft / "capability.yaml").write_text(
                'id: from-stars-bad\nversion: "0.1.0"\nkind: skill\n'
                "source:\n  type: compass-skill\n  path: .cursor/skills/from-stars-bad/SKILL.md\n"
                "lifecycle_stage: AVAILABLE_SKILL\ncapabilities_provided:\n  - x\n"
                "security_sensitivity: medium\nprovenance:\n  inferred: false\n"
                "  from_candidate: bad\n  captain_approval_required: true\nnotes: t\n",
                encoding="utf-8",
            )
            with self.assertRaises(SandboxHarnessError):
                run_fixture_sandbox_harness(repo, candidate, skill_slug="from-stars-bad")

    def test_captain_gate_still_required_for_available(self) -> None:
        candidate = {
            "id": "c1",
            "version": "0.1.0",
            "kind": "candidate",
            "source": {"type": "external-candidate", "path": "org/repo", "provenance_url": ""},
            "capabilities_provided": ["forms"],
            "approved_for_execution": False,
            "lifecycle_stage": "SANDBOX_TESTED",
            "discovery_signal": "test",
            "notes": "",
            "evidence_paths": ["e.md"],
        }
        with self.assertRaises(Exception) as ctx:
            advance_lifecycle(candidate, target_stage="AVAILABLE_SKILL", evidence_paths=["e.md"])
        self.assertIn("captain-approved", str(ctx.exception).lower().replace("_", "-"))

    def test_export_requires_categorized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LearningExportError):
                export_categorized_to_staging(Path(tmp), "anything")

    def test_similarity_jaccard_and_find(self) -> None:
        self.assertGreater(jaccard(tokenize("react forms"), tokenize("react accessible forms")), 0.3)
        candidate = {
            "id": "github-stars-example-org-accessible-react-forms",
            "notes": "[frontend-ui] accessible react forms validation",
            "discovery_signal": "github-stars:example-org/accessible-react-forms|category:frontend-ui",
            "capabilities_provided": ["accessible-forms", "react-ui"],
            "approved_for_execution": False,
            "provenance": {"star_category": "frontend-ui"},
        }
        matches = find_similar_skills(
            ROOT,
            candidate,
            repo={
                "full_name": "example-org/accessible-react-forms",
                "description": "Accessible React forms",
                "star_category": "frontend-ui",
                "topics": ["react", "accessibility", "forms"],
            },
            threshold=0.2,
            top_k=5,
        )
        slugs = {m["skill_slug"] for m in matches}
        self.assertIn("react-engineering", slugs)
        self.assertNotIn("skill-learning-loop", slugs)
        self.assertNotIn("security-review", slugs)

    def test_full_loop_fixtures_no_live_skill_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            before = {
                p.name: (p / "SKILL.md").read_text(encoding="utf-8")
                for p in (ROOT / ".cursor" / "skills").iterdir()
                if (p / "SKILL.md").is_file()
            }
            report = run_skill_learning_loop(
                repo,
                objective="accessible react forms",
                source="fixtures",
                top_n=1,
                control_root=ROOT,
            )
            self.assertEqual(report["kind"], "skill-learning-run")
            self.assertGreaterEqual(report["candidate_count"], 1)
            self.assertFalse(report["auto_install"])
            after = {
                p.name: (p / "SKILL.md").read_text(encoding="utf-8")
                for p in (ROOT / ".cursor" / "skills").iterdir()
                if (p / "SKILL.md").is_file()
            }
            self.assertEqual(before, after)
            entry = report["results"][0]
            draft = entry.get("draft") or {}
            skill_md = draft.get("skill_md")
            self.assertTrue(skill_md and Path(skill_md).is_file())
            self.assertIn("/skill-drafts/", skill_md)
            if entry["mode"] == "improve-existing":
                self.assertIn("skill-improvement-proposals", entry.get("improvement_proposal", ""))
                self.assertEqual(entry.get("target_skill_slug"), "react-engineering")

    def test_refuse_repo_root_under_skills(self) -> None:
        with self.assertRaises(LearningLoopError):
            run_skill_learning_loop(
                ROOT / ".cursor" / "skills",
                objective="x",
                source="fixtures",
                control_root=ROOT,
            )

    def test_loop_unsupported_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LearningLoopError):
                run_skill_learning_loop(
                    Path(tmp),
                    objective="x",
                    source="nope",
                    control_root=ROOT,
                )


if __name__ == "__main__":
    unittest.main()
