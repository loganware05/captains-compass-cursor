"""M40 WS3 — typed task-graph links and module dependency graph tests."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from orchestrator.dependency_graph import build_dependency_graph, resolve_import
from orchestrator.context.inodes import build_store
from orchestrator.planner.build import build_task_graph
from orchestrator.planner.decompose import ARCHITECTURE_CONTRACT
from orchestrator.planner.validate_graph import (
    GraphValidationError,
    normalize_dependencies,
    topological_order,
    validate_task_graph,
)
from orchestrator.plan_writer.render import render_task_graph
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SRC = ROOT / "tests" / "fixtures" / "context" / "src"


class TypedDependencyTests(unittest.TestCase):
    def test_string_form_passthrough(self) -> None:
        task = {"id": "a", "dependencies": ["b", "c"]}
        self.assertEqual(normalize_dependencies(task), ["b", "c"])

    def test_object_form_validated(self) -> None:
        task = {
            "id": "a",
            "dependencies": [
                {"target": "b", "link": "hard", "contract": "api-contract"},
                {"target": "c", "link": "symlink", "paths": ["src/x"]},
            ],
        }
        self.assertEqual(normalize_dependencies(task), ["b", "c"])

    def test_object_form_rejects_bad_link(self) -> None:
        task = {"id": "a", "dependencies": [{"target": "b", "link": "junction"}]}
        with self.assertRaises(GraphValidationError):
            normalize_dependencies(task)

    def test_object_form_requires_target(self) -> None:
        task = {"id": "a", "dependencies": [{"link": "hard"}]}
        with self.assertRaises(GraphValidationError):
            normalize_dependencies(task)

    def test_cycle_detected_through_typed_edges(self) -> None:
        tasks = [
            {"id": "a", "dependencies": [{"target": "b", "link": "hard"}]},
            {"id": "b", "dependencies": ["a"]},
        ]
        with self.assertRaises(GraphValidationError):
            validate_task_graph(tasks)

    def test_topological_order_with_typed_edges(self) -> None:
        tasks = [
            {"id": "c", "dependencies": [{"target": "b", "link": "symlink", "paths": []}]},
            {"id": "b", "dependencies": [{"target": "a", "link": "hard", "contract": "x"}]},
            {"id": "a", "dependencies": []},
        ]
        self.assertEqual(topological_order(tasks), ["a", "b", "c"])


class DecomposeTypedLinkTests(unittest.TestCase):
    def test_planner_emits_hard_and_symlink_edges(self) -> None:
        graph = build_task_graph("Build a React dashboard with a node API and tests")
        tasks = {task["id"]: task for task in graph["tasks"]}
        for task in graph["tasks"]:
            validate_document(task, "task.schema.json")

        frontend = tasks["task-impl-frontend"]
        self.assertEqual(
            frontend["dependencies"],
            [{"target": "task-architecture", "link": "hard", "contract": ARCHITECTURE_CONTRACT}],
        )
        backend = tasks["task-impl-backend"]
        self.assertEqual(
            backend["dependencies"],
            [{"target": "task-architecture", "link": "hard", "contract": ARCHITECTURE_CONTRACT}],
        )

        validation = tasks["task-validation"]
        dep_map = {dep["target"]: dep for dep in validation["dependencies"]}
        self.assertEqual(dep_map["task-impl-frontend"]["link"], "symlink")
        self.assertIn("frontend-diff", dep_map["task-impl-frontend"]["paths"])
        self.assertEqual(dep_map["task-impl-backend"]["link"], "symlink")

        # Ordering still holds: architecture before impl, validation after impl.
        order = graph["execution_order"]
        self.assertLess(order.index("task-architecture"), order.index("task-impl-frontend"))
        self.assertLess(order.index("task-impl-backend"), order.index("task-validation"))

    def test_render_handles_typed_dependencies(self) -> None:
        graph = build_task_graph("Build a React dashboard with tests")

        class _Artifacts:
            task_graph = graph

            @staticmethod
            def artifact_paths() -> dict:
                return {"task_graph": ".agent/plans/draft/task-graph.json"}

        artifacts = _Artifacts()
        artifacts.artifact_paths = {"task_graph": ".agent/plans/draft/task-graph.json"}
        rendered = render_task_graph(artifacts)
        self.assertIn("task-architecture (hard)", rendered)


class DependencyGraphTests(unittest.TestCase):
    def _fixture_repo(self, tmp: str) -> tuple[Path, Path]:
        repo = Path(tmp)
        shutil.copytree(FIXTURE_SRC, repo / "src")
        store = repo / ".agent" / "inodes"
        build_store(repo, output_dir=store)
        return repo, store

    def test_resolve_relative_import(self) -> None:
        indexed = {"src/ui/components/Input.tsx", "src/api/client.ts"}
        self.assertEqual(
            resolve_import("src/api/client.ts", "../ui/components/Input", indexed),
            "src/ui/components/Input.tsx",
        )
        self.assertIsNone(resolve_import("src/api/client.ts", "./missing", indexed))
        self.assertIsNone(resolve_import("src/api/client.ts", "react", indexed))

    def test_graph_edges_typed_and_boundary_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, store = self._fixture_repo(tmp)
            graph = build_dependency_graph(repo, store_dir=store)
            edges = {(edge["from"], edge["to"]): edge for edge in graph["edges"]}

            form_edge = edges[("src/api/client.ts", "src/ui/components/Form.tsx")]
            self.assertEqual(form_edge["link"], "hard")
            self.assertEqual(form_edge["contract"], ["FormProps", "buildForm"])
            self.assertTrue(form_edge["cross_boundary"])

            validate_edge = edges[("src/api/client.ts", "src/ui/utils/validate.ts")]
            self.assertEqual(validate_edge["link"], "hard")
            self.assertTrue(validate_edge["cross_boundary"])

            side_effect = edges[("src/api/client.ts", "src/ui/components/Input.tsx")]
            self.assertEqual(side_effect["link"], "symlink")
            self.assertTrue(side_effect["cross_boundary"])

            intra = edges[("src/ui/utils/validate.ts", "src/ui/components/Input.tsx")]
            self.assertEqual(intra["link"], "hard")
            self.assertFalse(intra["cross_boundary"])

            stats = graph["stats"]
            self.assertEqual(stats["symlink"], 1)
            self.assertEqual(stats["cross_boundary"], 3)
            self.assertEqual(stats["edge_count"], len(graph["edges"]))


if __name__ == "__main__":
    unittest.main()
