"""Hermetic tests: OpenUI emit → local preview/serve."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.openui.preview import (
    PreviewError,
    render_preview_html,
    write_preview,
)
from orchestrator.openui.service import OpenUIServiceError, run_ui_command


def _seed_repo(repo: Path) -> None:
    (repo / "VERSION").write_text("1.89.0\n", encoding="utf-8")
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


class PreviewTests(unittest.TestCase):
    def test_emit_then_preview_contains_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_OPENUI_ENABLED": "1"}):
                emitted = run_ui_command(repo, "emit", surface="plan", persist=True)
                self.assertEqual(emitted["status"], "emitted")
                result = run_ui_command(repo, "preview", surface="plan")
            self.assertEqual(result["status"], "preview_written")
            path = Path(result["path"])
            self.assertTrue(path.is_file())
            html = path.read_text(encoding="utf-8")
            self.assertIn("Live Open UI surfaces", html)
            self.assertIn("Surface: plan", html)
            self.assertIn("PlanApprovalCard", html)
            self.assertIn("demo-plan", html)
            self.assertIn("v1.89.0", html)
            self.assertIn("never auto-approves", html.lower())

    def test_preview_auto_emits_when_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_OPENUI_ENABLED": "1"}):
                result = run_ui_command(repo, "preview")
            self.assertEqual(result["status"], "preview_written")
            self.assertTrue((repo / ".agent" / "ui" / "plan.openui").is_file())
            html = Path(result["path"]).read_text(encoding="utf-8")
            self.assertIn("Surface: plan", html)

    def test_preview_requires_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COMPASS_OPENUI_ENABLED", None)
                with self.assertRaises(PermissionError):
                    run_ui_command(repo, "preview")

    def test_render_fails_without_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_OPENUI_ENABLED": "1"}):
                with self.assertRaises(PreviewError):
                    render_preview_html(repo)

    def test_serve_timeout_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_OPENUI_ENABLED": "1"}):
                run_ui_command(repo, "emit", surface="tower", persist=True)
                result = run_ui_command(
                    repo,
                    "serve",
                    surface="tower",
                    host="127.0.0.1",
                    port=18765,
                    timeout_seconds=0.4,
                )
            self.assertEqual(result["status"], "served")
            self.assertIn("127.0.0.1:18765", result["url"])
            self.assertFalse(result["auto_approved"])
            self.assertTrue(Path(result["path"]).is_file())

    def test_serve_rejects_non_localhost(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_repo(repo)
            with mock.patch.dict(os.environ, {"COMPASS_OPENUI_ENABLED": "1"}):
                run_ui_command(repo, "emit", surface="plan", persist=True)
                with self.assertRaises(OpenUIServiceError):
                    run_ui_command(
                        repo,
                        "serve",
                        host="0.0.0.0",
                        port=18766,
                        timeout_seconds=0.2,
                    )


if __name__ == "__main__":
    unittest.main()
