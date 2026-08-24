"""Phase F plan writer tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "planning"


class PlanWriterTests(unittest.TestCase):
    def test_renders_all_required_sections(self) -> None:
        artifacts = build_capability_plan(
            ROOT,
            "Build a React dashboard with component tests",
            {"stacks": ["react"]},
            plan_id="test-plan-writer",
        )
        markdown = render_capability_plan_sections(artifacts)
        for heading in (
            "## Required Capabilities",
            "## Reusable Capabilities Found",
            "## Technology Intelligence Candidates",
            "## Knowledge Context",
            "## Performance Context",
            "## Task Graph",
            "## Proposed Agent Configuration",
            "## Evaluation Strategy",
            "## Learning Plan",
            "## Approval Boundary",
        ):
            self.assertIn(heading, markdown)

    def test_frontend_fixture_mentions_react_skill(self) -> None:
        fixture = json.loads((FIXTURES / "frontend-ui.json").read_text(encoding="utf-8"))
        artifacts = build_capability_plan(
            ROOT,
            fixture["objective"],
            fixture.get("context", {}),
            plan_id="test-frontend",
        )
        markdown = render_capability_plan_sections(artifacts)
        self.assertIn("react-engineering", markdown)
        self.assertIn("task-impl-frontend", markdown)

    def test_capability_gap_fixture_surfaces_gaps(self) -> None:
        fixture = json.loads((FIXTURES / "capability-gap.json").read_text(encoding="utf-8"))
        artifacts = build_capability_plan(
            ROOT,
            fixture["objective"],
            fixture.get("context", {}),
            plan_id="test-gap",
        )
        markdown = render_capability_plan_sections(artifacts)
        self.assertIn("### Capability Gaps", markdown)
        self.assertIn("quantum-circuit-synthesis", markdown)
        self.assertIn("Do not silently improvise", markdown)

    def test_ti_candidates_show_not_approved_banner(self) -> None:
        artifacts = build_capability_plan(
            ROOT,
            "Build a React dashboard",
            plan_id="test-ti",
        )
        markdown = render_capability_plan_sections(artifacts)
        self.assertIn("NOT APPROVED FOR EXECUTION", markdown)
        self.assertIn("provider: stub", markdown)

    def test_writes_machine_artifacts(self) -> None:
        plan_id = "test-artifacts"
        artifacts = build_capability_plan(
            ROOT,
            "Build a Node API",
            {"stacks": ["node"]},
            plan_id=plan_id,
        )
        for key in ("resolve", "task_graph", "manifests"):
            rel = artifacts.artifact_paths[key]
            path = ROOT / rel
            self.assertTrue(path.is_file(), f"missing artifact {rel}")


if __name__ == "__main__":
    unittest.main()
