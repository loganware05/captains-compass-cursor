"""M51 Project Overseer — hermetic tests."""

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

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.status.compare import compare_since
from orchestrator.status.drift import (
    count_skills_fs,
    detect_drift,
    parse_skill_count_from_docs,
)
from orchestrator.status.enabled import require_status_enabled, status_enabled
from orchestrator.status.reconcile import draft_reconcile
from orchestrator.status.service import explain, export_csv, snapshot
from orchestrator.status.snapshot import build_snapshot, take_snapshot
from orchestrator.status.store import list_snapshots, load_snapshot


def _seed_memory(
    repo: Path,
    *,
    version: str = "1.56.0",
    skill_docs: str = "2 Skills",
    plan_id: str = "m51-project-overseer",
    plan_status: str = "APPROVED",
    progress_plan: str = "m51-project-overseer",
    progress_version: str | None = None,
) -> None:
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
    (repo / "PROJECT_CONTEXT.md").write_text(
        f"NorthStar control repo with {skill_docs} in .cursor/skills.\n",
        encoding="utf-8",
    )
    (repo / "IMPLEMENTATION_PLAN.md").write_text(
        f"# Plan\n\n- Status: {plan_status}\n\n"
        f"| Field | Value |\n|---|---|\n| Plan ID | `{plan_id}` |\n",
        encoding="utf-8",
    )
    ver_mention = progress_version if progress_version is not None else f"v{version}"
    (repo / "PROGRESS.md").write_text(
        f"## Current status\n\nActive plan `{progress_plan}` · {ver_mention}.\n",
        encoding="utf-8",
    )
    skill_root = repo / ".cursor" / "skills"
    for name in ("alpha", "beta"):
        d = skill_root / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_STATUS_ENABLED", None)
            self.assertFalse(status_enabled())
            with self.assertRaises(PermissionError):
                require_status_enabled()

    def test_enabled_truthy(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            self.assertTrue(status_enabled())


class SchemaTests(unittest.TestCase):
    def test_snapshot_schema_locks(self) -> None:
        doc = {
            "snapshot_id": "psnap-test",
            "schema_version": "1",
            "created_at": "2026-10-11T00:00:00Z",
            "repository_sha": "abc",
            "northstar_version": "1.56.0",
            "findings": [
                {
                    "finding_id": "f1",
                    "kind": "memory_docs",
                    "severity": "info",
                    "summary": "ok",
                    "evidence": ["AGENTS.md"],
                }
            ],
            "provider": {"name": "stub", "model": ""},
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(doc, "project-status-snapshot.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "project-status-snapshot.schema.json")

    def test_proposal_applied_must_be_false(self) -> None:
        doc = {
            "proposal_id": "srec-test",
            "snapshot_id": "psnap-test",
            "schema_version": "1",
            "created_at": "2026-10-11T00:00:00Z",
            "applied": False,
            "actions": [
                {
                    "action_id": "act-1",
                    "target": "PROGRESS.md",
                    "summary": "align version",
                }
            ],
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(doc, "status-reconcile-proposal.schema.json")
        bad = dict(doc)
        bad["applied"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "status-reconcile-proposal.schema.json")


class DriftTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m51-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_skill_count_parse_and_match(self) -> None:
        self.assertEqual(parse_skill_count_from_docs("Forty-three Skills"), 43)
        self.assertEqual(parse_skill_count_from_docs("2 Skills"), 2)
        _seed_memory(self.tmp, skill_docs="2 Skills")
        self.assertEqual(count_skills_fs(self.tmp), 2)
        drift = detect_drift(self.tmp)
        kinds = {f["kind"] for f in drift["findings"]}
        self.assertNotIn("skill_count_mismatch", kinds)

    def test_skill_count_mismatch(self) -> None:
        _seed_memory(self.tmp, skill_docs="99 Skills")
        drift = detect_drift(self.tmp)
        kinds = {f["kind"] for f in drift["findings"]}
        self.assertIn("skill_count_mismatch", kinds)

    def test_version_progress_mismatch(self) -> None:
        _seed_memory(self.tmp, progress_version="no-version-here")
        drift = detect_drift(self.tmp)
        kinds = {f["kind"] for f in drift["findings"]}
        self.assertIn("version_progress_mismatch", kinds)

    def test_missing_memory_docs(self) -> None:
        (self.tmp / "VERSION").write_text("1.0.0\n", encoding="utf-8")
        drift = detect_drift(self.tmp)
        kinds = {f["kind"] for f in drift["findings"]}
        self.assertIn("missing_memory_docs", kinds)


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m51-svc-"))
        _seed_memory(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_snapshot_persist_and_explain(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            result = snapshot(self.tmp)
            doc = result["snapshot"]
            self.assertFalse(doc["approved_for_execution"])
            self.assertFalse(doc["authority_mutation"])
            self.assertTrue(doc["snapshot_id"].startswith("psnap-"))
            loaded = load_snapshot(self.tmp, doc["snapshot_id"])
            self.assertEqual(loaded["snapshot_id"], doc["snapshot_id"])
            explained = explain(self.tmp, snapshot_id=doc["snapshot_id"])
            self.assertIn("stub-generated", explained["snapshot"]["explanation"])

    def test_reconcile_proposal_only(self) -> None:
        _seed_memory(self.tmp, skill_docs="99 Skills")
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            result = draft_reconcile(self.tmp)
            self.assertFalse(result["applied"])
            self.assertFalse(result["proposal"]["applied"])
            self.assertFalse(result["proposal"]["approved_for_execution"])
            path = Path(result["path"])
            self.assertTrue(path.is_file())
            # Memory docs must not be rewritten by reconcile.
            ctx = (self.tmp / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
            self.assertIn("99 Skills", ctx)

    def test_service_requires_gate(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_STATUS_ENABLED", None)
            with self.assertRaises(PermissionError):
                snapshot(self.tmp)

    def test_export_csv(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            take_snapshot(self.tmp, persist=True)
            dest = self.tmp / "status.csv"
            path = export_csv(self.tmp, dest)
            text = path.read_text(encoding="utf-8")
            self.assertIn("snapshot_id", text)
            self.assertIn("psnap-", text)

    def test_cli_fail_closed_and_snapshot(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_STATUS_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-status.sh"),
                "snapshot",
                "--repo-root",
                str(self.tmp),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_STATUS_ENABLED", proc.stderr)

        env["COMPASS_STATUS_ENABLED"] = "1"
        ok = subprocess.run(
            [
                str(ROOT / "scripts" / "run-status.sh"),
                "snapshot",
                "--repo-root",
                str(self.tmp),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(ok.returncode, 0, ok.stderr)
        payload = json.loads(ok.stdout)
        self.assertEqual(payload["status"], "snapshotted")
        self.assertFalse(payload["snapshot"]["authority_mutation"])
        self.assertEqual(len(list_snapshots(self.tmp)), 1)

    def test_compare_since_head(self) -> None:
        # Initialize a tiny git repo so compare can archive HEAD.
        subprocess.run(["git", "init"], cwd=self.tmp, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "m51@test.local"],
            cwd=self.tmp,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "M51 Test"],
            cwd=self.tmp,
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "add", "."], cwd=self.tmp, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "seed"],
            cwd=self.tmp,
            check=True,
            capture_output=True,
        )
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.tmp,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        # Mutate after commit so current differs from archived prior.
        (self.tmp / "PROJECT_CONTEXT.md").write_text(
            "NorthStar control repo with 99 Skills in .cursor/skills.\n",
            encoding="utf-8",
        )
        result = compare_since(self.tmp, sha)
        self.assertEqual(result["status"], "compared")
        self.assertIn("skill_count_mismatch", result["added_finding_kinds"])
        self.assertFalse(result["authority_mutation"])


class BuildSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m51-build-"))
        _seed_memory(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_build_has_fail_closed_flags(self) -> None:
        doc = build_snapshot(self.tmp)
        self.assertFalse(doc["approved_for_execution"])
        self.assertFalse(doc["authority_mutation"])
        self.assertEqual(doc["provider"]["name"], "stub")


if __name__ == "__main__":
    unittest.main()
