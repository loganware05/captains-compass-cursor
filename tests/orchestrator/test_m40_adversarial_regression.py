"""M40 adversarial-remediation regression tests.

Each test pins a defect class found by the adversarial review of the initial
M40 implementation (H1–H6, M7–M13, L17/L18). Fixture corpus:
tests/fixtures/context-edgecases/.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from orchestrator.context.extract import _parse_params, extract_typescript
from orchestrator.context.inodes import build_store, iter_source_files
from orchestrator.context.walker import ContextWalkError, derive_context_tree, walk_route
from orchestrator.dependency_graph import resolve_import
from orchestrator.review.boundary import _call_sites, emit_boundary_candidates
from orchestrator.schemas.validate import ValidationError, validate_document

ROOT = Path(__file__).resolve().parents[2]
EDGE_SRC = ROOT / "tests" / "fixtures" / "context-edgecases" / "src"
CORE_SRC = ROOT / "tests" / "fixtures" / "context" / "src"


def _repo(tmp: Path, src: Path = EDGE_SRC) -> Path:
    repo = tmp / "repo"
    shutil.copytree(src, repo / "src")
    build_store(repo)
    derive_context_tree(repo)
    return repo


class H1ExtractorCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = extract_typescript((EDGE_SRC / "ui" / "lib.ts").read_text(encoding="utf-8"))
        cls.symbols = {s["name"]: s for s in cls.result["symbols"]}

    def test_generic_function_extracted(self) -> None:
        identity = self.symbols["identity"]
        self.assertEqual(identity["kind"], "function")
        self.assertTrue(identity["exported"])
        self.assertEqual([p["name"] for p in identity["params"]], ["value"])

    def test_default_export_function_extracted(self) -> None:
        widget = self.symbols["Widget"]
        self.assertTrue(widget["exported"])
        self.assertEqual([p["name"] for p in widget["params"]], ["props"])

    def test_one_liner_body_extracted(self) -> None:
        self.assertIn("sizeOf", self.symbols)

    def test_generic_param_type_is_one_param(self) -> None:
        size_of = self.symbols["sizeOf"]
        self.assertEqual(len(size_of["params"]), 1)
        self.assertEqual(size_of["params"][0]["type"], "Map<string, number>")

    def test_rest_param_marked_variadic(self) -> None:
        collect = self.symbols["collect"]
        self.assertEqual(len(collect["params"]), 2)
        self.assertFalse(collect["params"][0]["variadic"])
        self.assertTrue(collect["params"][1]["variadic"])
        self.assertTrue(collect["params"][1]["optional"])

    def test_class_extracted_with_methods(self) -> None:
        store = self.symbols["FormStore"]
        self.assertEqual(store["kind"], "class")
        methods = [f["name"] for f in store["fields"]]
        self.assertIn("add", methods)
        self.assertIn("count", methods)

    def test_named_reexport_lands_in_exports(self) -> None:
        exports = {s["name"] for s in self.result["symbols"] if s.get("exported")}
        self.assertIn("InputProps", exports)
        reexport = self.symbols["InputProps"]
        self.assertEqual(reexport["kind"], "reexport")

    def test_multi_line_import_parsed(self) -> None:
        source = "import {\n  FormProps,\n  buildForm,\n} from './Form';\n"
        result = extract_typescript(source)
        self.assertEqual(result["imports"][0]["module"], "./Form")
        self.assertEqual(result["imports"][0]["names"], ["FormProps", "buildForm"])

    def test_m13_type_alias_literals_elided(self) -> None:
        token = self.symbols["ApiToken"]
        self.assertNotIn("placeholder-not-a-secret", token["signature"])
        self.assertIn("…", token["signature"])

    def test_h2_default_with_comma_single_param(self) -> None:
        params = _parse_params("a: string, b: string = 'x,y'")
        self.assertEqual(len(params), 2)
        self.assertEqual(params[1]["name"], "b")
        self.assertTrue(params[1]["optional"])


class H3H4M11CallSiteTests(unittest.TestCase):
    def test_multi_line_call_argc(self) -> None:
        lines = ["const form = buildForm(", "  title,", "  fields,", ");"]
        sites = _call_sites(lines, {"buildForm"})
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0]["argc"], 2)

    def test_foreach_marks_loop_context(self) -> None:
        lines = ["items.forEach((item) => process(item));"]
        sites = _call_sites(lines, {"process"})
        self.assertEqual(sites[0]["in_loop"], True)

    def test_single_line_for_loop_marks_call(self) -> None:
        lines = ["for (const x of xs) process(x);"]
        sites = _call_sites(lines, {"process"})
        self.assertEqual(sites[0]["in_loop"], True)

    def test_method_call_not_matched(self) -> None:
        lines = ["const y = formBuilder.buildForm(title);"]
        self.assertEqual(_call_sites(lines, {"buildForm"}), [])

    def test_comment_and_string_mentions_not_matched(self) -> None:
        lines = [
            '// TODO: call buildForm(title, fields, extras) later',
            'const hint = "run buildForm(a, b, c) first";',
        ]
        self.assertEqual(_call_sites(lines, {"buildForm"}), [])

    def test_generic_call_syntax_matched(self) -> None:
        lines = ["const out = identity<number>(size);"]
        sites = _call_sites(lines, {"identity"})
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0]["argc"], 1)


class H5H6BoundaryDirectionTests(unittest.TestCase):
    def test_callee_side_removal_flags_unchanged_importer(self) -> None:
        """Diff deletes validateForm from validate.ts; unchanged client.ts (src/api)
        imports it cross-boundary and must be flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = _repo(Path(tmp), CORE_SRC)
            diff = "\n".join(
                [
                    "diff --git a/src/ui/utils/validate.ts b/src/ui/utils/validate.ts",
                    "--- a/src/ui/utils/validate.ts",
                    "+++ b/src/ui/utils/validate.ts",
                    "@@ -8,10 +8,3 @@",
                    "-/** @complexity O(N) */",
                    "-export function validateForm(fields: InputProps[]): string[] {",
                    "-  const errors: string[] = [];",
                    "-  for (const field of fields) {",
                    "-    if (field.required && !field.label) {",
                    "-      errors.push(field.name);",
                    "-    }",
                    "-  }",
                    "-  return errors;",
                    "-}",
                    "",
                ]
            )
            candidates, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/ui/utils/validate.ts"],
                diff_text=diff,
            )
            ids = {c["id"] for c in candidates}
            self.assertIn("boundary-unknown-symbol-src/api/client.ts-validateForm", ids)

    def test_new_file_with_bad_import_flagged(self) -> None:
        """A brand-new file (absent from the store) is checked via added lines."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = _repo(Path(tmp), CORE_SRC)
            diff = "\n".join(
                [
                    "diff --git a/src/api/newhandler.ts b/src/api/newhandler.ts",
                    "--- /dev/null",
                    "+++ b/src/api/newhandler.ts",
                    "@@ -0,0 +1,2 @@",
                    "+import { nonexistent } from '../ui/utils/validate';",
                    "+export const x = nonexistent();",
                    "",
                ]
            )
            candidates, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/api/newhandler.ts"],
                diff_text=diff,
            )
            ids = {c["id"] for c in candidates}
            self.assertIn("boundary-unknown-symbol-src/api/newhandler.ts-nonexistent", ids)

    def test_both_sides_change_no_false_positive(self) -> None:
        """Hard-link pattern: callee gains export + caller imports it (store=base)."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = _repo(Path(tmp), CORE_SRC)
            diff = "\n".join(
                [
                    "diff --git a/src/ui/utils/validate.ts b/src/ui/utils/validate.ts",
                    "--- a/src/ui/utils/validate.ts",
                    "+++ b/src/ui/utils/validate.ts",
                    "@@ -20,3 +20,6 @@",
                    "+/** @complexity O(1) */",
                    "+export function addedHelper(value: string): boolean {",
                    "+  return value.length > 0;",
                    "+}",
                    "diff --git a/src/api/client.ts b/src/api/client.ts",
                    "--- a/src/api/client.ts",
                    "+++ b/src/api/client.ts",
                    "@@ -1,4 +1,4 @@",
                    "-import { validateForm } from '../ui/utils/validate';",
                    "+import { validateForm, addedHelper } from '../ui/utils/validate';",
                    "",
                ]
            )
            candidates, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/ui/utils/validate.ts", "src/api/client.ts"],
                diff_text=diff,
            )
            self.assertEqual(candidates, [])

    def test_m10_duplicate_ids_get_occurrence_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _repo(Path(tmp), CORE_SRC)
            diff = "\n".join(
                [
                    "diff --git a/src/api/client.ts b/src/api/client.ts",
                    "--- a/src/api/client.ts",
                    "+++ b/src/api/client.ts",
                    "@@ -14,3 +14,5 @@",
                    "+export function a(title: string): FormProps {",
                    "+  return buildForm(title);",
                    "+}",
                    "+export function b(title: string): FormProps {",
                    "+  return buildForm(title);",
                    "+}",
                    "",
                ]
            )
            candidates, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/api/client.ts"],
                diff_text=diff,
            )
            arity = [c for c in candidates if c["id"].startswith("boundary-arity")]
            self.assertEqual(len(arity), 2)
            self.assertNotEqual(arity[0]["id"], arity[1]["id"])

    def test_edgecase_clean_corpus_zero_findings(self) -> None:
        """Generics/defaults/variadic/class/re-export corpus: no false positives."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = _repo(Path(tmp), EDGE_SRC)
            diff = "\n".join(
                [
                    "diff --git a/src/api/caller.ts b/src/api/caller.ts",
                    "--- a/src/api/caller.ts",
                    "+++ b/src/api/caller.ts",
                    "@@ -8,3 +8,6 @@",
                    "+export function rerun(opts: Map<string, number>): number {",
                    "+  return sizeOf(opts) + collect('a', 1, 2).length;",
                    "+}",
                    "",
                ]
            )
            candidates, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/api/caller.ts"],
                diff_text=diff,
            )
            self.assertEqual(candidates, [])


class M7M8WalkerHardeningTests(unittest.TestCase):
    def test_deleted_module_route_stops_resolving(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _repo(Path(tmp), CORE_SRC)
            self.assertTrue(walk_route(repo, "src/worker")["resolved"])
            (repo / "src" / "worker" / "processor.py").unlink()
            build_store(repo)
            derive_context_tree(repo)
            result = walk_route(repo, "src/worker")
            self.assertFalse(result["resolved"])

    def test_traversal_segments_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _repo(Path(tmp), CORE_SRC)
            with self.assertRaises(ContextWalkError):
                walk_route(repo, "../../../outside")
            with self.assertRaises(ContextWalkError):
                walk_route(repo, "src/../worker")


class M12SymlinkTests(unittest.TestCase):
    def test_symlinked_files_not_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _repo(Path(tmp), CORE_SRC)
            outside = Path(tmp) / "outside.py"
            outside.write_text("def outside_fn():\n    pass\n", encoding="utf-8")
            link = repo / "src" / "linked.py"
            link.symlink_to(outside)
            paths = list(iter_source_files(repo))
            self.assertNotIn("src/linked.py", paths)


class M9SchemaAnyOfTests(unittest.TestCase):
    def test_typed_dependency_schema_enforced(self) -> None:
        valid = {
            "id": "a",
            "objective": "x",
            "dependencies": [{"target": "b", "link": "hard", "contract": "c"}],
        }
        validate_document(valid, "task.schema.json")
        for bad in (
            {"id": "a", "objective": "x", "dependencies": [{"target": "b"}]},
            {"id": "a", "objective": "x", "dependencies": [{"target": "b", "link": "junction"}]},
            {"id": "a", "objective": "x", "dependencies": [42]},
            {"id": "a", "objective": "x", "dependencies": [{"target": "", "link": "hard"}]},
        ):
            with self.assertRaises(ValidationError, msg=json.dumps(bad)):
                validate_document(bad, "task.schema.json")


class L18ResolveTests(unittest.TestCase):
    def test_above_root_relative_import_unresolvable(self) -> None:
        indexed = {"x.py", "a/b.py"}
        self.assertIsNone(resolve_import("a/b.py", "../../../x", indexed))


if __name__ == "__main__":
    unittest.main()
