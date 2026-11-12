"""C2 session memory — dual gate, progressive search, authority locks."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-session-memory-tests"
FIXTURE_OBS = ROOT / "tests" / "fixtures" / "session-memory" / "obs-design-gate-approved.json"

from orchestrator.cognitive.session_memory import (
    SessionMemoryError,
    ingest_observation,
    search_observations,
    show_observation,
    timeline_observations,
)
from orchestrator.schemas.validate import validate_document


def _mk_repo() -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="sessmem-", dir=str(_FIXTURE_ROOT)))


class SessionMemoryTests(unittest.TestCase):
    def test_fixture_schema(self) -> None:
        doc = json.loads(FIXTURE_OBS.read_text(encoding="utf-8"))
        validate_document(doc, "session-observation.schema.json")
        self.assertIs(doc["approved_for_execution"], False)
        self.assertIs(doc["authority_mutation"], False)

    def test_dual_gate_cli(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_BRAIN_ENABLED", None)
        env.pop("COMPASS_SESSION_MEMORY_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-brain.sh"),
                "memory",
                "search",
                "--query",
                "design",
                "--repo-root",
                str(ROOT),
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_BRAIN_ENABLED", proc.stderr)

        env["COMPASS_BRAIN_ENABLED"] = "1"
        proc2 = subprocess.run(
            [
                str(ROOT / "scripts" / "run-brain.sh"),
                "memory",
                "search",
                "--query",
                "design",
                "--repo-root",
                str(ROOT),
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc2.returncode, 2)
        self.assertIn("COMPASS_SESSION_MEMORY_ENABLED", proc2.stderr)

    def test_ingest_search_show_progressive(self) -> None:
        repo = _mk_repo()
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BRAIN_ENABLED": "1",
                "COMPASS_SESSION_MEMORY_ENABLED": "1",
            },
        ):
            ingested = ingest_observation(repo, path=FIXTURE_OBS)
            self.assertEqual(ingested["observation_id"], "obs-fixture-design-gate")
            self.assertIs(ingested["approved_for_execution"], False)

            index = search_observations(repo, "session memory design", top_n=5)
            validate_document(index, "session-memory-search-response.schema.json")
            self.assertGreaterEqual(len(index["results"]), 1)
            row = index["results"][0]
            self.assertEqual(row["observation_id"], "obs-fixture-design-gate")
            self.assertNotIn("body", row)

            full = show_observation(repo, "obs-fixture-design-gate")
            self.assertIn("Captain chose sequential", full["body"])
            self.assertIs(full["authority_mutation"], False)

            tl = timeline_observations(repo, limit=5)
            self.assertEqual(tl["results"][0]["observation_id"], "obs-fixture-design-gate")

    def test_secret_rejection(self) -> None:
        repo = _mk_repo()
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BRAIN_ENABLED": "1",
                "COMPASS_SESSION_MEMORY_ENABLED": "1",
            },
        ):
            with self.assertRaises(SessionMemoryError):
                ingest_observation(
                    repo,
                    document={
                        "title": "bad",
                        "summary": "has secret",
                        "body": "api_key=sk-live-not-real",
                        "approved_for_execution": False,
                        "authority_mutation": False,
                    },
                )

    def test_context_include_session_memory(self) -> None:
        repo = _mk_repo()
        # Minimal knowledge/decisions not required — session hits alone OK.
        (repo / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
        (repo / "VERSION").write_text("1.86.0\n", encoding="utf-8")
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BRAIN_ENABLED": "1",
                "COMPASS_SESSION_MEMORY_ENABLED": "1",
            },
        ):
            ingest_observation(repo, path=FIXTURE_OBS)
            from orchestrator.cognitive.context import build_context

            ctx = build_context(
                repo,
                "design-before-plan session memory",
                include_session_memory=True,
            )
            validate_document(ctx, "brain-context-response.schema.json")
            kinds = {c["kind"] for c in ctx["citations"]}
            self.assertIn("session_observation", kinds)
            self.assertTrue(ctx["evidence_linked"])
            self.assertIs(ctx["approved_for_execution"], False)


if __name__ == "__main__":
    unittest.main()
