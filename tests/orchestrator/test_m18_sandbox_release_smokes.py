"""M18 sandbox release smokes — catalog, runner, closeout validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.release.sandbox_smokes import (
    RELEASE_SMOKE_CATALOG,
    SandboxSmokeError,
    interactive_smoke_catalog,
    run_automated_sandbox_smokes,
    validate_release_smoke_evidence,
    write_smoke_report,
)

ROOT = Path(__file__).resolve().parents[2]


class SandboxSmokeCatalogTests(unittest.TestCase):
    def test_catalog_has_automated_and_interactive(self) -> None:
        modes = {step.mode for step in RELEASE_SMOKE_CATALOG}
        self.assertIn("automated", modes)
        self.assertIn("interactive", modes)

    def test_interactive_catalog_matches_checklist(self) -> None:
        items = interactive_smoke_catalog()
        self.assertEqual(len(items), 8)
        self.assertEqual(items[0]["checklist_item"], 1)
        self.assertEqual(items[-1]["smoke_id"], "post-foundation-smokes")


class SandboxSmokeRunnerTests(unittest.TestCase):
    def test_run_with_mock_steps(self) -> None:
        def always_pass(control_root: Path, sandbox_root: Path) -> dict:
            return {"smoke_id": "mock", "passed": True, "detail": "ok"}

        with tempfile.TemporaryDirectory() as control_tmp, tempfile.TemporaryDirectory() as sandbox_tmp:
            control = Path(control_tmp)
            sandbox = Path(sandbox_tmp)
            (control / "VERSION").write_text("1.22.0\n", encoding="utf-8")
            checklist = control / "docs" / "evals" / "SANDBOX_BEHAVIORAL_CHECKLIST.md"
            checklist.parent.mkdir(parents=True)
            checklist.write_text("Post-foundation\n", encoding="utf-8")

            runners = {step.smoke_id: always_pass for step in RELEASE_SMOKE_CATALOG if step.mode == "automated"}
            report = run_automated_sandbox_smokes(control, sandbox, steps=runners)
            self.assertTrue(report["passed"])
            self.assertEqual(report["kind"], "sandbox-release-smoke-report")
            self.assertEqual(len(report["results"]), len(runners))

    def test_write_smoke_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.json"
            report = {"kind": "sandbox-release-smoke-report", "passed": True, "results": []}
            write_smoke_report(report, path)
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(loaded["passed"])


class SandboxSmokeValidationTests(unittest.TestCase):
    def test_validate_requires_automated_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with self.assertRaises(SandboxSmokeError):
                validate_release_smoke_evidence(repo, "1.22.0", require_interactive=False)

    def test_validate_passes_with_both_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            evidence = repo / ".agent" / "evidence" / "release-v1.22.0"
            evidence.mkdir(parents=True)
            automated = {
                "kind": "sandbox-release-smoke-report",
                "passed": True,
                "results": [{"smoke_id": "doctor-sandbox", "passed": True}],
            }
            interactive = {
                "kind": "sandbox-interactive-smoke-report",
                "passed": True,
                "checklist_results": [{"item": 1, "passed": True}],
            }
            (evidence / "sandbox-smokes-automated.json").write_text(
                json.dumps(automated), encoding="utf-8"
            )
            (evidence / "sandbox-smokes-interactive.json").write_text(
                json.dumps(interactive), encoding="utf-8"
            )
            result = validate_release_smoke_evidence(repo, "1.22.0")
            self.assertTrue(result["passed"])

    def test_validate_rejects_failed_automated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            evidence = repo / ".agent" / "evidence" / "release-v1.22.0"
            evidence.mkdir(parents=True)
            (evidence / "sandbox-smokes-automated.json").write_text(
                json.dumps({"passed": False}), encoding="utf-8"
            )
            with self.assertRaises(SandboxSmokeError):
                validate_release_smoke_evidence(repo, "1.22.0", require_interactive=False)


class SandboxSmokeIntegrationTests(unittest.TestCase):
    def test_behavioral_checklist_present_in_repo(self) -> None:
        path = ROOT / "docs" / "evals" / "SANDBOX_BEHAVIORAL_CHECKLIST.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Post-foundation", text)
        self.assertIn("run-sandbox-release-smokes", text)

    def test_release_scripts_exist(self) -> None:
        self.assertTrue((ROOT / "scripts" / "run-sandbox-release-smokes.sh").is_file())
        self.assertTrue((ROOT / "scripts" / "validate-sandbox-release-smokes.sh").is_file())


if __name__ == "__main__":
    unittest.main()
