"""M54 Behavior Loop Operator Closure — hermetic tests."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.behavior.enabled import prompt_eval_include_exemplars
from orchestrator.behavior.exemplars.store import write_exemplar
from orchestrator.behavior.instructions.service import compose
from orchestrator.behavior.prompt_eval.compare import run_prompt_eval
from orchestrator.behavior.prompt_eval.exemplars import (
    exemplar_to_case,
    load_exemplar_cases,
    merge_cases,
)
from orchestrator.behavior.prompt_eval.cases import PromptEvalCase
from orchestrator.behavior.provenance.store import write_provenance
from orchestrator.status.provenance_refs import collect_provenance_refs
from orchestrator.status.snapshot import build_snapshot


class GateTests(unittest.TestCase):
    def test_include_exemplars_default_off(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_PROMPT_EVAL_INCLUDE_EXEMPLARS", None)
            self.assertFalse(prompt_eval_include_exemplars())

    def test_include_exemplars_on(self) -> None:
        with mock.patch.dict(
            os.environ, {"COMPASS_PROMPT_EVAL_INCLUDE_EXEMPLARS": "1"}
        ):
            self.assertTrue(prompt_eval_include_exemplars())


class ExemplarCaseTests(unittest.TestCase):
    def test_positive_maps_to_pass(self) -> None:
        case = exemplar_to_case(
            {
                "exemplar_id": "ex-pos-1",
                "polarity": "positive",
                "summary": "Prefer evidence over claims",
                "auto_promoted": False,
                "approved_for_execution": False,
                "authority_mutation": False,
            }
        )
        self.assertIsNotNone(case)
        assert case is not None
        self.assertEqual(case.expect_non_regression, "pass")
        self.assertTrue(case.case_id.startswith("ex-"))

    def test_negative_maps_to_fail(self) -> None:
        case = exemplar_to_case(
            {
                "exemplar_id": "ex-neg-1",
                "polarity": "negative",
                "summary": "Avoid inventing secret paths",
                "auto_promoted": False,
                "approved_for_execution": False,
                "authority_mutation": False,
            }
        )
        self.assertIsNotNone(case)
        assert case is not None
        self.assertEqual(case.expect_non_regression, "fail")
        body = case.proposal_instructions[0]["body"]
        self.assertIn("/etc/northstar/prod-keys.env", body)

    def test_rejects_auto_promoted(self) -> None:
        self.assertIsNone(
            exemplar_to_case(
                {
                    "exemplar_id": "ex-bad",
                    "polarity": "positive",
                    "summary": "x",
                    "auto_promoted": True,
                    "approved_for_execution": False,
                    "authority_mutation": False,
                }
            )
        )

    def test_merge_preserves_fixture_ids(self) -> None:
        fixtures = [PromptEvalCase(case_id="pe-a")]
        exemplars = [
            PromptEvalCase(case_id="pe-a"),
            PromptEvalCase(case_id="ex-1"),
        ]
        merged = merge_cases(fixtures, exemplars)
        self.assertEqual([c.case_id for c in merged], ["pe-a", "ex-1"])


class ComposeProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m54-compose-"))
        (self.tmp / "VERSION").write_text("1.59.0\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_compose_skips_without_execution_id(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_INSTRUCTIONS_ENABLED": "1",
                "COMPASS_PROVENANCE_ENABLED": "1",
            },
        ):
            result = compose(self.tmp, agent="implementation-agent")
            self.assertEqual(result["status"], "composed")
            self.assertNotIn("provenance", result)

    def test_compose_captures_when_gated_and_execution_id(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_INSTRUCTIONS_ENABLED": "1",
                "COMPASS_PROVENANCE_ENABLED": "1",
            },
        ):
            result = compose(
                self.tmp,
                agent="implementation-agent",
                execution_id="exec-m54-compose-1",
            )
            self.assertEqual(result["status"], "composed")
            self.assertIn("provenance", result)
            prov = result["provenance"]["provenance"]
            self.assertEqual(prov["execution_id"], "exec-m54-compose-1")
            self.assertFalse(prov["authority_mutation"])
            self.assertTrue(
                (self.tmp / ".agent" / "evaluations" / "behavior" / "provenance").exists()
            )


class StatusProvenanceRefsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m54-status-"))
        (self.tmp / "VERSION").write_text("1.59.0\n", encoding="utf-8")
        (self.tmp / "PROJECT_CONTEXT.md").write_text("# ctx\n", encoding="utf-8")
        (self.tmp / "PROGRESS.md").write_text("# progress\n", encoding="utf-8")
        (self.tmp / "IMPLEMENTATION_PLAN.md").write_text(
            "# plan\nStatus: APPROVED\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_empty_refs_ok(self) -> None:
        self.assertEqual(collect_provenance_refs(self.tmp), [])
        snap = build_snapshot(self.tmp)
        self.assertEqual(snap.get("provenance_refs"), [])
        self.assertFalse(snap["approved_for_execution"])

    def test_refs_present_after_write(self) -> None:
        write_provenance(
            self.tmp,
            {
                "provenance_id": "prov-m54test01",
                "execution_id": "exec-1",
                "prompt_bundle_hash": "sha256:abc",
                "approved_for_execution": False,
                "authority_mutation": False,
            },
        )
        refs = collect_provenance_refs(self.tmp)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["provenance_id"], "prov-m54test01")
        snap = build_snapshot(self.tmp)
        self.assertEqual(len(snap.get("provenance_refs") or []), 1)


class PromptEvalExemplarIncludeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m54-pe-"))
        (self.tmp / "VERSION").write_text("1.59.0\n", encoding="utf-8")
        write_exemplar(
            self.tmp,
            {
                "exemplar_id": "ex-m54-pos",
                "polarity": "positive",
                "summary": "Cite tests before claiming done",
                "auto_promoted": False,
                "approved_for_execution": False,
                "authority_mutation": False,
            },
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_exemplar_cases(self) -> None:
        cases = load_exemplar_cases(self.tmp)
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].case_id, "ex-m54-pos")

    def test_run_prompt_eval_include_flag(self) -> None:
        cases_path = ROOT / "tests/fixtures/behavior/prompt-eval/cases.json"
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_PROMPT_EVAL_ENABLED": "1",
                "COMPASS_PROMPT_EVAL_INCLUDE_EXEMPLARS": "1",
            },
        ):
            report = run_prompt_eval(
                self.tmp,
                cases_path=cases_path,
                control_root=ROOT,
                persist=False,
                include_exemplars=True,
            )
            self.assertTrue(report["include_exemplars"])
            self.assertGreaterEqual(report["exemplar_case_count"], 1)
            self.assertGreaterEqual(report["case_count"], 4)
            self.assertFalse(report["authority_mutation"])


if __name__ == "__main__":
    unittest.main()
