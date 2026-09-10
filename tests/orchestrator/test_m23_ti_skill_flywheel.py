"""M23 TI scorecard + skill flywheel gates."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.learning.drafts import LearningDraftError, write_unified_skill_draft
from orchestrator.learning.loop import run_skill_learning_loop
from orchestrator.learning.scorecard import ScorecardError, write_ti_scorecard_evidence
from orchestrator.promotion.draft_gates import (
    SkillDraftGateError,
    require_skill_draft_evidence,
)
from orchestrator.providers.technology_intelligence.github_stars_provider import (
    load_recorded_starred_fixtures,
)
from orchestrator.providers.technology_intelligence.stars_categorization import (
    DEFAULT_CATEGORIES,
    load_manual_labels,
    run_batch_categorization,
)
from orchestrator.providers.technology_intelligence.starred_provenance import (
    StarredProvenanceError,
    assert_starred_provenance,
    has_starred_provenance,
    stamp_starred_provenance,
)

ROOT = Path(__file__).resolve().parents[2]
LABELS = ROOT / "tests" / "fixtures" / "ti" / "github-stars-labels" / "manual-labels.json"
STARRED = ROOT / "tests" / "fixtures" / "ti" / "github-stars-recorded"


class M23CategoriesTests(unittest.TestCase):
    def test_default_categories_include_design_system(self) -> None:
        self.assertIn("design-system", DEFAULT_CATEGORIES)
        self.assertEqual(len(DEFAULT_CATEGORIES), 6)

    def test_manual_labels_include_design_system(self) -> None:
        labels = load_manual_labels(LABELS)
        cats = {row["category"] for row in labels}
        self.assertIn("design-system", cats)


class M23StarredProvenanceTests(unittest.TestCase):
    def test_rejects_non_starred_external_feed(self) -> None:
        with self.assertRaises(StarredProvenanceError):
            assert_starred_provenance(
                [
                    {
                        "full_name": "evil/not-starred",
                        "description": "random url ingest",
                        "html_url": "https://example.com/evil",
                    }
                ],
                context="test",
            )

    def test_accepts_stamped_starred_fixtures(self) -> None:
        repos = load_recorded_starred_fixtures(STARRED)
        self.assertTrue(repos)
        self.assertTrue(all(has_starred_provenance(r) for r in repos))
        assert_starred_provenance(repos, source="fixtures:github-stars-recorded")

    def test_stamp_adds_provenance(self) -> None:
        stamped = stamp_starred_provenance(
            [{"full_name": "org/repo", "description": "x"}],
            source="gh api user/starred",
        )
        self.assertTrue(stamped[0]["starred"])
        self.assertTrue(has_starred_provenance(stamped[0]))


class M23DraftGateTests(unittest.TestCase):
    def test_draft_fails_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            candidate = {
                "id": "c1",
                "version": "0.1.0",
                "kind": "candidate",
                "source": {
                    "type": "external-candidate",
                    "path": "example-org/craft-design-tokens",
                    "provenance_url": "",
                },
                "capabilities_provided": ["design-tokens"],
                "approved_for_execution": False,
                "lifecycle_stage": "ANALYZED",
                "discovery_signal": "github-stars:example-org/craft-design-tokens",
                "notes": "",
                "provenance": {"star_category": "design-system", "starred": True},
            }
            with self.assertRaises(LearningDraftError):
                write_unified_skill_draft(repo, candidate, "from-stars-craft-tokens")

    def test_draft_fails_when_only_security_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            evidence = repo / "security-review.md"
            evidence.write_text("# Security\n", encoding="utf-8")
            with self.assertRaises(SkillDraftGateError) as ctx:
                require_skill_draft_evidence([evidence])
            self.assertIn("dependency-supply-chain", str(ctx.exception))

    def test_scorecard_then_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            starred = {
                "full_name": "example-org/craft-design-tokens",
                "description": "Craft design tokens",
                "topics": ["design-system", "tokens"],
                "star_category": "design-system",
                "starred": True,
                "html_url": "https://github.com/example-org/craft-design-tokens",
            }
            candidate = {
                "id": "github-stars-example-org-craft-design-tokens",
                "version": "0.1.0",
                "kind": "candidate",
                "source": {
                    "type": "external-candidate",
                    "path": "example-org/craft-design-tokens",
                    "provenance_url": starred["html_url"],
                    "starred": True,
                },
                "capabilities_provided": ["design-tokens", "craft-ui"],
                "approved_for_execution": False,
                "lifecycle_stage": "ANALYZED",
                "discovery_signal": "github-stars:example-org/craft-design-tokens|category:design-system",
                "notes": "[design-system] craft tokens",
                "provenance": {"star_category": "design-system", "starred": True},
            }
            scorecard = write_ti_scorecard_evidence(
                repo, repo=starred, candidate=candidate, category="design-system"
            )
            self.assertFalse(scorecard["approved_for_execution"])
            self.assertEqual(len(scorecard["evidence_paths"]), 2)
            drafts = write_unified_skill_draft(
                repo,
                candidate,
                "from-stars-craft-design-tokens",
                evidence_paths=scorecard["evidence_paths"],
            )
            self.assertTrue(drafts["skill_md"].is_file())
            body = drafts["skill_md"].read_text(encoding="utf-8")
            self.assertIn("security-review", body)
            self.assertIn("design-system", body)
            staged = json.loads(drafts["source_candidate"].read_text(encoding="utf-8"))
            self.assertIs(staged["approved_for_execution"], False)

    def test_scorecard_rejects_non_starred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ScorecardError):
                write_ti_scorecard_evidence(
                    Path(tmp),
                    repo={"full_name": "evil/repo", "description": "nope"},
                    candidate={"id": "x", "approved_for_execution": False},
                )


class M23LearningLoopDesignSystemTests(unittest.TestCase):
    def test_loop_design_system_category_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report = run_skill_learning_loop(
                repo,
                objective="design system tokens craft ui primitives",
                source="fixtures",
                top_n=1,
                category_filter="design-system",
                control_root=ROOT,
            )
            self.assertGreaterEqual(report["candidate_count"], 1)
            self.assertTrue(report["starred_provenance_required"])
            self.assertTrue(report["draft_requires_security_and_supply_chain"])
            self.assertFalse(report["approved_for_execution"])
            entry = report["results"][0]
            self.assertEqual(entry["star_category"], "design-system")
            self.assertIn("scorecard", entry)
            evidence = entry["scorecard"]["evidence_paths"]
            self.assertEqual(len(evidence), 2)
            for path in evidence:
                self.assertTrue(Path(path).is_file())
            draft = entry["draft"]["skill_md"]
            self.assertIn("/skill-drafts/", draft)

    def test_batch_rejects_unstamped_when_not_using_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # run_batch stamps, so pass empty list of already-bad through categorize gate
            # via assert directly after loading raw JSON without stamp helpers
            raw_path = STARRED / "starred-repos.json"
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            # Strip starred markers to simulate non-starred URL ingest
            unclean = []
            for row in raw:
                item = {
                    "full_name": row["full_name"],
                    "description": row["description"],
                    "topics": row.get("topics") or [],
                }
                unclean.append(item)
            with self.assertRaises(StarredProvenanceError):
                assert_starred_provenance(unclean, context="raw-url-ingest")
            # Batch path stamps trusted fixture source — still OK when source trusted
            report = run_batch_categorization(
                Path(tmp),
                unclean,
                labels_path=LABELS,
                source="fixtures:github-stars-recorded",
            )
            self.assertEqual(report["record_count"], 4)


if __name__ == "__main__":
    unittest.main()
