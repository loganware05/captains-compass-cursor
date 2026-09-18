"""M36 — fail-closed hook hardening (plan-approval + protected-branch)."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN_HOOK = ROOT / ".cursor" / "hooks" / "plan-approval-check.sh"
BRANCH_HOOK = ROOT / ".cursor" / "hooks" / "protected-branch.sh"


def _run_hook(script: Path, payload: dict, *, env: dict | None = None, cwd: Path | None = None) -> dict:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        [str(script)],
        input=json.dumps(payload),
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=merged,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )


def _init_repo(repo: Path, branch: str = "feature/m36") -> None:
    _git(repo, "init")
    _git(repo, "checkout", "-b", branch)
    (repo / "f").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "f")
    subprocess.run(
        ["git", "-c", "user.email=t@t.com", "-c", "user.name=t", "commit", "-m", "init"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )


APPROVED_PLAN = """# Implementation Plan

## Metadata

| Field | Value |
|---|---|
| Status | APPROVED |
| Approved by | Logan Ware |
| Approval date | 2026-09-16 |

## Approval Record

Captain approved in chat.
"""


class ProtectedBranchHardeningTests(unittest.TestCase):
    def test_denies_push_refspecs_and_git_c_and_checkout_shortcircuit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            _init_repo(repo, "feature/ok")

            # On feature HEAD, push to main via refspec must deny
            out = _run_hook(
                BRANCH_HOOK,
                {"command": "git push origin HEAD:main", "cwd": str(repo)},
            )
            self.assertEqual(out["permission"], "deny")

            out = _run_hook(
                BRANCH_HOOK,
                {"command": "git push origin main", "cwd": str(repo)},
            )
            self.assertEqual(out["permission"], "deny")

            # checkout -b substring must NOT short-circuit a commit on main
            _git(repo, "checkout", "-B", "main")
            out = _run_hook(
                BRANCH_HOOK,
                {
                    "command": "git checkout -b feature/evil && git commit -m x",
                    "cwd": str(repo),
                },
            )
            self.assertEqual(out["permission"], "deny")

            # git -C into protected repo from another cwd
            other = Path(tmp) / "other"
            other.mkdir()
            out = _run_hook(
                BRANCH_HOOK,
                {"command": f"cd {other} && git -C {repo} commit -m x"},
            )
            self.assertEqual(out["permission"], "deny")

            _git(repo, "checkout", "-B", "feature/ok")
            out = _run_hook(
                BRANCH_HOOK,
                {"command": "git commit -m x", "cwd": str(repo)},
            )
            self.assertEqual(out["permission"], "allow")


class PlanApprovalHardeningTests(unittest.TestCase):
    def test_self_serve_plan_write_denied_without_captain_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            forged = {
                "path": "IMPLEMENTATION_PLAN.md",
                "contents": APPROVED_PLAN,
            }
            out = _run_hook(PLAN_HOOK, forged, cwd=repo)
            self.assertEqual(out["permission"], "deny")
            self.assertIn("self-serve", out["user_message"].lower())

            out = _run_hook(
                PLAN_HOOK,
                forged,
                cwd=repo,
                env={"COMPASS_CAPTAIN_APPROVE": "1"},
            )
            self.assertEqual(out["permission"], "allow")

    def test_working_tree_approved_does_not_unlock_product_without_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            # Working tree only — not committed
            (repo / "IMPLEMENTATION_PLAN.md").write_text(APPROVED_PLAN, encoding="utf-8")
            out = _run_hook(PLAN_HOOK, {"path": "src/App.tsx"}, cwd=repo)
            self.assertEqual(out["permission"], "deny")
            self.assertIn("committed", out["user_message"].lower())

            _git(repo, "add", "IMPLEMENTATION_PLAN.md")
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=t@t.com",
                    "-c",
                    "user.name=t",
                    "commit",
                    "-m",
                    "approve",
                ],
                cwd=str(repo),
                check=True,
                capture_output=True,
            )
            out = _run_hook(PLAN_HOOK, {"path": "src/App.tsx"}, cwd=repo)
            self.assertEqual(out["permission"], "allow")

    def test_template_heading_alone_insufficient(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _init_repo(repo)
            weak = """# Implementation Plan

## Metadata

| Field | Value |
|---|---|
| Status | APPROVED |
| Approved by | |
| Approval date | |

## Approval Record

<!-- After Captain approval, record who approved -->
"""
            (repo / "IMPLEMENTATION_PLAN.md").write_text(weak, encoding="utf-8")
            _git(repo, "add", "IMPLEMENTATION_PLAN.md")
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=t@t.com",
                    "-c",
                    "user.name=t",
                    "commit",
                    "-m",
                    "weak",
                ],
                cwd=str(repo),
                check=True,
                capture_output=True,
            )
            out = _run_hook(PLAN_HOOK, {"path": "src/App.tsx"}, cwd=repo)
            self.assertEqual(out["permission"], "deny")


if __name__ == "__main__":
    unittest.main()
