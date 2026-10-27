"""N5 Skill-fit / routing feedback — hermetic tests."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.feedback.n5.enabled import n5_enabled
from orchestrator.feedback.n5.service import N5ServiceError, run_n5_feedback
from orchestrator.feedback.n5.suggest import build_skill_fit_suggestions
from orchestrator.schemas.validate import ValidationError, validate_document

REPO = Path(__file__).resolve().parents[2]
N4_LATEST = (
    REPO / ".agent" / "evidence" / "n4-cross-stack-benchmark" / "LATEST_hermetic.json"
)


def _seed_repo_with_n4(tmp: Path) -> Path:
    dest = (
        tmp
        / ".agent"
        / "evidence"
        / "n4-cross-stack-benchmark"
        / "LATEST_hermetic.json"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(N4_LATEST, dest)
    (tmp / "VERSION").write_text("1.76.0\n", encoding="utf-8")
    return dest


class GateTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_N5_FEEDBACK_ENABLED", None)
            self.assertFalse(n5_enabled())
            with self.assertRaises(PermissionError):
                run_n5_feedback(REPO, persist=False)


class SuggestTests(unittest.TestCase):
    def test_positive_deltas_emit_boosts(self) -> None:
        with N4_LATEST.open(encoding="utf-8") as handle:
            n4 = json.load(handle)
        rows = build_skill_fit_suggestions(n4)
        actions = {r["action"] for r in rows}
        self.assertIn("boost", actions)
        self.assertTrue(any(r["skill_id"] != "(none)" for r in rows))

    def test_below_threshold_no_change(self) -> None:
        rows = build_skill_fit_suggestions(
            {
                "deltas": {
                    "accept_rate": 0.01,
                    "skill_reuse_rate": 0.01,
                    "retrieval_precision": 0.01,
                    "primary_efficiency": 0.01,
                },
                "stacks": [],
            }
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["action"], "no_change")


class SchemaLockTests(unittest.TestCase):
    def test_authority_locks(self) -> None:
        self.assertTrue(N4_LATEST.is_file())
        with mock.patch.dict(os.environ, {"COMPASS_N5_FEEDBACK_ENABLED": "1"}):
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                _seed_repo_with_n4(repo)
                packet = run_n5_feedback(repo, persist=False, write_proposals=False)
        validate_document(packet, "n5-feedback-report.schema.json")
        self.assertFalse(packet["approved_for_execution"])
        self.assertFalse(packet["authority_mutation"])
        self.assertFalse(packet["auto_applied"])
        self.assertFalse(packet["policy_promoted"])
        self.assertFalse(packet["weights_applied"])
        self.assertFalse(packet["validation_summary"]["proposal_applied"])
        bad = dict(packet)
        bad["weights_applied"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "n5-feedback-report.schema.json")


class RunnerTests(unittest.TestCase):
    def test_writes_proposal_not_applied(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_N5_FEEDBACK_ENABLED": "1"}):
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                _seed_repo_with_n4(repo)
                packet = run_n5_feedback(repo, persist=True, write_proposals=True)
                self.assertGreater(
                    packet["validation_summary"]["actionable_suggestions"], 0
                )
                self.assertTrue(packet["validation_summary"]["proposal_written"])
                self.assertFalse(packet["validation_summary"]["proposal_applied"])
                self.assertIsNotNone(packet["routing_proposal_path"])
                prop = Path(packet["routing_proposal_path"])
                self.assertTrue(prop.is_file())
                with prop.open(encoding="utf-8") as handle:
                    proposal = json.load(handle)
                self.assertFalse(proposal["auto_apply"])
                self.assertFalse(proposal.get("captain_approved"))
                latest = (
                    repo
                    / ".agent"
                    / "evidence"
                    / "n5-skill-routing-feedback"
                    / "LATEST.json"
                )
                self.assertTrue(latest.is_file())

    def test_missing_n4_refuses(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_N5_FEEDBACK_ENABLED": "1"}):
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                (repo / "VERSION").write_text("1.76.0\n", encoding="utf-8")
                with self.assertRaises(N5ServiceError):
                    run_n5_feedback(repo, persist=False)


if __name__ == "__main__":
    unittest.main()
