"""M40 WS4 — cross-boundary review gate tests (precision = 1.0 on fixtures)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.context.inodes import build_store
from orchestrator.review.boundary import (
    _added_lines_by_file,
    _call_sites,
    emit_boundary_candidates,
)
from orchestrator.review.pipeline import run_code_review

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SRC = ROOT / "tests" / "fixtures" / "context" / "src"
BOUNDARY_FIXTURES = ROOT / "tests" / "fixtures" / "code-review" / "boundary"
BAD_DIFF = BOUNDARY_FIXTURES / "bad-change.diff"
CLEAN_DIFF = BOUNDARY_FIXTURES / "clean-change.diff"
EMPTY_CANDIDATES = BOUNDARY_FIXTURES / "empty-candidates.json"
REVIEW_CLI = ROOT / "scripts" / "run-code-review.sh"


def _fixture_repo(tmp: Path) -> tuple[Path, Path]:
    repo = tmp / "repo"
    shutil.copytree(FIXTURE_SRC, repo / "src")
    store = repo / ".agent" / "inodes"
    build_store(repo, output_dir=store)
    return repo, store


class AddedLinesTests(unittest.TestCase):
    def test_parses_added_lines_per_file(self) -> None:
        added = _added_lines_by_file(BAD_DIFF.read_text(encoding="utf-8"))
        self.assertIn("src/api/client.ts", added)
        lines = added["src/api/client.ts"]
        self.assertTrue(any("deleteForm" in line for line in lines))
        self.assertFalse(any(line.startswith("-") for line in lines))

    def test_call_sites_argc_and_loop_context(self) -> None:
        lines = [
            "export function validateAll(forms: FormProps[]): string[] {",
            "  for (const form of forms) {",
            "    const errs = validateForm(form.fields);",
            "    const made = buildForm(title);",
            "  }",
            "}",
            "const ok = validateForm(a, b);",
        ]
        sites = {site["name"]: site for site in _call_sites(lines, {"validateForm", "buildForm"})}
        self.assertEqual(sites["buildForm"]["argc"], 1)
        self.assertTrue(sites["buildForm"]["in_loop"])
        in_loop_validate = [
            site for site in _call_sites(lines, {"validateForm"}) if site["in_loop"]
        ]
        self.assertEqual(len(in_loop_validate), 1)
        self.assertEqual(in_loop_validate[0]["argc"], 1)


class BoundaryEmitterTests(unittest.TestCase):
    def test_absent_store_skips_with_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(FIXTURE_SRC, repo / "src")
            candidates, notes = emit_boundary_candidates(
                repo, changed_paths=["src/api/client.ts"], diff_text=""
            )
            self.assertEqual(candidates, [])
            self.assertIn("absent", notes[0])

    def test_stale_store_skips_with_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = _fixture_repo(Path(tmp))
            target = repo / "src" / "ui" / "utils" / "validate.ts"
            with target.open("a", encoding="utf-8") as handle:
                handle.write("\n// drift after indexing\n")
            candidates, notes = emit_boundary_candidates(
                repo, changed_paths=["src/api/client.ts"], diff_text=""
            )
            self.assertEqual(candidates, [])
            self.assertIn("stale", notes[0])

    def test_bad_diff_yields_three_seeded_violations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = _fixture_repo(Path(tmp))
            candidates, notes = emit_boundary_candidates(
                repo,
                changed_paths=["src/api/client.ts"],
                diff_text=BAD_DIFF.read_text(encoding="utf-8"),
            )
            ids = {candidate["id"] for candidate in candidates}
            self.assertIn("boundary-unknown-symbol-src/api/client.ts-deleteForm", ids)
            self.assertIn("boundary-arity-src/api/client.ts-buildForm", ids)
            self.assertIn("boundary-complexity-src/api/client.ts-validateForm", ids)
            self.assertEqual(len(candidates), 3)
            for candidate in candidates:
                self.assertEqual(candidate["category"], "boundary")
                self.assertEqual(len(candidate["evidence_paths"]), 2)
            self.assertIn("1 changed file(s) checked", notes[-1])

    def test_clean_diff_yields_zero_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = _fixture_repo(Path(tmp))
            candidates, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/api/client.ts"],
                diff_text=CLEAN_DIFF.read_text(encoding="utf-8"),
            )
            self.assertEqual(candidates, [])

    def test_intra_module_imports_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = _fixture_repo(Path(tmp))
            # validate.ts imports InputProps from ../components/Input — same route (src/ui).
            candidates, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/ui/utils/validate.ts"],
                diff_text="",
            )
            self.assertEqual(candidates, [])


class BoundaryPrecisionTests(unittest.TestCase):
    """AC5: precision = TP/(TP+FP) = 1.0 on the fixture corpus."""

    def test_precision_is_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = _fixture_repo(Path(tmp))
            true_positives, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/api/client.ts"],
                diff_text=BAD_DIFF.read_text(encoding="utf-8"),
            )
            false_positives, _ = emit_boundary_candidates(
                repo,
                changed_paths=["src/api/client.ts"],
                diff_text=CLEAN_DIFF.read_text(encoding="utf-8"),
            )
            tp = len(true_positives)
            fp = len(false_positives)
            self.assertEqual(tp, 3)
            self.assertEqual(fp, 0)
            precision = tp / (tp + fp)
            self.assertEqual(precision, 1.0)


class PipelineIntegrationTests(unittest.TestCase):
    def test_review_pipeline_includes_boundary_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = _fixture_repo(Path(tmp))
            result = run_code_review(
                repo_root=repo,
                diff_text=BAD_DIFF.read_text(encoding="utf-8"),
                changed_paths=["src/api/client.ts"],
                candidates_path=EMPTY_CANDIDATES,
                plan_id="m40-boundary-test",
            )
            boundary = result["boundary"]
            self.assertTrue(boundary["enabled"])
            self.assertEqual(boundary["candidates"], 3)
            self.assertEqual(result["candidates_source"], "fixtures+boundary")
            boundary_findings = [
                f for f in result["findings"] if f.get("category") == "boundary"
            ]
            self.assertEqual(len(boundary_findings), 3)
            self.assertTrue(all(f["status"] == "verified" for f in boundary_findings))
            self.assertEqual(
                result["report"]["provenance"]["boundary"]["candidates"], 3
            )

    def test_review_pipeline_skips_cleanly_without_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(FIXTURE_SRC, repo / "src")
            result = run_code_review(
                repo_root=repo,
                diff_text=CLEAN_DIFF.read_text(encoding="utf-8"),
                changed_paths=["src/api/client.ts"],
                candidates_path=EMPTY_CANDIDATES,
                plan_id="m40-boundary-skip-test",
            )
            self.assertIn("absent", result["boundary"]["notes"][0])
            self.assertEqual(result["candidates_source"], "fixtures")

    def test_review_cli_boundary_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = _fixture_repo(Path(tmp))
            proc = subprocess.run(
                [
                    str(REVIEW_CLI),
                    "--repo-root", str(repo),
                    "--diff-file", str(BAD_DIFF),
                    "--changed", "src/api/client.ts",
                    "--candidates", str(EMPTY_CANDIDATES),
                    "--run-id", "m40-cli-boundary",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            import json

            summary = json.loads(proc.stdout)
            self.assertEqual(summary["boundary"]["candidates"], 3)
            self.assertEqual(summary["summary"]["verified"], 3)


if __name__ == "__main__":
    unittest.main()
