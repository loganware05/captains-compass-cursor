"""Open UI control plane — hermetic tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.openui.approval import ApprovalError, apply_plan_decision
from orchestrator.openui.emitters import (
    emit_closeout_ledger,
    emit_control_tower,
    emit_hermetic_scorecard,
    emit_plan_approval,
)
from orchestrator.openui.enabled import openui_enabled
from orchestrator.openui.lang import OpenUILangError, validate_openui_lang
from orchestrator.openui.service import OpenUIServiceError, run_ui_command


def _seed_repo(repo: Path) -> None:
    (repo / "VERSION").write_text("1.74.0\n", encoding="utf-8")
    (repo / "IMPLEMENTATION_PLAN.md").write_text(
        "# Demo Plan\n\n"
        "- Status: **AWAITING APPROVAL**\n\n"
        "| Field | Value |\n|---|---|\n"
        "| Status | **AWAITING APPROVAL** |\n"
        "| Plan ID | `demo-plan` |\n\n"
        "## Approval record\n\n"
        "| Field | Value |\n|---|---|\n"
        "| Approved by | — |\n"
        "| Approval date | — |\n"
        "| Notes | — |\n\n"
        "## Files Expected to Change\n\n"
        "| Path | Change |\n|---|---|\n"
        "| `orchestrator/ui/src/library.ts` | new |\n",
        encoding="utf-8",
    )
    agents = repo / ".cursor" / "agents"
    agents.mkdir(parents=True)
    (agents / "implementation-agent.md").write_text("# impl\n", encoding="utf-8")
    hooks = repo / ".cursor" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "plan-approval-check.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    skills = repo / ".cursor" / "skills" / "react-engineering"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text("# react\n", encoding="utf-8")
    budgets = repo / ".agent" / "budgets"
    budgets.mkdir(parents=True)
    (budgets / "demo-plan.md").write_text("Status: ACTIVE\n", encoding="utf-8")


class LangTests(unittest.TestCase):
    def test_validate_ok(self) -> None:
        lang = (
            'card = PlanApprovalCard("id", "title", "APPROVED", "r", "f", "s", "h")\n'
            "root = NorthStarStack([card])\n"
        )
        meta = validate_openui_lang(lang)
        self.assertTrue(meta["ok"])
        self.assertIn("root", meta["identifiers"])

    def test_validate_unknown_component_fail_closed(self) -> None:
        with self.assertRaises(OpenUILangError):
            validate_openui_lang('root = EvilWidget("x")\n')

    def test_validate_nested_unknown_component_fail_closed(self) -> None:
        with self.assertRaises(OpenUILangError):
            validate_openui_lang('root = NorthStarStack([EvilWidget("x")])\n')

    def test_validate_ignores_parens_inside_string_literals(self) -> None:
        lang = (
            'card = PlanApprovalCard("id", "Open UI Control Plane (v1.74.0)", '
            '"APPROVED", "r", "f", "s", "h")\n'
            "root = NorthStarStack([card])\n"
        )
        meta = validate_openui_lang(lang)
        self.assertTrue(meta["ok"])

    def test_validate_missing_root(self) -> None:
        with self.assertRaises(OpenUILangError):
            validate_openui_lang('card = CompassStatusBadge("a", "1", "ok")\n')


class EmitterTests(unittest.TestCase):
    def test_emitters_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            for fn in (
                emit_plan_approval,
                emit_control_tower,
                emit_hermetic_scorecard,
                emit_closeout_ledger,
            ):
                lang = fn(repo)
                validate_openui_lang(lang)
                self.assertIn("root = NorthStarStack", lang)


class ApprovalTests(unittest.TestCase):
    def test_approve_requires_captain_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COMPASS_CAPTAIN_APPROVE", None)
                with self.assertRaises(ApprovalError):
                    apply_plan_decision(repo, decision="approve")

    def test_approve_with_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_CAPTAIN_APPROVE": "1"}):
                out = apply_plan_decision(repo, decision="approve", approved_by="Captain")
            self.assertEqual(out["status"], "APPROVED")
            text = (repo / "IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
            self.assertIn("APPROVED", text)
            self.assertIn("Captain", text)

    def test_reject_writes_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            out = apply_plan_decision(
                repo, decision="reject", feedback="Needs clearer rollback"
            )
            self.assertEqual(out["decision"], "reject")
            self.assertTrue(Path(out["feedback_path"]).is_file())
            text = (repo / "IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
            self.assertIn("AWAITING APPROVAL", text)
            self.assertIn("Needs clearer rollback", text)


class ServiceGateTests(unittest.TestCase):
    def test_emit_requires_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COMPASS_OPENUI_ENABLED", None)
                self.assertFalse(openui_enabled())
                with self.assertRaises(PermissionError):
                    run_ui_command(repo, "emit", surface="plan")

    def test_emit_with_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_OPENUI_ENABLED": "1"}):
                result = run_ui_command(repo, "emit", surface="plan", persist=True)
            self.assertEqual(result["status"], "emitted")
            self.assertFalse(result["auto_approved"])
            self.assertTrue(Path(result["path"]).is_file())

    def test_unknown_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_OPENUI_ENABLED": "1"}):
                with self.assertRaises(OpenUIServiceError):
                    run_ui_command(repo, "emit", surface="nope")


if __name__ == "__main__":
    unittest.main()
