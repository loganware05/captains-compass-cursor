"""Phase C capability resolver tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from orchestrator.intent.infer_capabilities import infer_capabilities
from orchestrator.matcher.score import is_eligible_skill, rank_skills, score_skill
from orchestrator.registry.compiler import write_registry
from orchestrator.resolver.resolve import resolve_capabilities

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "planning"


class IntentInferenceTests(unittest.TestCase):
    def test_frontend_objective_infers_react_capabilities(self) -> None:
        intent = infer_capabilities(
            "Build a React dashboard with TypeScript components",
            {"stacks": ["react"]},
        )
        self.assertIn("react-component-development", intent.required_capabilities)
        self.assertIn("react", intent.domains_detected)

    def test_security_objective_flags_sensitive(self) -> None:
        intent = infer_capabilities("Review OAuth auth and secrets handling", {})
        self.assertTrue(intent.security_sensitive)
        self.assertIn("auth-review", intent.required_capabilities)


class MatcherScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        write_registry(ROOT)

    def test_react_skill_scores_higher_for_ui_objective(self) -> None:
        from orchestrator.registry.load import load_registry, registry_skills

        skills = registry_skills(load_registry(ROOT))
        react = next(s for s in skills if s["id"] == "react-engineering")
        harness = next(s for s in skills if s["id"] == "harness-gc")
        required = ["react-component-development", "typescript-ui"]
        react_score = score_skill(react, required, stacks=["react"]).score
        harness_score = score_skill(harness, required, stacks=["react"]).score
        self.assertGreater(react_score, harness_score)

    def test_candidate_skill_not_eligible(self) -> None:
        candidate = {
            "id": "external-lib",
            "kind": "candidate",
            "approved_for_execution": False,
            "lifecycle_stage": "DISCOVERED",
            "capabilities_provided": ["pdf-parsing"],
        }
        self.assertFalse(is_eligible_skill(candidate))
        ranked = rank_skills([candidate], ["pdf-parsing"])
        self.assertEqual(ranked, [])

    def test_scoring_breakdown_present(self) -> None:
        from orchestrator.registry.load import load_registry, registry_skills

        skills = registry_skills(load_registry(ROOT))
        node = next(s for s in skills if s["id"] == "node-engineering")
        ranked = score_skill(node, ["node-api-development"], stacks=["node"])
        self.assertEqual(len(ranked.scoring_breakdown), 5)
        self.assertAlmostEqual(sum(item["score"] for item in ranked.scoring_breakdown), ranked.score)


class FixtureResolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        write_registry(ROOT)

    def _run_fixture(self, name: str) -> None:
        fixture = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
        result = resolve_capabilities(
            ROOT,
            fixture["objective"],
            fixture.get("context", {}),
        )
        top_n = fixture.get("top_n", 5)
        top_ids = [item.skill_id for item in result.ranked_skills[:top_n]]
        for expected in fixture.get("expected_top_skills", []):
            self.assertIn(
                expected,
                top_ids,
                f"{name}: expected {expected} in top ranks, got {top_ids}",
            )
        for gap in fixture.get("expected_gaps", []):
            self.assertIn(gap, result.capability_gaps, f"{name}: missing gap {gap}")

    def test_frontend_ui_fixture(self) -> None:
        self._run_fixture("frontend-ui.json")

    def test_backend_api_fixture(self) -> None:
        self._run_fixture("backend-api.json")

    def test_ml_pipeline_fixture(self) -> None:
        self._run_fixture("ml-pipeline.json")

    def test_security_sensitive_fixture(self) -> None:
        self._run_fixture("security-sensitive.json")

    def test_multi_domain_fixture(self) -> None:
        self._run_fixture("multi-domain.json")

    def test_capability_gap_fixture(self) -> None:
        fixture = json.loads((FIXTURES / "capability-gap.json").read_text(encoding="utf-8"))
        result = resolve_capabilities(ROOT, fixture["objective"], fixture.get("context", {}))
        self.assertGreater(len(result.capability_gaps), 0)
        self.assertEqual(result.capability_gaps, fixture["expected_gaps"])


class DeterminismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        write_registry(ROOT)

    def test_same_input_same_ranking(self) -> None:
        objective = "Build React UI with Playwright e2e tests"
        context = {"stacks": ["react"]}
        first = resolve_capabilities(ROOT, objective, context)
        second = resolve_capabilities(ROOT, objective, context)
        self.assertEqual(
            [item.skill_id for item in first.ranked_skills[:5]],
            [item.skill_id for item in second.ranked_skills[:5]],
        )


if __name__ == "__main__":
    unittest.main()
