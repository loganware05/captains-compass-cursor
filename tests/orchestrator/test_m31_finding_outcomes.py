"""M31 finding outcomes → Experience → RoutingProposal tests."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.review.outcomes import (
    OutcomeError,
    load_triage_input,
    normalize_outcome,
    outcome_to_experience,
    record_finding_outcomes,
)
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "code-review"
SAMPLE_REPORT = (
    ROOT
    / ".agent"
    / "evidence"
    / "m28-reviewer-specialist-composition"
    / "bitcoin-style-demo"
    / "report.json"
)


class FindingOutcomeSchemaTests(unittest.TestCase):
    def test_normalize_forces_captain_approval_false(self) -> None:
        report = json.loads(SAMPLE_REPORT.read_text(encoding="utf-8"))
        pack = normalize_outcome(
            {
                "finding_id": "sec-secret-in-diff",
                "decision": "accepted",
                "captain_approval": True,
            },
            report=report,
        )
        validate_document(pack, "finding-outcome.schema.json")
        self.assertIs(pack["captain_approval"], False)
        self.assertEqual(pack["label"], "tp")

    def test_unknown_finding_rejected(self) -> None:
        report = json.loads(SAMPLE_REPORT.read_text(encoding="utf-8"))
        with self.assertRaises(OutcomeError):
            normalize_outcome(
                {"finding_id": "does-not-exist", "decision": "accepted"},
                report=report,
            )

    def test_non_dict_triage_rows_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(["x", 1, None]), encoding="utf-8")
            with self.assertRaises(OutcomeError):
                load_triage_input(path)


class ExperienceBridgeTests(unittest.TestCase):
    def test_accepted_maps_to_success(self) -> None:
        report = json.loads(SAMPLE_REPORT.read_text(encoding="utf-8"))
        outcome = normalize_outcome(
            {"finding_id": "sec-secret-in-diff", "decision": "accepted"},
            report=report,
        )
        experience = outcome_to_experience(outcome, plan_id="m31-finding-outcomes-experience")
        validate_document(experience, "experience.schema.json")
        self.assertEqual(experience["outcome"], "success")
        self.assertIn("security-review", experience["skills_used"])

    def test_rejected_maps_to_failed(self) -> None:
        report = json.loads(SAMPLE_REPORT.read_text(encoding="utf-8"))
        outcome = normalize_outcome(
            {"finding_id": "noise-style-nit", "decision": "rejected", "label": "fp"},
            report=report,
        )
        experience = outcome_to_experience(outcome)
        self.assertEqual(experience["outcome"], "failed")

    def test_notes_redact_embedded_tokens(self) -> None:
        report = json.loads(SAMPLE_REPORT.read_text(encoding="utf-8"))
        outcome = normalize_outcome(
            {
                "finding_id": "sec-secret-in-diff",
                "decision": "accepted",
                "notes": (
                    "saw token=ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA "
                    "password=supersecret "
                    "AKIAIOSFODNN7EXAMPLE "
                    "in chat"
                ),
            },
            report=report,
        )
        self.assertNotIn("ghp_", outcome["notes"])
        self.assertNotIn("supersecret", outcome["notes"])
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", outcome["notes"])
        self.assertIn("[REDACTED]", outcome["notes"])
        experience = outcome_to_experience(outcome)
        blob = json.dumps(experience)
        self.assertNotIn("ghp_", blob)
        self.assertNotIn("supersecret", blob)


class RecordOutcomesTests(unittest.TestCase):
    def test_record_writes_experience_and_optional_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report_src = SAMPLE_REPORT
            report_dst = (
                repo
                / ".agent"
                / "evidence"
                / "code-review"
                / "m28-bitcoin-style-demo"
                / "report.json"
            )
            report_dst.parent.mkdir(parents=True)
            shutil.copy(report_src, report_dst)
            triage = FIXTURES / "triage-outcomes.json"

            result = record_finding_outcomes(
                repo_root=repo,
                report_path=report_dst,
                triage_path=triage,
                plan_id="m31-finding-outcomes-experience",
                emit_routing_proposal=True,
            )
            self.assertEqual(result["outcome_count"], 3)
            self.assertIs(result["captain_approval"], False)
            self.assertEqual(result["proposal_auto_apply"], False)
            self.assertEqual(result["source_instance"], "product-import")
            self.assertTrue(Path(result["outcomes_path"]).is_file())
            self.assertEqual(len(result["experience_paths"]), 2)  # deferred skipped
            experience = json.loads(Path(result["experience_paths"][0]).read_text(encoding="utf-8"))
            self.assertEqual(experience["source_instance"], "product-import")
            proposal = json.loads(Path(result["proposal_path"]).read_text(encoding="utf-8"))
            validate_document(proposal, "routing-proposal.schema.json")
            self.assertIs(proposal["auto_apply"], False)
            self.assertIs(proposal["captain_approved"], False)
            self.assertTrue(proposal["skill_confidence_deltas"])

    def test_proposal_notes_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report_dst = (
                repo
                / ".agent"
                / "evidence"
                / "code-review"
                / "m28-bitcoin-style-demo"
                / "report.json"
            )
            report_dst.parent.mkdir(parents=True)
            shutil.copy(SAMPLE_REPORT, report_dst)
            triage = repo / "triage.json"
            triage.write_text(
                json.dumps(
                    {
                        "outcomes": [
                            {
                                "finding_id": "sec-secret-in-diff",
                                "decision": "accepted",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = record_finding_outcomes(
                repo_root=repo,
                report_path=report_dst,
                triage_path=triage,
                emit_routing_proposal=True,
                proposal_notes="leak ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            )
            proposal = json.loads(Path(result["proposal_path"]).read_text(encoding="utf-8"))
            self.assertNotIn("ghp_", proposal["notes"])
            self.assertIn("[REDACTED]", proposal["notes"])

    def test_cli_record_finding_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report_dst = (
                repo
                / ".agent"
                / "evidence"
                / "code-review"
                / "m28-bitcoin-style-demo"
                / "report.json"
            )
            report_dst.parent.mkdir(parents=True)
            shutil.copy(SAMPLE_REPORT, report_dst)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "record-finding-outcomes.sh"),
                    "--repo-root",
                    str(repo),
                    "--report",
                    str(report_dst),
                    "--triage",
                    str(FIXTURES / "triage-outcomes.json"),
                    "--plan-id",
                    "m31-finding-outcomes-experience",
                    "--emit-routing-proposal",
                    "--notes",
                    "keep ghp_BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB out",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertFalse(payload["captain_approval"])
            self.assertEqual(payload["proposal_auto_apply"], False)
            proposal = json.loads(Path(payload["proposal_path"]).read_text(encoding="utf-8"))
            self.assertNotIn("ghp_", proposal["notes"])


if __name__ == "__main__":
    unittest.main()
