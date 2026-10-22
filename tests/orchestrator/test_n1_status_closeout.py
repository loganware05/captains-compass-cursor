"""N1 status closeout — hermetic tests."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.status.closeout import build_closeout_report
from orchestrator.status.drift import parse_skill_count_from_docs
from orchestrator.status.enabled import status_enabled
from orchestrator.status.service import closeout


def _seed_memory(repo: Path) -> None:
    (repo / "VERSION").write_text("1.71.1\n", encoding="utf-8")
    for name in (
        "AGENTS.md",
        "PROJECT_CONTEXT.md",
        "DECISIONS.md",
        "PROGRESS.md",
        "TESTING.md",
        "IMPLEMENTATION_PLAN.md",
    ):
        (repo / name).write_text("", encoding="utf-8")
    (repo / "PROJECT_CONTEXT.md").write_text(
        "NorthStar control repo with Forty-eight Skills in .cursor/skills.\n",
        encoding="utf-8",
    )
    (repo / "IMPLEMENTATION_PLAN.md").write_text(
        "# Plan\n\n- Status: APPROVED\n\n"
        "| Field | Value |\n|---|---|\n"
        "| Plan ID | `n1-operational-reconciliation` |\n",
        encoding="utf-8",
    )
    (repo / "PROGRESS.md").write_text(
        "## Current status\n\nActive plan `n1-operational-reconciliation` · v1.71.1.\n",
        encoding="utf-8",
    )
    skill_root = repo / ".cursor" / "skills"
    for name in ("alpha", "beta"):
        d = skill_root / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    # Fix skill docs to match fs for non-mismatch cases
    (repo / "PROJECT_CONTEXT.md").write_text(
        "NorthStar control repo with 2 Skills in .cursor/skills.\n",
        encoding="utf-8",
    )


class SchemaTests(unittest.TestCase):
    def test_closeout_schema_locks(self) -> None:
        doc = {
            "schema_version": "1",
            "report_id": "closeout-test",
            "created_at": "2026-10-22T00:00:00Z",
            "repository_sha": "abc",
            "northstar_version": "1.71.1",
            "snapshot_id": "psnap-test",
            "readiness": "ready",
            "ledger_items": [],
            "drift_finding_ids": [],
            "recommended_actions": ["none"],
            "approved_for_execution": False,
            "authority_mutation": False,
            "issues_auto_closed": False,
        }
        validate_document(doc, "status-closeout-report.schema.json")
        bad = dict(doc)
        bad["issues_auto_closed"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "status-closeout-report.schema.json")
        bad2 = dict(doc)
        bad2["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad2, "status-closeout-report.schema.json")


class DriftWordNumberTests(unittest.TestCase):
    def test_forty_seven_and_eight(self) -> None:
        self.assertEqual(parse_skill_count_from_docs("Forty-seven Skills"), 47)
        self.assertEqual(parse_skill_count_from_docs("Forty-eight Skills"), 48)


class CloseoutServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="n1-closeout-"))
        _seed_memory(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_fail_closed_without_gate(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_STATUS_ENABLED", None)
            self.assertFalse(status_enabled())
            with self.assertRaises(Exception):
                closeout(self.tmp)

    def test_closeout_with_ledger(self) -> None:
        ledger = {
            "items": [
                {
                    "item_id": "issue-220",
                    "kind": "github_issue",
                    "title": "Post-C7 closeout",
                    "status": "completed",
                    "recommended_disposition": "Verify then close",
                    "evidence": ["PR #221"],
                    "subsystem": "cognitive-core",
                    "notes": "",
                },
                {
                    "item_id": "plan-l3",
                    "kind": "plan",
                    "title": "Level 3",
                    "status": "deferred",
                    "recommended_disposition": "Keep deferred",
                    "evidence": ["SPECIALIZED_MODEL_LEVEL_3.md"],
                },
            ]
        }
        ledger_path = self.tmp / "ledger.json"
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            result = closeout(self.tmp, ledger_path=str(ledger_path))
        self.assertEqual(result["status"], "closeout_assessed")
        report = result["report"]
        self.assertFalse(report["approved_for_execution"])
        self.assertFalse(report["authority_mutation"])
        self.assertFalse(report["issues_auto_closed"])
        self.assertEqual(report["readiness"], "needs_captain_action")
        self.assertEqual(len(report["ledger_items"]), 2)
        validate_document(report, "status-closeout-report.schema.json")

    def test_build_without_ledger_ready_when_clean(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            report = build_closeout_report(self.tmp, persist=True)
        self.assertEqual(report["readiness"], "ready")
        self.assertFalse(report["issues_auto_closed"])
        validate_document(report, "status-closeout-report.schema.json")


if __name__ == "__main__":
    unittest.main()
