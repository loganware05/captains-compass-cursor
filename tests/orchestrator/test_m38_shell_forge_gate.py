"""M38 — shell forge gate for IMPLEMENTATION_PLAN.md (beforeShellExecution)."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN_HOOK = ROOT / ".cursor" / "hooks" / "plan-approval-check.sh"


def _run_hook(payload: dict, *, env: dict | None = None) -> dict:
    merged = os.environ.copy()
    # Isolate from ambient Captain approve in the agent environment.
    merged.pop("COMPASS_CAPTAIN_APPROVE", None)
    if env:
        merged.update(env)
    proc = subprocess.run(
        [str(PLAN_HOOK)],
        input=json.dumps(payload),
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=merged,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


class ShellForgeGateTests(unittest.TestCase):
    def test_denies_echo_redirect_promoting_approved(self) -> None:
        out = _run_hook(
            {
                "command": (
                    'echo "| Status | APPROVED |" > IMPLEMENTATION_PLAN.md'
                )
            }
        )
        self.assertEqual(out["permission"], "deny")
        self.assertIn("shell forge", out["agent_message"].lower())

    def test_denies_tee_promoting_in_progress(self) -> None:
        out = _run_hook(
            {
                "command": (
                    'printf "| Status | IN PROGRESS |\\n" | tee IMPLEMENTATION_PLAN.md'
                )
            }
        )
        self.assertEqual(out["permission"], "deny")

    def test_allows_captain_env_promote(self) -> None:
        out = _run_hook(
            {
                "command": (
                    'echo "| Status | APPROVED |" > IMPLEMENTATION_PLAN.md'
                )
            },
            env={"COMPASS_CAPTAIN_APPROVE": "1"},
        )
        self.assertEqual(out["permission"], "allow")

    def test_denies_opaque_non_promoting_plan_shell_write(self) -> None:
        # Fail-closed residual from #173: redirects without promote tokens
        # still cannot prove Status is safe.
        out = _run_hook(
            {
                "command": (
                    'echo "| Status | AWAITING APPROVAL |" > IMPLEMENTATION_PLAN.md'
                )
            }
        )
        self.assertEqual(out["permission"], "deny")
        self.assertIn("opaque", out["agent_message"].lower())

    def test_denies_opaque_cat_redirect(self) -> None:
        out = _run_hook(
            {"command": "cat somewhere.md > IMPLEMENTATION_PLAN.md"}
        )
        self.assertEqual(out["permission"], "deny")

    def test_allows_read_only_plan_shell(self) -> None:
        out = _run_hook({"command": "cat IMPLEMENTATION_PLAN.md"})
        self.assertEqual(out["permission"], "allow")
        out = _run_hook({"command": "grep -n Status IMPLEMENTATION_PLAN.md"})
        self.assertEqual(out["permission"], "allow")

    def test_allows_captain_env_in_command_string(self) -> None:
        out = _run_hook(
            {
                "command": (
                    "COMPASS_CAPTAIN_APPROVE=1 "
                    'echo "| Status | APPROVED |" > IMPLEMENTATION_PLAN.md'
                )
            }
        )
        self.assertEqual(out["permission"], "allow")

    def test_allows_unrelated_shell(self) -> None:
        out = _run_hook({"command": "echo hello && git status"})
        self.assertEqual(out["permission"], "allow")

    def test_write_path_still_denies_self_serve(self) -> None:
        out = _run_hook(
            {
                "file_path": "IMPLEMENTATION_PLAN.md",
                "contents": "| Status | APPROVED |\n| Approved by | X |\n| Approval date | 2026-09-18 |\n",
            }
        )
        self.assertEqual(out["permission"], "deny")


if __name__ == "__main__":
    unittest.main()
