"""M52 Project Overseer Skill + opt-in live StatusProvider — hermetic tests."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.status.drift import parse_skill_count_from_docs
from orchestrator.status.memory import write_overseer_memory
from orchestrator.status.providers.http import HttpStatusProvider, HttpStatusProviderError
from orchestrator.status.providers.select import (
    StatusProviderSelectError,
    select_status_provider,
)
from orchestrator.status.providers.stub import StubStatusProvider
from orchestrator.status.service import explain, snapshot
from orchestrator.status.snapshot import take_snapshot


def _seed_memory(repo: Path) -> None:
    (repo / "VERSION").write_text("1.57.0\n", encoding="utf-8")
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
        "NorthStar control repo with 2 Skills in .cursor/skills.\n",
        encoding="utf-8",
    )
    (repo / "IMPLEMENTATION_PLAN.md").write_text(
        "# Plan\n\n- Status: APPROVED\n\n"
        "| Field | Value |\n|---|---|\n| Plan ID | `m52-overseer-skill-live-provider` |\n",
        encoding="utf-8",
    )
    (repo / "PROGRESS.md").write_text(
        "## Current status\n\nActive plan `m52-overseer-skill-live-provider` · v1.57.0.\n",
        encoding="utf-8",
    )
    skill_root = repo / ".cursor" / "skills"
    for name in ("alpha", "beta"):
        d = skill_root / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")


class ProviderSelectTests(unittest.TestCase):
    def test_default_stub(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_STATUS_PROVIDER", None)
            provider = select_status_provider()
            self.assertIsInstance(provider, StubStatusProvider)

    def test_unknown_provider(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_PROVIDER": "kimi-magic"}):
            with self.assertRaises(StatusProviderSelectError):
                select_status_provider()

    def test_http_requires_key_and_model(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"COMPASS_STATUS_PROVIDER": "http"},
            clear=False,
        ):
            os.environ.pop("OPENROUTER_API_KEY", None)
            os.environ.pop("COMPASS_STATUS_API_KEY", None)
            os.environ.pop("COMPASS_STATUS_MODEL", None)
            with self.assertRaises(StatusProviderSelectError):
                select_status_provider()


class HttpProviderTests(unittest.TestCase):
    def test_mocked_http_explain(self) -> None:
        def fake_post(url, headers, body, timeout):  # noqa: ANN001
            self.assertTrue(url.startswith("https://"))
            self.assertIn("Authorization", headers)
            payload = {
                "choices": [
                    {
                        "message": {
                            "content": "Observed: version matches. Proposed: none."
                        }
                    }
                ]
            }
            return json.dumps(payload).encode("utf-8")

        provider = HttpStatusProvider(
            api_key="test-key",
            model="test-model",
            http_post=fake_post,
        )
        text = provider.explain(
            {
                "northstar_version": "1.57.0",
                "repository_sha": "abc",
                "findings": [
                    {
                        "kind": "memory_docs",
                        "severity": "info",
                        "claim_kind": "observed",
                        "summary": "ok",
                    }
                ],
            }
        )
        self.assertIn("Observed", text)
        self.assertEqual(provider.model, "test-model")

    def test_http_rejects_non_https(self) -> None:
        with self.assertRaises(HttpStatusProviderError):
            HttpStatusProvider(
                api_key="k",
                model="m",
                url="http://example.com/v1/chat/completions",
            )

    def test_http_fail_closed_on_bad_shape(self) -> None:
        provider = HttpStatusProvider(
            api_key="k",
            model="m",
            http_post=lambda *a, **k: b'{"choices":[]}',
        )
        with self.assertRaises(HttpStatusProviderError):
            provider.explain({"findings": []})


class MemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m52-mem-"))
        _seed_memory(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_system_map_and_ledger_only(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            snap = take_snapshot(self.tmp, persist=True, write_memory=True)
        paths = write_overseer_memory(self.tmp, snap)
        map_path = Path(paths["system_map"])
        ledger_path = Path(paths["scope_ledger"])
        self.assertTrue(map_path.is_file())
        self.assertTrue(ledger_path.is_file())
        self.assertIn("Non-canonical", map_path.read_text(encoding="utf-8"))
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        validate_document(ledger, "scope-ledger.schema.json")
        self.assertTrue(ledger["canonical_memory_untouched"])
        self.assertFalse(ledger["approved_for_execution"])
        # Canonical memory unchanged by Overseer memory writers.
        ctx = (self.tmp / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("2 Skills", ctx)

    def test_scope_ledger_schema_lock(self) -> None:
        bad = {
            "schema_version": "1",
            "created_at": "2026-10-11T00:00:00Z",
            "snapshot_id": "psnap-x",
            "entries": [],
            "canonical_memory_untouched": True,
            "approved_for_execution": True,
            "authority_mutation": False,
        }
        with self.assertRaises(ValidationError):
            validate_document(bad, "scope-ledger.schema.json")


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m52-svc-"))
        _seed_memory(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_explain_uses_stub_and_memory(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"COMPASS_STATUS_ENABLED": "1", "COMPASS_STATUS_PROVIDER": "stub"},
        ):
            result = explain(self.tmp)
        self.assertIn("stub-generated", result["snapshot"]["explanation"])
        self.assertEqual(result["snapshot"]["provider"]["name"], "stub")
        self.assertTrue((self.tmp / ".agent" / "status" / "system-map.md").is_file())
        self.assertTrue((self.tmp / ".agent" / "status" / "scope-ledger.json").is_file())

    def test_http_service_fail_closed(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_STATUS_ENABLED": "1",
                "COMPASS_STATUS_PROVIDER": "http",
            },
            clear=False,
        ):
            os.environ.pop("OPENROUTER_API_KEY", None)
            os.environ.pop("COMPASS_STATUS_API_KEY", None)
            os.environ.pop("COMPASS_STATUS_MODEL", None)
            from orchestrator.status.service import StatusServiceError

            with self.assertRaises(StatusServiceError):
                explain(self.tmp)

    def test_skill_and_agent_exist(self) -> None:
        self.assertTrue(
            (ROOT / ".cursor" / "skills" / "project-overseer" / "SKILL.md").is_file()
        )
        self.assertTrue((ROOT / ".cursor" / "agents" / "project-overseer.md").is_file())
        self.assertEqual(parse_skill_count_from_docs("Forty-four Skills"), 44)


class SnapshotClaimTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m52-claim-"))
        _seed_memory(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_findings_carry_claim_kind(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_STATUS_ENABLED": "1"}):
            result = snapshot(self.tmp)
        for finding in result["snapshot"]["findings"]:
            self.assertIn(finding.get("claim_kind"), {
                "observed",
                "documented",
                "external",
                "proposed",
            })


if __name__ == "__main__":
    unittest.main()
