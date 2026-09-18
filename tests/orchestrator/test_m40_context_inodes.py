"""M40 WS1/WS2 — context inode store, extractors, and route walker tests."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.context.extract import extract_for_path, extract_python, extract_typescript
from orchestrator.context.inodes import (
    build_inode,
    build_store,
    find_stale,
    inode_for_path,
    inode_id_for,
    load_index,
    module_route_for,
)
from orchestrator.context.walker import derive_context_tree, walk_route
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SRC = ROOT / "tests" / "fixtures" / "context" / "src"
BUILD_CLI = ROOT / "scripts" / "build-context-inodes.sh"
WALK_CLI = ROOT / "scripts" / "walk-context-route.sh"


def _copy_fixture_tree(dest: Path) -> Path:
    target = dest / "src"
    shutil.copytree(FIXTURE_SRC, target)
    return dest


class PythonExtractTests(unittest.TestCase):
    def test_functions_classes_imports(self) -> None:
        source = (FIXTURE_SRC / "worker" / "processor.py").read_text(encoding="utf-8")
        result = extract_python(source)
        self.assertEqual(result["language"], "python")
        self.assertEqual(result["declared_complexity"], "O(N)")

        symbols = {symbol["name"]: symbol for symbol in result["symbols"]}
        process = symbols["process_records"]
        self.assertTrue(process["exported"])
        self.assertEqual(process["complexity"], "O(N)")
        self.assertEqual(process["return_type"], "list[dict]")
        param_names = [param["name"] for param in process["params"]]
        self.assertEqual(param_names, ["records", "strict"])
        self.assertEqual(process["params"][0]["type"], "list[dict]")

        helper = symbols["_internal_helper"]
        self.assertFalse(helper["exported"])

        store = symbols["RecordStore"]
        self.assertEqual(store["kind"], "class")
        method_names = [field["name"] for field in store["fields"]]
        self.assertIn("add", method_names)
        self.assertIn("to_json", method_names)

        modules = [imp["module"] for imp in result["imports"]]
        self.assertIn("json", modules)

    def test_syntax_error_yields_empty(self) -> None:
        result = extract_python("def broken(:\n")
        self.assertEqual(result["symbols"], [])


class TypeScriptExtractTests(unittest.TestCase):
    def test_interface_function_const_imports(self) -> None:
        source = (FIXTURE_SRC / "ui" / "components" / "Form.tsx").read_text(encoding="utf-8")
        result = extract_typescript(source)

        symbols = {symbol["name"]: symbol for symbol in result["symbols"]}
        props = symbols["FormProps"]
        self.assertEqual(props["kind"], "interface")
        self.assertTrue(props["exported"])
        field_map = {field["name"]: field for field in props["fields"]}
        self.assertEqual(field_map["title"]["type"], "string")
        self.assertTrue(field_map["disabled"]["optional"])

        build = symbols["buildForm"]
        self.assertEqual(build["kind"], "function")
        self.assertEqual(build["complexity"], "O(N)")
        self.assertEqual([p["name"] for p in build["params"]], ["title", "fields"])
        self.assertEqual(build["return_type"], "FormProps")

        const = symbols["DEFAULT_FORM_TITLE"]
        self.assertEqual(const["kind"], "const")

        imports = result["imports"]
        self.assertEqual(imports[0]["module"], "./Input")
        self.assertEqual(imports[0]["names"], ["InputProps"])

    def test_type_alias_and_arrow(self) -> None:
        source = (FIXTURE_SRC / "ui" / "components" / "Input.tsx").read_text(encoding="utf-8")
        result = extract_typescript(source)
        symbols = {symbol["name"]: symbol for symbol in result["symbols"]}
        self.assertEqual(symbols["InputKind"]["kind"], "type")
        self.assertEqual(symbols["describeInput"]["kind"], "function")
        self.assertEqual(symbols["describeInput"]["return_type"], "string")


class InodeStoreTests(unittest.TestCase):
    def test_build_inode_schema_and_addressing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _copy_fixture_tree(Path(tmp))
            inode = build_inode(repo, "src/ui/components/Form.tsx")
            validate_document(inode, "context-inode.schema.json")
            self.assertTrue(inode["inode_id"].startswith("ino-"))
            self.assertEqual(inode["inode_id"], inode_id_for(inode["content_hash"]))
            self.assertEqual(inode["language"], "tsx")
            self.assertEqual(inode["module"], "src/ui")
            self.assertIn("FormProps", inode["exports"])
            self.assertIn("buildForm", inode["exports"])

    def test_build_store_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _copy_fixture_tree(Path(tmp))
            store_a = Path(tmp) / "store-a"
            store_b = Path(tmp) / "store-b"
            index_a = build_store(repo, output_dir=store_a)
            index_b = build_store(repo, output_dir=store_b)
            self.assertEqual(index_a, index_b)
            files_a = sorted(p.name for p in store_a.glob("*.json"))
            files_b = sorted(p.name for p in store_b.glob("*.json"))
            self.assertEqual(files_a, files_b)
            for name in files_a:
                self.assertEqual((store_a / name).read_bytes(), (store_b / name).read_bytes())
            self.assertEqual(index_a["file_count"], 5)
            self.assertGreaterEqual(index_a["inode_count"], 5)

    def test_find_stale_modified_and_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _copy_fixture_tree(Path(tmp))
            store = Path(tmp) / "store"
            build_store(repo, output_dir=store)
            self.assertEqual(find_stale(repo, store_dir=store), [])

            target = repo / "src" / "ui" / "utils" / "validate.ts"
            target.write_text(target.read_text(encoding="utf-8") + "\n// touched\n", encoding="utf-8")
            stale = find_stale(repo, store_dir=store)
            self.assertEqual(stale, [{"path": "src/ui/utils/validate.ts", "reason": "modified"}])

            target.unlink()
            stale = find_stale(repo, store_dir=store)
            self.assertEqual(stale, [{"path": "src/ui/utils/validate.ts", "reason": "deleted"}])

    def test_inode_for_path_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _copy_fixture_tree(Path(tmp))
            store = Path(tmp) / "store"
            build_store(repo, output_dir=store)
            inode = inode_for_path(repo, "src/worker/processor.py", store_dir=store)
            self.assertIsNotNone(inode)
            self.assertEqual(inode["language"], "python")
            self.assertIsNone(inode_for_path(repo, "src/nope.py", store_dir=store))

    def test_module_route_mapping(self) -> None:
        self.assertEqual(module_route_for("src/ui/components/Form.tsx"), "src/ui")
        self.assertEqual(module_route_for("orchestrator/review/pipeline.py"), "orchestrator/review")


class WalkerTests(unittest.TestCase):
    def _build(self, tmp: str) -> tuple[Path, Path, Path]:
        repo = _copy_fixture_tree(Path(tmp))
        store = Path(tmp) / "store"
        context = Path(tmp) / "context"
        build_store(repo, output_dir=store)
        derive_context_tree(repo, store_dir=store, output_dir=context)
        return repo, store, context

    def test_walk_resolves_sequentially(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, context = self._build(tmp)
            result = walk_route(repo, "src/ui", context_root=context)
            validate_document(result, "context-route.schema.json")
            self.assertTrue(result["resolved"])
            self.assertEqual([step["segment"] for step in result["steps"]], ["src", "ui"])
            self.assertTrue(all(step["found"] for step in result["steps"]))
            self.assertEqual(len(result["steps"]), 2)
            self.assertEqual(len(result["inode_refs"]), 3)

    def test_walk_missing_segment_stops(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, context = self._build(tmp)
            result = walk_route(repo, "src/nonexistent/deep", context_root=context)
            validate_document(result, "context-route.schema.json")
            self.assertFalse(result["resolved"])
            self.assertEqual(result["failed_segment"], "nonexistent")
            self.assertEqual(len(result["steps"]), 2)
            self.assertEqual(result["inode_refs"], [])

    def test_walk_scopes_inode_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, store, context = self._build(tmp)
            index = load_index(repo, store_dir=store)
            api_result = walk_route(repo, "src/api", context_root=context)
            worker_result = walk_route(repo, "src/worker", context_root=context)
            api_refs = set(api_result["inode_refs"])
            worker_refs = set(worker_result["inode_refs"])
            self.assertEqual(api_refs.isdisjoint(worker_refs), True)
            api_inode = index["files"]["src/api/client.ts"]["inode_id"]
            self.assertIn(api_inode, api_refs)


class CliTests(unittest.TestCase):
    def test_build_and_walk_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _copy_fixture_tree(Path(tmp))
            store = Path(tmp) / "store"
            context = Path(tmp) / "context"

            build = subprocess.run(
                [
                    str(BUILD_CLI),
                    "--repo-root", str(repo),
                    "--output", str(store),
                    "--context-output", str(context),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            summary = json.loads(build.stdout)
            self.assertTrue(summary["ok"])
            self.assertEqual(summary["files_indexed"], 5)

            walk = subprocess.run(
                [
                    str(WALK_CLI),
                    "--repo-root", str(repo),
                    "--route", "src/ui",
                    "--context-root", str(context),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(walk.returncode, 0, walk.stderr)
            route = json.loads(walk.stdout)
            self.assertTrue(route["resolved"])

            check = subprocess.run(
                [str(BUILD_CLI), "--repo-root", str(repo), "--output", str(store), "--check"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(check.returncode, 0, check.stderr)

            target = repo / "src" / "api" / "client.ts"
            target.write_text(target.read_text(encoding="utf-8") + "\n// drift\n", encoding="utf-8")
            recheck = subprocess.run(
                [str(BUILD_CLI), "--repo-root", str(repo), "--output", str(store), "--check"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(recheck.returncode, 1)
            self.assertIn("stale", recheck.stderr)


if __name__ == "__main__":
    unittest.main()
