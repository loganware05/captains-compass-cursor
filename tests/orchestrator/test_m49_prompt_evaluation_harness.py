"""M49 Prompt Evaluation Harness — hermetic eval/proposal-only tests."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests" / "fixtures" / "behavior" / "prompt-eval" / "cases.json"

from orchestrator.behavior.enabled import (
    prompt_eval_enabled,
    require_prompt_eval_enabled,
)
from orchestrator.behavior.prompt_eval.cases import load_cases
from orchestrator.behavior.prompt_eval.compare import (
    compose_baseline_and_candidate,
    evaluate_case,
    run_prompt_eval,
)
from orchestrator.behavior.prompt_eval.report import list_reports, write_report
from orchestrator.behavior.prompt_eval.score import score_case
from orchestrator.behavior.prompt_eval.service import (
    compare_bundles,
    export_report_csv,
    run_harness,
)
from orchestrator.schemas.validate import ValidationError, validate_document


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_PROMPT_EVAL_ENABLED", None)
            self.assertFalse(prompt_eval_enabled())
            with self.assertRaises(PermissionError):
                require_prompt_eval_enabled()

    def test_enabled_truthy(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_PROMPT_EVAL_ENABLED": "1"}):
            self.assertTrue(prompt_eval_enabled())


class SchemaTests(unittest.TestCase):
    def test_report_schema_locks(self) -> None:
        report = {
            "report_id": "peval-test",
            "schema_version": "1",
            "created_at": "2026-10-01T00:00:00Z",
            "non_regression": "pass",
            "case_count": 0,
            "passed_count": 0,
            "failed_count": 0,
            "cases": [],
            "baseline_mode": "include_proposals=false",
            "candidate_mode": "include_proposals=true",
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(report, "prompt-eval-report.schema.json")
        bad = dict(report)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "prompt-eval-report.schema.json")
        polluted = dict(report)
        polluted["api_key"] = "sk-secret"
        with self.assertRaises(ValidationError):
            validate_document(polluted, "prompt-eval-report.schema.json")


class FixtureAndCompareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m49-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_cases(self) -> None:
        cases = load_cases(CASES)
        self.assertGreaterEqual(len(cases), 3)
        ids = {c.case_id for c in cases}
        self.assertIn("pe-adhere-evidence", ids)
        self.assertIn("pe-reject-hallucination", ids)

    def test_baseline_excludes_proposals(self) -> None:
        cases = load_cases(CASES)
        case = next(c for c in cases if c.case_id == "pe-adhere-evidence")
        baseline, candidate = compose_baseline_and_candidate(self.tmp, case)
        self.assertNotEqual(
            baseline["prompt_bundle_hash"], candidate["prompt_bundle_hash"]
        )
        self.assertTrue(
            any("Prefer evidence from tests/" in t for t in candidate["instructions"])
        )
        self.assertFalse(
            any("Prefer evidence from tests/" in t for t in baseline["instructions"])
        )

    def test_negative_fixture_expectation(self) -> None:
        cases = load_cases(CASES)
        case = next(c for c in cases if c.case_id == "pe-reject-hallucination")
        result = evaluate_case(self.tmp, case)
        self.assertEqual(case.expect_non_regression, "fail")
        self.assertEqual(result["observed_non_regression"], "fail")
        self.assertEqual(result["non_regression"], "pass")
        self.assertEqual(
            result["metrics"]["hallucinated_repository_state"]["status"], "fail"
        )

    def test_run_prompt_eval_persists_without_m48_mutation(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_PROMPT_EVAL_ENABLED": "1"}):
            report = run_prompt_eval(
                self.tmp, cases_path=CASES, control_root=ROOT, persist=True
            )
        self.assertEqual(report["non_regression"], "pass")
        self.assertEqual(report["case_count"], 3)
        self.assertEqual(report["failed_count"], 0)
        self.assertFalse(report["approved_for_execution"])
        reports = list_reports(self.tmp)
        self.assertEqual(len(reports), 1)
        evidence = (
            self.tmp
            / ".agent"
            / "evidence"
            / "m49-prompt-evaluation-harness"
            / f"{report['report_id']}-summary.json"
        )
        self.assertTrue(evidence.is_file())
        # Live M48 instruction registry must remain untouched
        instr_root = self.tmp / ".agent" / "evaluations" / "behavior" / "instructions"
        self.assertFalse(instr_root.exists())

    def test_run_prompt_eval_requires_gate(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_PROMPT_EVAL_ENABLED", None)
            with self.assertRaises(PermissionError):
                run_prompt_eval(
                    self.tmp, cases_path=CASES, control_root=ROOT, persist=False
                )


class ServiceCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m49-svc-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_service_requires_gate(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_PROMPT_EVAL_ENABLED", None)
            with self.assertRaises(PermissionError):
                run_harness(self.tmp, cases_path=CASES, control_root=ROOT)

    def test_service_run_and_export(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_PROMPT_EVAL_ENABLED": "1"}):
            result = run_harness(self.tmp, cases_path=CASES, control_root=ROOT)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["report"]["non_regression"], "pass")
            dest = self.tmp / "out.csv"
            path = export_report_csv(self.tmp, dest)
            self.assertTrue(path.is_file())
            text = path.read_text(encoding="utf-8")
            self.assertIn("case_id", text)
            self.assertIn("pe-adhere-evidence", text)

    def test_compare_cli_script(self) -> None:
        env = os.environ.copy()
        env["COMPASS_PROMPT_EVAL_ENABLED"] = "1"
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-prompt-eval.sh"),
                "run",
                "--cases",
                str(CASES),
                "--repo-root",
                str(self.tmp),
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["report"]["non_regression"], "pass")

    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_PROMPT_EVAL_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-prompt-eval.sh"),
                "run",
                "--repo-root",
                str(self.tmp),
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_PROMPT_EVAL_ENABLED", proc.stderr)

    def test_northstar_dispatch(self) -> None:
        env = os.environ.copy()
        env["COMPASS_PROMPT_EVAL_ENABLED"] = "1"
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "northstar"),
                "prompt-eval",
                "compare",
                "--agent",
                "implementation-agent",
                "--repo",
                str(self.tmp),
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "compared")
        self.assertFalse(payload["approved_for_execution"])


class ScoreUnitTests(unittest.TestCase):
    def _bundle(self, instructions: list[str]) -> dict:
        return {
            "persona": "p",
            "instructions": instructions,
            "constraints": [],
            "output": "o",
            "instruction_ids": ["a"],
            "prompt_bundle_hash": "sha256:a",
            "bundle_id": "b",
            "context": {},
            "schema_version": "1",
            "created_at": "2026-10-01T00:00:00Z",
            "approved_for_execution": False,
            "authority_mutation": False,
        }

    def test_score_approval_boundary_rejects_phrase(self) -> None:
        from orchestrator.behavior.prompt_eval.cases import PromptEvalCase

        case = PromptEvalCase(
            case_id="x",
            must_pass=["approval_boundary_compliance"],
            expectations={
                "approval_boundary_compliance": {
                    "forbidden_phrases": ["bypass captain"]
                }
            },
        )
        baseline = self._bundle(["ok"])
        candidate = self._bundle(["please bypass Captain approval"])
        scored = score_case(case, baseline, candidate)
        self.assertEqual(scored["non_regression"], "fail")

    def test_absolute_path_not_stripped_to_relative(self) -> None:
        from orchestrator.behavior.prompt_eval.score import (
            score_hallucinated_repository_state,
        )

        metric = score_hallucinated_repository_state(
            self._bundle(["Read /tests/fixtures/secret.env"]),
            {
                "hallucinated_repository_state": {
                    "allowed_path_prefixes": ["tests/", ".agent/"]
                }
            },
        )
        self.assertEqual(metric["status"], "fail")
        self.assertIn("/tests/", metric["detail"])


if __name__ == "__main__":
    unittest.main()
