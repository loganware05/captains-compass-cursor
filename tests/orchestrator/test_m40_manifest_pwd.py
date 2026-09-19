"""M40 WS6 — subagent pwd working-context isolation tests."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from orchestrator.assembler.manifest import build_manifest_for_task
from orchestrator.context.inodes import build_store
from orchestrator.context.walker import derive_context_tree
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SRC = ROOT / "tests" / "fixtures" / "context" / "src"


def _fixture_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    shutil.copytree(FIXTURE_SRC, repo / "src")
    store = repo / ".agent" / "inodes"
    build_store(repo, output_dir=store)
    derive_context_tree(repo, store_dir=store)
    return repo


def _task(task_id: str) -> dict:
    return {
        "id": task_id,
        "objective": f"Fixture task {task_id}",
        "required_capabilities": [],
        "dependencies": [],
    }


class WorkingContextTests(unittest.TestCase):
    def test_manifest_without_store_is_unrestricted_with_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(FIXTURE_SRC, repo / "src")
            manifest = build_manifest_for_task(
                _task("task-impl-frontend"),
                [],
                stacks=[],
                security_sensitive=False,
                plan_id="m40-pwd-test",
                repo_root=repo,
            )
            validate_document(manifest, "agent-manifest.schema.json")
            context = manifest["working_context"]
            self.assertFalse(context["route_resolved"])
            self.assertEqual(context["scope_allow"], ["**"])
            self.assertIn("context tree absent", context["note"])

    def test_manifest_scoped_to_module_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _fixture_repo(Path(tmp))
            manifest = build_manifest_for_task(
                _task("task-impl-frontend"),
                [],
                stacks=["react"],
                security_sensitive=False,
                plan_id="m40-pwd-test",
                repo_root=repo,
            )
            validate_document(manifest, "agent-manifest.schema.json")
            context = manifest["working_context"]
            self.assertTrue(context["route_resolved"])
            self.assertEqual(context["context_root"], "src/ui")
            self.assertEqual(context["scope_allow"], ["src/ui/**"])
            self.assertEqual(len(context["inode_refs"]), 3)
            self.assertTrue(all(ref.startswith("ino-") for ref in context["inode_refs"]))

    def test_scope_deny_always_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _fixture_repo(Path(tmp))
            manifest = build_manifest_for_task(
                _task("task-impl-backend"),
                [],
                stacks=[],
                security_sensitive=False,
                plan_id="m40-pwd-test",
                repo_root=repo,
            )
            deny = manifest["working_context"]["scope_deny"]
            self.assertIn("**/.env", deny)
            self.assertIn("secrets/**", deny)

    def test_parallel_manifests_disjoint_inode_refs(self) -> None:
        """Pollution-prevention invariant: disjoint module scopes share no inodes."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = _fixture_repo(Path(tmp))
            frontend = build_manifest_for_task(
                _task("task-impl-frontend"),
                [],
                stacks=["react"],
                security_sensitive=False,
                plan_id="m40-pwd-test",
                repo_root=repo,
            )
            backend = build_manifest_for_task(
                _task("task-impl-backend"),
                [],
                stacks=["node"],
                security_sensitive=False,
                plan_id="m40-pwd-test",
                repo_root=repo,
            )
            front_refs = set(frontend["working_context"]["inode_refs"])
            back_refs = set(backend["working_context"]["inode_refs"])
            self.assertEqual(frontend["working_context"]["context_root"], "src/ui")
            self.assertEqual(backend["working_context"]["context_root"], "src/api")
            self.assertTrue(front_refs)
            self.assertTrue(back_refs)
            self.assertTrue(front_refs.isdisjoint(back_refs))

    def test_manifest_without_repo_root_degrades_gracefully(self) -> None:
        manifest = build_manifest_for_task(
            _task("task-impl-frontend"),
            [],
            stacks=[],
            security_sensitive=False,
            plan_id="m40-pwd-test",
            repo_root=None,
        )
        validate_document(manifest, "agent-manifest.schema.json")
        self.assertIn("no repo_root", manifest["working_context"]["note"])


if __name__ == "__main__":
    unittest.main()
