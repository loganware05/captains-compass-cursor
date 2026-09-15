"""M33 / B5 precision ledger tests."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.review.precision import (
    DEFAULT_MIN_SAMPLE,
    PrecisionError,
    aggregate_precision,
    build_precision_ledger,
    build_priority_proposal,
    ledger_to_experiences,
    load_outcomes_bundle,
)
from orchestrator.routing.propose import build_routing_proposal
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "code-review" / "precision-outcomes.json"
M31_OUTCOMES = ROOT / ".agent" / "evidence" / "m31-finding-outcomes" / "outcomes.json"


class PrecisionMathTests(unittest.TestCase):
    def test_precision_excludes_deferred(self) -> None:
        rows = load_outcomes_bundle(FIXTURE)
        ledger = build_precision_ledger(rows, ledger_id="precision-test-math")
        validate_document(ledger, "precision-ledger.schema.json")
        by_key = {e["key"]: e for e in ledger["entries"]}
        sec = by_key["security-review"]
        self.assertEqual(sec["accepted"], 4)
        self.assertEqual(sec["rejected"], 1)
        self.assertEqual(sec["deferred"], 0)
        self.assertEqual(sec["decided"], 5)
        self.assertEqual(sec["precision"], 0.8)
        self.assertEqual(sec["key_kind"], "specialist")

        cr = by_key["code-reviewer"]
        self.assertEqual(cr["accepted"], 0)
        self.assertEqual(cr["rejected"], 1)
        self.assertEqual(cr["deferred"], 1)
        self.assertEqual(cr["decided"], 1)
        self.assertEqual(cr["precision"], 0.0)
        self.assertIs(ledger["captain_approval"], False)
        self.assertIs(ledger["locks"]["auto_apply"], False)

    def test_empty_outcomes_refuse(self) -> None:
        with self.assertRaises(PrecisionError):
            build_precision_ledger([])

    def test_unknown_skill_refuse(self) -> None:
        with self.assertRaises(PrecisionError):
            build_precision_ledger(
                [
                    {
                        "finding_id": "x",
                        "decision": "accepted",
                        "skill": "",
                        "run_id": "r1",
                    }
                ]
            )


class ExperienceSafetyTests(unittest.TestCase):
    def test_per_skill_experiences_do_not_blanket_success(self) -> None:
        rows = load_outcomes_bundle(FIXTURE)
        ledger = build_precision_ledger(rows, ledger_id="precision-test-exp")
        experiences = ledger_to_experiences(
            ledger, plan_id="b5-precision-ledger", source_instance="control-test"
        )
        by_skill = {e["skills_used"][0]: e for e in experiences}
        self.assertEqual(set(by_skill), {"security-review", "code-reviewer"})
        self.assertEqual(by_skill["security-review"]["outcome"], "partial")
        self.assertEqual(by_skill["code-reviewer"]["outcome"], "failed")
        self.assertEqual(by_skill["code-reviewer"]["skills_used"], ["code-reviewer"])

        # Low-precision skill must not earn a positive confidence delta from this Experience.
        proposal = build_routing_proposal([by_skill["code-reviewer"]])
        deltas = {d["skill_id"]: d["delta"] for d in proposal["skill_confidence_deltas"]}
        self.assertLessEqual(deltas.get("code-reviewer", 0), 0)


class PriorityProposalTests(unittest.TestCase):
    def test_insufficient_sample_refuses_proposal(self) -> None:
        rows = load_outcomes_bundle(M31_OUTCOMES)
        ledger = build_precision_ledger(
            rows,
            ledger_id="precision-test-small",
            min_sample_for_proposal=DEFAULT_MIN_SAMPLE,
        )
        with self.assertRaises(PrecisionError):
            build_priority_proposal(ledger)

    def test_emit_proposal_refuses_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with self.assertRaises(PrecisionError):
                aggregate_precision(
                    repo_root=repo,
                    outcomes=M31_OUTCOMES,
                    ledger_id="should-not-write",
                    emit_priority_proposal=True,
                    min_sample_for_proposal=5,
                    write_experience_lesson=True,
                    source_instance="control-test",
                )
            evidence = repo / ".agent" / "evidence" / "precision" / "should-not-write"
            experience_dir = repo / ".agent" / "experience"
            self.assertFalse(evidence.exists())
            self.assertFalse(experience_dir.exists())

    def test_sufficient_sample_emits_proposal_only(self) -> None:
        rows = load_outcomes_bundle(FIXTURE)
        ledger = build_precision_ledger(
            rows,
            ledger_id="precision-test-proposal",
            min_sample_for_proposal=5,
        )
        proposal = build_priority_proposal(ledger)
        self.assertIs(proposal["auto_apply"], False)
        self.assertIs(proposal["captain_approved"], False)
        skill_ids = {d["skill_id"] for d in proposal["skill_confidence_deltas"]}
        self.assertIn("security-review", skill_ids)
        # code-reviewer has only 1 decided — below min sample → omitted
        self.assertNotIn("code-reviewer", skill_ids)


class AggregateCliTests(unittest.TestCase):
    def test_aggregate_writes_evidence_and_experience(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = aggregate_precision(
                repo_root=repo,
                outcomes=FIXTURE,
                plan_id="b5-precision-ledger",
                ledger_id="b5-fixture-demo",
                write_experience_lesson=True,
                emit_priority_proposal=True,
                min_sample_for_proposal=5,
                source_instance="control-test",
            )
            self.assertEqual(result["ledger_id"], "b5-fixture-demo")
            self.assertTrue(Path(result["ledger_path"]).is_file())
            self.assertTrue(Path(result["dashboard_md_path"]).is_file())
            self.assertTrue(Path(result["dashboard_json_path"]).is_file())
            self.assertEqual(len(result["experience_paths"]), 2)
            self.assertTrue(Path(result["proposal_path"]).is_file())
            self.assertIs(result["captain_approval"], False)
            self.assertIs(result["proposal_auto_apply"], False)

            ledger = json.loads(Path(result["ledger_path"]).read_text(encoding="utf-8"))
            validate_document(ledger, "precision-ledger.schema.json")
            md = Path(result["dashboard_md_path"]).read_text(encoding="utf-8")
            self.assertIn("security-review", md)
            self.assertIn("80.0%", md)

            proposal = json.loads(Path(result["proposal_path"]).read_text(encoding="utf-8"))
            self.assertIs(proposal["auto_apply"], False)

    def test_notes_redact_embedded_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = aggregate_precision(
                repo_root=repo,
                outcomes=FIXTURE,
                ledger_id="b5-redact-demo",
                write_experience_lesson=False,
                emit_priority_proposal=True,
                min_sample_for_proposal=5,
                proposal_notes=(
                    "token=ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA "
                    "password=supersecret "
                    "AKIAIOSFODNN7EXAMPLE"
                ),
                source_instance="control-test",
            )
            proposal = json.loads(Path(result["proposal_path"]).read_text(encoding="utf-8"))
            notes = str(proposal.get("notes") or "")
            self.assertIn("[REDACTED]", notes)
            self.assertNotIn("ghp_", notes)
            self.assertNotIn("supersecret", notes)
            self.assertNotIn("AKIAIOSFODNN7EXAMPLE", notes)

    def test_script_cli_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "aggregate-precision-ledger.sh"),
                    "--repo-root",
                    str(repo),
                    "--outcomes",
                    str(FIXTURE),
                    "--ledger-id",
                    "b5-cli-smoke",
                    "--plan-id",
                    "b5-precision-ledger",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["ledger_id"], "b5-cli-smoke")
            self.assertTrue(Path(payload["dashboard_md_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
