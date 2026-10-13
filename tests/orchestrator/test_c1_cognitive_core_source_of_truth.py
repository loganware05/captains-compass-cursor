"""C1 Cognitive Core — hermetic project-state / brain tests."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-c1-tests"

from orchestrator.cognitive.enabled import brain_enabled, require_brain_enabled
from orchestrator.cognitive.git_facts import git_sha
from orchestrator.cognitive.service import show, status, sync
from orchestrator.cognitive.store import load_latest, load_snapshot
from orchestrator.cognitive.sync import build_project_state, sync_project_state
from orchestrator.schemas.validate import ValidationError, validate_document


def _mk_fixture_dir(prefix: str) -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(_FIXTURE_ROOT)))


def _seed_repo(repo: Path, *, version: str = "1.60.0") -> None:
    (repo / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    for name in (
        "AGENTS.md",
        "PROJECT_CONTEXT.md",
        "DECISIONS.md",
        "PROGRESS.md",
        "TESTING.md",
        "IMPLEMENTATION_PLAN.md",
    ):
        (repo / name).write_text("", encoding="utf-8")
    (repo / "IMPLEMENTATION_PLAN.md").write_text(
        "# Plan\n\n- Status: APPROVED\n\n"
        "| Field | Value |\n|---|---|\n"
        "| Plan ID | `c1-cognitive-core-source-of-truth` |\n",
        encoding="utf-8",
    )
    (repo / "PROGRESS.md").write_text(
        "## Current status\n\nActive plan `c1-cognitive-core-source-of-truth` · "
        f"v{version}.\n",
        encoding="utf-8",
    )
    # Avoid creating `.cursor/` in fixtures; skill_count_fs may be 0.
    proc = subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git init failed: {proc.stderr or proc.stdout}")
    subprocess.run(
        ["git", "config", "user.email", "c1@test.local"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "C1 Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "commit", "-m", "seed"],
        cwd=repo,
        check=True,
        capture_output=True,
    )


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_BRAIN_ENABLED", None)
            self.assertFalse(brain_enabled())
            with self.assertRaises(PermissionError):
                require_brain_enabled()

    def test_enabled_truthy(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
            self.assertTrue(brain_enabled())


class SchemaTests(unittest.TestCase):
    def test_snapshot_schema_locks_authority(self) -> None:
        doc = {
            "snapshot_id": "pstate-test",
            "schema_version": "1",
            "created_at": "2026-10-13T00:00:00Z",
            "repository_sha": "abc",
            "northstar_version": "1.60.0",
            "freshness": "fresh",
            "sources": ["local_git"],
            "citations": [
                {"kind": "git", "ref": "HEAD=abc", "claim_kind": "observed"}
            ],
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(doc, "project-state-snapshot.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "project-state-snapshot.schema.json")


class SyncFreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = _mk_fixture_dir("c1-brain-")
        _seed_repo(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_sync_writes_fresh_snapshot(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
            result = sync(self.tmp)
        snap = result["snapshot"]
        self.assertEqual(result["freshness"], "fresh")
        self.assertEqual(snap["freshness"], "fresh")
        self.assertEqual(snap["repository_sha"], git_sha(self.tmp))
        self.assertIn("local_git", snap["sources"])
        self.assertFalse(snap["approved_for_execution"])
        self.assertFalse(snap["authority_mutation"])
        loaded = load_latest(self.tmp)
        assert loaded is not None
        self.assertEqual(loaded["snapshot_id"], snap["snapshot_id"])
        validate_document(loaded, "project-state-snapshot.schema.json")

    def test_status_stale_after_new_commit(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
            sync(self.tmp)
            (self.tmp / "EXTRA.md").write_text("x\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "EXTRA.md"],
                cwd=self.tmp,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-c", "commit.gpgsign=false", "commit", "-m", "advance"],
                cwd=self.tmp,
                check=True,
                capture_output=True,
            )
            report = status(self.tmp)
        self.assertEqual(report["freshness"], "stale")
        self.assertEqual(report["status"], "ok")
        self.assertNotEqual(
            report["repository_sha_head"],
            report["snapshot"]["repository_sha"],
        )

    def test_show_requires_id(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
            synced = sync(self.tmp)
            sid = synced["snapshot"]["snapshot_id"]
            shown = show(self.tmp, snapshot_id=sid)
        self.assertEqual(shown["snapshot"]["snapshot_id"], sid)
        self.assertEqual(load_snapshot(self.tmp, sid)["snapshot_id"], sid)

    def test_status_without_sync(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BRAIN_ENABLED": "1"}):
            report = status(self.tmp)
        self.assertEqual(report["status"], "no_snapshot")
        self.assertEqual(report["freshness"], "stale")


class CliGateTests(unittest.TestCase):
    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_BRAIN_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-brain.sh"), "sync", "--repo-root", str(ROOT)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_BRAIN_ENABLED", proc.stderr)

    def test_northstar_brain_sync(self) -> None:
        tmp = _mk_fixture_dir("c1-cli-")
        try:
            _seed_repo(tmp)
            env = os.environ.copy()
            env["COMPASS_BRAIN_ENABLED"] = "1"
            env["PYTHONPATH"] = str(ROOT)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "northstar"),
                    "brain",
                    "sync",
                    "--repo",
                    str(tmp),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            doc = json.loads(proc.stdout)
            self.assertEqual(doc["status"], "synced")
            self.assertEqual(doc["freshness"], "fresh")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class BuildWithoutStatusComposeTests(unittest.TestCase):
    def test_local_git_only_when_status_disabled(self) -> None:
        tmp = _mk_fixture_dir("c1-local-")
        try:
            _seed_repo(tmp)
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COMPASS_STATUS_ENABLED", None)
                doc = build_project_state(tmp)
            self.assertEqual(doc["sources"], ["local_git"])
            self.assertIsNone(doc["composed_status_snapshot_id"])
            sync_project_state(tmp, persist=True)
            latest = load_latest(tmp)
            assert latest is not None
            self.assertEqual(latest["sources"], ["local_git"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
