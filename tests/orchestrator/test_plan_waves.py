"""Wave ledger + continue-after-merge (#274)."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "plan-waves"
_TMP = ROOT / ".agent" / "tmp-plan-waves-tests"

from orchestrator.plan_waves.errors import PlanWavesError
from orchestrator.plan_waves.gh_pr import require_merged_pr
from orchestrator.plan_waves.parse import parse_waves_from_plan
from orchestrator.plan_waves.service import (
    advance_wave,
    continue_after_merge,
    init_wave_ledger,
    wave_ledger_status,
)
from orchestrator.schemas.validate import validate_document


def _mk_repo() -> Path:
    _TMP.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="planwaves-", dir=str(_TMP)))


def _gh_from_fixture(name: str):
    payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def _view(owner: str, repo: str, number: int):
        return dict(payload)

    return _view


class PlanWavesParseTests(unittest.TestCase):
    def test_parse_wave_headings(self) -> None:
        text = (FIXTURES / "two-wave-plan.md").read_text(encoding="utf-8")
        waves = parse_waves_from_plan(text)
        self.assertEqual(len(waves), 2)
        self.assertEqual(waves[0]["wave_id"], "wave-a")
        self.assertEqual(waves[1]["wave_id"], "wave-b")


class PlanWavesServiceTests(unittest.TestCase):
    def test_init_status_advance_continue(self) -> None:
        repo = _mk_repo()
        plan = FIXTURES / "two-wave-plan.md"
        init = init_wave_ledger(
            repo, plan_id="fixture-two-wave", from_path=plan
        )
        self.assertEqual(init["action"], "init")
        ledger = init["ledger"]
        validate_document(ledger, "wave-ledger.schema.json")
        self.assertIs(ledger["auto_merge"], False)
        self.assertIs(ledger["approved_for_execution"], False)
        self.assertIs(ledger["authority_mutation"], False)
        self.assertEqual(ledger["waves"][0]["status"], "in_progress")

        status = wave_ledger_status(repo, "fixture-two-wave")
        self.assertEqual(status["next_action"], "implement_wave")
        self.assertEqual(status["remaining_count"], 2)

        advanced = advance_wave(
            repo,
            plan_id="fixture-two-wave",
            pr_url="https://github.com/example/repo/pull/42",
            gh_pr_view=_gh_from_fixture("gh-merged.json"),
        )
        self.assertEqual(advanced["action"], "advanced")
        self.assertEqual(advanced["completed_wave"]["wave_id"], "wave-a")
        self.assertIsNotNone(advanced["next_wave"])
        self.assertEqual(advanced["next_wave"]["wave_id"], "wave-b")
        self.assertIn("continue wave wave-b", advanced["resume_prompt"])

        # Idempotent on same SHA
        again = advance_wave(
            repo,
            plan_id="fixture-two-wave",
            pr_url="https://github.com/example/repo/pull/42",
            gh_pr_view=_gh_from_fixture("gh-merged.json"),
        )
        self.assertEqual(again["action"], "idempotent")

        # Second wave merge → settle
        def gh_wave_b(owner, repo_name, number):
            return {
                "state": "MERGED",
                "mergedAt": "2026-11-14T19:00:00Z",
                "mergeCommit": {"oid": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
                "url": "https://github.com/example/repo/pull/43",
            }

        final = continue_after_merge(
            repo,
            plan_id="fixture-two-wave",
            pr_url="https://github.com/example/repo/pull/43",
            plan_path=plan,
            gh_pr_view=gh_wave_b,
        )
        self.assertIsNone(final["next_wave"])
        self.assertEqual(final["next_action"], "settle_complete")
        self.assertIn("no remaining waves", final["resume_prompt"])

    def test_refuse_draft_plan(self) -> None:
        repo = _mk_repo()
        with self.assertRaises(PlanWavesError) as ctx:
            init_wave_ledger(
                repo,
                plan_id="fixture-draft",
                from_path=FIXTURES / "draft-plan.md",
            )
        self.assertIn("never forge APPROVED", str(ctx.exception))

    def test_refuse_open_pr(self) -> None:
        repo = _mk_repo()
        plan = FIXTURES / "two-wave-plan.md"
        init_wave_ledger(repo, plan_id="fixture-two-wave", from_path=plan)
        with self.assertRaises(PlanWavesError) as ctx:
            continue_after_merge(
                repo,
                plan_id="fixture-two-wave",
                pr_url="https://github.com/example/repo/pull/42",
                plan_path=plan,
                gh_pr_view=_gh_from_fixture("gh-open.json"),
            )
        self.assertIn("not MERGED", str(ctx.exception))

    def test_refuse_no_remaining_waves(self) -> None:
        repo = _mk_repo()
        plan = FIXTURES / "two-wave-plan.md"
        init_wave_ledger(repo, plan_id="fixture-two-wave", from_path=plan)
        # Complete both waves
        advance_wave(
            repo,
            plan_id="fixture-two-wave",
            pr_url="https://github.com/example/repo/pull/42",
            gh_pr_view=_gh_from_fixture("gh-merged.json"),
        )

        def gh_b(owner, repo_name, number):
            return {
                "state": "MERGED",
                "mergedAt": "2026-11-14T19:00:00Z",
                "mergeCommit": {"oid": "cccccccccccccccccccccccccccccccccccccccc"},
                "url": "https://github.com/example/repo/pull/43",
            }

        continue_after_merge(
            repo,
            plan_id="fixture-two-wave",
            pr_url="https://github.com/example/repo/pull/43",
            plan_path=plan,
            gh_pr_view=gh_b,
        )
        with self.assertRaises(PlanWavesError) as ctx:
            continue_after_merge(
                repo,
                plan_id="fixture-two-wave",
                pr_url="https://github.com/example/repo/pull/44",
                plan_path=plan,
                gh_pr_view=_gh_from_fixture("gh-merged.json"),
            )
        self.assertIn("no remaining waves", str(ctx.exception))

    def test_pause_between_waves(self) -> None:
        repo = _mk_repo()
        plan = FIXTURES / "two-wave-plan.md"
        init_wave_ledger(
            repo,
            plan_id="fixture-two-wave",
            from_path=plan,
            pause_between_waves=True,
        )
        with self.assertRaises(PlanWavesError) as ctx:
            continue_after_merge(
                repo,
                plan_id="fixture-two-wave",
                pr_url="https://github.com/example/repo/pull/42",
                plan_path=plan,
                gh_pr_view=_gh_from_fixture("gh-merged.json"),
            )
        self.assertIn("pause_between_waves", str(ctx.exception))

    def test_require_merged_helper(self) -> None:
        merged = require_merged_pr(
            "https://github.com/example/repo/pull/42",
            gh_pr_view=_gh_from_fixture("gh-merged.json"),
        )
        self.assertEqual(merged["merged_sha"], "abc123mergedsha000000000000000000000001")
        with self.assertRaises(PlanWavesError):
            require_merged_pr(
                "https://github.com/example/repo/pull/42",
                gh_pr_view=_gh_from_fixture("gh-open.json"),
            )


class PlanWavesCliTests(unittest.TestCase):
    def test_cli_init_and_status(self) -> None:
        repo = _mk_repo()
        plan = FIXTURES / "two-wave-plan.md"
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-plan-waves.sh"),
                "waves",
                "init",
                "--plan-id",
                "fixture-two-wave",
                "--from",
                str(plan),
                "--repo-root",
                str(repo),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["action"], "init")

        proc2 = subprocess.run(
            [
                str(ROOT / "scripts" / "northstar"),
                "plan",
                "waves",
                "status",
                "--plan-id",
                "fixture-two-wave",
                "--repo",
                str(repo),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc2.returncode, 0, proc2.stderr)
        status = json.loads(proc2.stdout)
        self.assertEqual(status["plan_id"], "fixture-two-wave")
        self.assertEqual(status["remaining_count"], 2)

    def test_cli_refuse_open_via_continue(self) -> None:
        repo = _mk_repo()
        plan = FIXTURES / "two-wave-plan.md"
        init_wave_ledger(repo, plan_id="fixture-two-wave", from_path=plan)
        # Mock gh by patching PATH with a fake gh
        fake_bin = repo / "bin"
        fake_bin.mkdir()
        fake_gh = fake_bin / "gh"
        fake_gh.write_text(
            "#!/bin/sh\ncat <<'EOF'\n"
            + (FIXTURES / "gh-open.json").read_text(encoding="utf-8")
            + "\nEOF\n",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}:{env.get('PATH', '')}"
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-plan-waves.sh"),
                "continue-after-merge",
                "--plan-id",
                "fixture-two-wave",
                "--pr",
                "https://github.com/example/repo/pull/42",
                "--from",
                str(plan),
                "--repo-root",
                str(repo),
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("not MERGED", proc.stderr)


if __name__ == "__main__":
    unittest.main()
