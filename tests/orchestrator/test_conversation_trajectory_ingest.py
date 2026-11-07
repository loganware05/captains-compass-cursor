"""Conversation trajectory ingest tests (#247)."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "conversations" / "obsidian-chatgpt-sample.md"

from orchestrator.conversation.enabled import (
    conversation_ingest_enabled,
    require_conversation_ingest_enabled,
)
from orchestrator.conversation.parser import (
    ConversationParseError,
    parse_obsidian_chatgpt_export,
)
from orchestrator.conversation.service import (
    ConversationServiceError,
    ingest_conversation_export,
    list_trajectories,
    show_trajectory,
)
from orchestrator.schemas.validate import ValidationError, validate_document


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_CONVERSATION_INGEST_ENABLED", None)
            self.assertFalse(conversation_ingest_enabled())
            with self.assertRaises(PermissionError):
                require_conversation_ingest_enabled()

    def test_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_CONVERSATION_INGEST_ENABLED": "1"}):
            self.assertTrue(conversation_ingest_enabled())


class ParserTests(unittest.TestCase):
    def test_parses_fixture_turns(self) -> None:
        text = FIXTURE.read_text(encoding="utf-8")
        parsed = parse_obsidian_chatgpt_export(text)
        self.assertEqual(parsed.conversation_id, "chatgpt_fixture-conv-001")
        self.assertGreaterEqual(len(parsed.turns), 2)
        self.assertIn("ingest ChatGPT", parsed.turns[0].user_prompt)
        self.assertIn("trajectories", parsed.turns[0].assistant_suggestion)

    def test_empty_raises(self) -> None:
        with self.assertRaises(ConversationParseError):
            parse_obsidian_chatgpt_export("")


class SchemaTests(unittest.TestCase):
    def test_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "trajectory_id": "conv-fixture-t000",
            "conversation_id": "chatgpt_fixture-conv-001",
            "turn_index": 0,
            "source": "obsidian-ai-exporter",
            "model_or_source": "chatgpt",
            "user_prompt": "prompt",
            "assistant_suggestion": "suggestion body",
            "assistant_suggestion_excerpt": "suggestion body",
            "claim_kind": "external",
            "source_path": "tests/fixtures/conversations/obsidian-chatgpt-sample.md",
            "source_sha256": "abc",
            "source_url": None,
            "exported_at": "2026-11-06T18:00:00+00:00",
            "ingested_at": "2026-11-06T18:00:00Z",
            "thread_title": "fixture",
            "keywords": ["conversation"],
            "approved_for_execution": False,
            "authority_mutation": False,
            "auto_promoted": False,
        }
        validate_document(doc, "conversation-trajectory.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "conversation-trajectory.schema.json")


class ServiceTests(unittest.TestCase):
    def test_ingest_show_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".agent").mkdir()
            with mock.patch.dict(os.environ, {"COMPASS_CONVERSATION_INGEST_ENABLED": "1"}):
                result = ingest_conversation_export(
                    repo,
                    FIXTURE,
                    source="obsidian-ai-exporter",
                    draft_exemplar="positive",
                )
                self.assertEqual(result["status"], "ingested")
                self.assertGreaterEqual(result["turn_count"], 2)
                self.assertFalse(result["approved_for_execution"])
                traj_id = result["trajectory_ids"][0]
                shown = show_trajectory(repo, traj_id)
                self.assertEqual(shown["trajectory_id"], traj_id)
                self.assertEqual(shown["claim_kind"], "external")
                listed = list_trajectories(repo)
                self.assertGreaterEqual(listed["count"], 2)
                know_path = repo / ".agent" / "knowledge" / "items" / f"know-{traj_id}.json"
                self.assertTrue(know_path.is_file())
                draft = Path(result["exemplar_draft_path"])
                self.assertTrue(draft.is_file())

    def test_ingest_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COMPASS_CONVERSATION_INGEST_ENABLED", None)
                with self.assertRaises(PermissionError):
                    ingest_conversation_export(Path(tmp), FIXTURE)


class CliTests(unittest.TestCase):
    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_CONVERSATION_INGEST_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-conversation.sh"), "list", "--repo-root", str(ROOT)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_CONVERSATION_INGEST_ENABLED", proc.stderr)

    def test_cli_ingest_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            env = os.environ.copy()
            env["COMPASS_CONVERSATION_INGEST_ENABLED"] = "1"
            env["PYTHONPATH"] = str(ROOT)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-conversation.sh"),
                    "ingest",
                    "--path",
                    str(FIXTURE),
                    "--source",
                    "obsidian-ai-exporter",
                    "--repo-root",
                    str(repo),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertGreaterEqual(payload["turn_count"], 2)


if __name__ == "__main__":
    unittest.main()
