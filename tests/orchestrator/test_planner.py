"""Phase D task graph planner tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from orchestrator.intent.infer_capabilities import infer_capabilities
from orchestrator.planner.build import build_task_graph
from orchestrator.planner.decompose import decompose
from orchestrator.planner.validate_graph import GraphValidationError, topological_order, validate_task_graph

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "planning"


class DecomposeTests(unittest.TestCase):
    def test_frontend_objective_includes_ui_task(self) -> None:
        objective = "Build an accessible React dashboard with component tests"
        intent = infer_capabilities(objective, {"stacks": ["react"]})
        tasks = decompose(objective, intent)
        ids = [task["id"] for task in tasks]
        self.assertIn("task-discovery", ids)
        self.assertIn("task-architecture", ids)
        self.assertIn("task-impl-frontend", ids)
        self.assertIn("task-validation", ids)
        self.assertIn("task-documentation", ids)

    def test_multi_domain_impl_tasks_parallelizable(self) -> None:
        objective = (
            "Ship a full-stack feature: React UI, Node API, Prisma migrations, Docker preview"
        )
        intent = infer_capabilities(
            objective,
            {"stacks": ["react", "node", "postgres", "docker"]},
        )
        tasks = decompose(objective, intent)
        impl_tasks = [t for t in tasks if t["id"].startswith("task-impl-")]
        self.assertGreaterEqual(len(impl_tasks), 3)
        for task in impl_tasks:
            self.assertTrue(task["parallelizable"])
            self.assertEqual(task["dependencies"], ["task-architecture"])

    def test_security_sensitive_adds_security_review_task(self) -> None:
        objective = "Review OAuth login flow for auth flaws and injection risks"
        intent = infer_capabilities(objective, {"security_sensitive": True})
        tasks = decompose(objective, intent)
        ids = [task["id"] for task in tasks]
        self.assertIn("task-security-review", ids)


class ValidateGraphTests(unittest.TestCase):
    def test_rejects_missing_dependency(self) -> None:
        tasks = [
            {"id": "a", "objective": "A", "dependencies": ["missing"]},
            {"id": "b", "objective": "B", "dependencies": []},
        ]
        with self.assertRaises(GraphValidationError):
            validate_task_graph(tasks)

    def test_rejects_cycle(self) -> None:
        tasks = [
            {"id": "a", "objective": "A", "dependencies": ["b"]},
            {"id": "b", "objective": "B", "dependencies": ["a"]},
        ]
        with self.assertRaises(GraphValidationError):
            validate_task_graph(tasks)

    def test_topological_order(self) -> None:
        tasks = [
            {"id": "task-discovery", "objective": "d", "dependencies": []},
            {"id": "task-architecture", "objective": "a", "dependencies": ["task-discovery"]},
            {"id": "task-validation", "objective": "v", "dependencies": ["task-architecture"]},
        ]
        order = topological_order(tasks)
        self.assertEqual(order.index("task-discovery"), 0)
        self.assertLess(order.index("task-architecture"), order.index("task-validation"))


class BuildTaskGraphTests(unittest.TestCase):
    def test_build_validates_task_schema(self) -> None:
        graph = build_task_graph("Build a React dashboard", {"stacks": ["react"]})
        self.assertIn("tasks", graph)
        self.assertIn("execution_order", graph)
        self.assertGreater(len(graph["tasks"]), 0)

    def test_fixture_graphs_are_valid(self) -> None:
        for fixture_path in FIXTURES.glob("*.json"):
            if fixture_path.name == "capability-gap.json":
                continue
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            graph = build_task_graph(fixture["objective"], fixture.get("context", {}))
            validate_task_graph(graph["tasks"])

    def test_deterministic_task_graph(self) -> None:
        objective = "Build React UI with Node API"
        context = {"stacks": ["react", "node"]}
        first = build_task_graph(objective, context)
        second = build_task_graph(objective, context)
        self.assertEqual(
            [task["id"] for task in first["tasks"]],
            [task["id"] for task in second["tasks"]],
        )


if __name__ == "__main__":
    unittest.main()
