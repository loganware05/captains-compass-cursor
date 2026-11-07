"""I1 Sentry incident intelligence + Overseer development refs."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "sentry" / "sample-issues.json"

from orchestrator.integrations.sentry.enabled import (
    require_sentry_ingest_enabled,
    sentry_ingest_enabled,
)
from orchestrator.integrations.sentry.normalize import normalize_issue
from orchestrator.integrations.sentry.service import (
    SentryServiceError,
    fetch_incidents,
    list_packets,
    show_packet,
)
from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.status.development_refs import (
    attach_development_refs,
    collect_incident_refs,
)
from orchestrator.status.drift import detect_drift
from orchestrator.status.snapshot import build_snapshot


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_SENTRY_INGEST_ENABLED", None)
            self.assertFalse(sentry_ingest_enabled())
            with self.assertRaises(PermissionError):
                require_sentry_ingest_enabled()


class NormalizeTests(unittest.TestCase):
    def test_normalize_fixture_issue(self) -> None:
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        issue = payload["issues"][0]
        packet = normalize_issue(
            issue, org=payload["org"], project=payload["project"], mode="fixture"
        )
        validate_document(packet, "sentry-incident-packet.schema.json")
        self.assertFalse(packet["approved_for_execution"])
        self.assertFalse(packet["write_to_sentry"])
        self.assertEqual(packet["claim_kind"], "external")
        bad = dict(packet)
        bad["write_to_sentry"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "sentry-incident-packet.schema.json")


class ServiceTests(unittest.TestCase):
    def test_fetch_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with mock.patch.dict(os.environ, {"COMPASS_SENTRY_INGEST_ENABLED": "1"}):
                result = fetch_incidents(repo, fixture_path=FIXTURE)
                self.assertEqual(result["mode"], "fixture")
                self.assertGreaterEqual(result["count"], 2)
                self.assertFalse(result["write_to_sentry"])
                packet_id = result["packet_ids"][0]
                shown = show_packet(repo, packet_id)
                self.assertEqual(shown["packet_id"], packet_id)
                listed = list_packets(repo)
                self.assertGreaterEqual(listed["count"], 2)
                refs = collect_incident_refs(repo)
                self.assertGreaterEqual(len(refs), 1)

    def test_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COMPASS_SENTRY_INGEST_ENABLED", None)
                with self.assertRaises(PermissionError):
                    fetch_incidents(Path(tmp), fixture_path=FIXTURE)


class OverseerDevRefsTests(unittest.TestCase):
    def test_snapshot_includes_incident_and_plan_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "VERSION").write_text("1.78.0\n", encoding="utf-8")
            (repo / "PROGRESS.md").write_text(
                "Active plan `i1-sentry-incident-intelligence` IN PROGRESS\n",
                encoding="utf-8",
            )
            (repo / "PROJECT_CONTEXT.md").write_text("# ctx\n", encoding="utf-8")
            (repo / "DECISIONS.md").write_text("# d\n", encoding="utf-8")
            (repo / "TESTING.md").write_text("# t\n", encoding="utf-8")
            (repo / "IMPLEMENTATION_PLAN.md").write_text(
                "# Plan\n\n- Status: **APPROVED**\n\n"
                "| Field | Value |\n|---|---|\n"
                "| Plan ID | `i1-sentry-incident-intelligence` |\n"
                "| Status | **APPROVED** |\n",
                encoding="utf-8",
            )
            (repo / ".cursor" / "skills").mkdir(parents=True)
            with mock.patch.dict(os.environ, {"COMPASS_SENTRY_INGEST_ENABLED": "1"}):
                fetch_incidents(repo, fixture_path=FIXTURE)
            drift = detect_drift(repo)
            kinds = {f.get("kind") for f in drift["findings"]}
            self.assertIn("active_development", kinds)
            self.assertIn("external_incident_evidence", kinds)
            snap: dict = {
                "findings": drift["findings"],
                "provenance_refs": [],
            }
            attach_development_refs(snap, repo)
            self.assertGreaterEqual(len(snap["incident_refs"]), 1)
            full = build_snapshot(repo)
            validate_document(
                {
                    **full,
                    "schema_version": "1",
                    "created_at": "2026-11-07T00:00:00Z",
                },
                "project-status-snapshot.schema.json",
            )


class CliTests(unittest.TestCase):
    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_SENTRY_INGEST_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-sentry.sh"), "list", "--repo-root", str(ROOT)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_SENTRY_INGEST_ENABLED", proc.stderr)


if __name__ == "__main__":
    unittest.main()
