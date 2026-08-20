"""Phase G end-to-end orchestrator integration tests (golden fixtures)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from orchestrator.assembler.manifest import build_manifests_for_objective
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections
from orchestrator.planner.build import build_task_graph
from orchestrator.resolver.resolve import resolve_capabilities

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "planning"
FIXTURE_NAMES = (
    "frontend-ui.json",
    "backend-api.json",
    "ml-pipeline.json",
    "security-sensitive.json",
    "multi-domain.json",
    "capability-gap.json",
)


class GoldenFixturePipelineTests(unittest.TestCase):
    def _load_fixture(self, name: str) -> dict:
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_all_fixtures_present(self) -> None:
        for name in FIXTURE_NAMES:
            self.assertTrue((FIXTURES / name).is_file(), f"missing fixture {name}")

    def test_fixtures_produce_deterministic_pipeline(self) -> None:
        for name in FIXTURE_NAMES:
            fixture = self._load_fixture(name)
            objective = fixture["objective"]
            context = fixture.get("context", {})
            plan_id = f"golden-{name.replace('.json', '')}"

            first = build_capability_plan(ROOT, objective, context, plan_id=plan_id)
            second = build_capability_plan(ROOT, objective, context, plan_id=plan_id)

            self.assertEqual(first.resolve, second.resolve, f"{name}: resolve drift")
            self.assertEqual(first.task_graph, second.task_graph, f"{name}: task graph drift")
            self.assertEqual(first.manifests, second.manifests, f"{name}: manifests drift")

    def test_fixtures_match_expected_skill_rankings(self) -> None:
        for name in FIXTURE_NAMES:
            fixture = self._load_fixture(name)
            result = resolve_capabilities(ROOT, fixture["objective"], fixture.get("context", {}))
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

    def test_security_sensitive_fixture_includes_security_task(self) -> None:
        fixture = self._load_fixture("security-sensitive.json")
        graph = build_task_graph(fixture["objective"], fixture.get("context", {}))
        task_ids = [task["id"] for task in graph["tasks"]]
        self.assertIn("task-security-review", task_ids)

        payload = build_manifests_for_objective(
            ROOT, fixture["objective"], fixture.get("context", {})
        )
        security_manifest = next(
            m for m in payload["manifests"] if m["task_id"] == "task-security-review"
        )
        self.assertEqual(security_manifest["reference_profile"], "security-reviewer")
        self.assertIn("security-review", security_manifest["skills"])

    def test_multi_domain_fixture_has_parallel_impl_tasks(self) -> None:
        fixture = self._load_fixture("multi-domain.json")
        graph = build_task_graph(fixture["objective"], fixture.get("context", {}))
        impl_tasks = [t for t in graph["tasks"] if t["id"].startswith("task-impl-")]
        self.assertGreaterEqual(len(impl_tasks), 3)
        for task in impl_tasks:
            self.assertTrue(task["parallelizable"])

    def test_capability_gap_fixture_surfaces_in_rendered_plan(self) -> None:
        fixture = self._load_fixture("capability-gap.json")
        artifacts = build_capability_plan(
            ROOT,
            fixture["objective"],
            fixture.get("context", {}),
            plan_id="golden-gap",
        )
        markdown = render_capability_plan_sections(artifacts)
        self.assertIn("### Capability Gaps", markdown)
        self.assertIn("quantum-circuit-synthesis", markdown)
        self.assertIn("Do not silently improvise", markdown)

    def test_rendered_plan_contains_all_template_sections(self) -> None:
        fixture = self._load_fixture("frontend-ui.json")
        artifacts = build_capability_plan(
            ROOT,
            fixture["objective"],
            fixture.get("context", {}),
            plan_id="golden-sections",
        )
        markdown = render_capability_plan_sections(artifacts)
        for heading in (
            "## Required Capabilities",
            "## Reusable Capabilities Found",
            "## Technology Intelligence Candidates",
            "## Task Graph",
            "## Proposed Agent Configuration",
            "## Evaluation Strategy",
            "## Learning Plan",
            "## Approval Boundary",
        ):
            self.assertIn(heading, markdown, f"missing section {heading}")


if __name__ == "__main__":
    unittest.main()
