"""Phase E agent manifest assembler tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from orchestrator.assembler.manifest import build_manifests_for_objective
from orchestrator.registry.compiler import write_registry
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "planning"


class ManifestAssemblerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        write_registry(ROOT)

    def _manifest_for_task(self, objective: str, context: dict, task_id: str) -> dict:
        payload = build_manifests_for_objective(ROOT, objective, context)
        for manifest in payload["manifests"]:
            if manifest["task_id"] == task_id:
                return manifest
        self.fail(f"task {task_id} not found in manifests")

    def test_frontend_impl_manifest_uses_implementation_agent(self) -> None:
        manifest = self._manifest_for_task(
            "Build a React dashboard with component tests",
            {"stacks": ["react"]},
            "task-impl-frontend",
        )
        self.assertEqual(manifest["reference_profile"], "implementation-agent")
        self.assertEqual(manifest["model"]["class"], "coding-strong")
        self.assertIn("react-engineering", manifest["skills"])

    def test_validation_manifest_uses_test_engineer(self) -> None:
        manifest = self._manifest_for_task(
            "Build a React dashboard with component tests",
            {"stacks": ["react"]},
            "task-validation",
        )
        self.assertEqual(manifest["reference_profile"], "test-engineer")
        self.assertIn("testing-validation", manifest["skills"])

    def test_security_review_manifest(self) -> None:
        manifest = self._manifest_for_task(
            "Review OAuth login flow for auth flaws and injection risks",
            {"security_sensitive": True},
            "task-security-review",
        )
        self.assertEqual(manifest["reference_profile"], "security-reviewer")
        self.assertIn("security-review", manifest["skills"])

    def test_manifest_count_matches_tasks(self) -> None:
        objective = "Ship React UI and Node API with tests"
        context = {"stacks": ["react", "node"]}
        payload = build_manifests_for_objective(ROOT, objective, context)
        from orchestrator.planner.build import build_task_graph

        graph = build_task_graph(objective, context)
        self.assertEqual(len(payload["manifests"]), len(graph["tasks"]))

    def test_manifests_validate_against_schema(self) -> None:
        payload = build_manifests_for_objective(
            ROOT,
            "Build a React dashboard",
            {"stacks": ["react"]},
        )
        for manifest in payload["manifests"]:
            validate_document(manifest, "agent-manifest.schema.json")

    def test_scoring_breakdown_present_when_skills_matched(self) -> None:
        manifest = self._manifest_for_task(
            "Build a React dashboard",
            {"stacks": ["react"]},
            "task-impl-frontend",
        )
        self.assertIn("scoring_breakdown", manifest)
        self.assertEqual(len(manifest["scoring_breakdown"]), 5)

    def test_fixture_manifests_are_deterministic(self) -> None:
        fixture = json.loads((FIXTURES / "frontend-ui.json").read_text(encoding="utf-8"))
        first = build_manifests_for_objective(
            ROOT, fixture["objective"], fixture.get("context", {})
        )
        second = build_manifests_for_objective(
            ROOT, fixture["objective"], fixture.get("context", {})
        )
        self.assertEqual(first["manifests"], second["manifests"])

    def test_permissions_least_privilege_for_discovery(self) -> None:
        manifest = self._manifest_for_task(
            "Build a React dashboard",
            {"stacks": ["react"]},
            "task-discovery",
        )
        self.assertEqual(manifest["permissions"], ["read-repo"])


if __name__ == "__main__":
    unittest.main()
