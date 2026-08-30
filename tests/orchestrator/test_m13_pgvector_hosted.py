"""M13 hosted pgvector / Neon vector adapter tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from orchestrator.knowledge.adapters.pgvector import (
    reset_mock_hosted_vector_backend,
    sync_knowledge_vectors,
)
from orchestrator.knowledge.query import query_knowledge
from orchestrator.knowledge.store import write_knowledge_item
from orchestrator.knowledge.vector_index import write_vector_index


def _sample_item(item_id: str, title: str, summary: str, *, kind: str = "knowledge") -> dict:
    return {
        "item_id": item_id,
        "kind": kind,
        "title": title,
        "summary": summary,
        "tags": ["m13"],
        "provenance": {"source": "test"},
        "source_artifact": {"type": "fixture", "id": item_id, "path": f"tests/{item_id}.md"},
        "created_at": "2026-08-30T00:00:00Z",
        "updated_at": "2026-08-30T00:00:00Z",
    }


class HostedPgvectorTests(unittest.TestCase):
    def tearDown(self) -> None:
        reset_mock_hosted_vector_backend()
        os.environ.pop("COMPASS_VECTOR_PROVIDER", None)
        os.environ.pop("COMPASS_VECTOR_NAMESPACE", None)
        os.environ.pop("COMPASS_EMBEDDING_PROVIDER", None)

    def test_default_file_provider_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_knowledge_item(
                repo,
                _sample_item(
                    "know-m13-routing",
                    "Matcher routing weights",
                    "Bounded autonomy and matcher tuning for experience routing",
                ),
            )
            write_vector_index(repo)
            old_vector = os.environ.pop("COMPASS_VECTOR_PROVIDER", None)
            old_emb = os.environ.pop("COMPASS_EMBEDDING_PROVIDER", None)
            try:
                results = query_knowledge(repo, "matcher routing", mode="vector", top_n=5)
                self.assertTrue(results)
                self.assertEqual(results[0].get("vector_backend"), "tfidf")
            finally:
                if old_vector is not None:
                    os.environ["COMPASS_VECTOR_PROVIDER"] = old_vector
                if old_emb is not None:
                    os.environ["COMPASS_EMBEDDING_PROVIDER"] = old_emb

    def test_mock_pgvector_sync_and_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_knowledge_item(
                repo,
                _sample_item(
                    "know-m13-routing",
                    "Matcher routing weights",
                    "Bounded autonomy and matcher tuning for experience routing",
                ),
            )
            write_knowledge_item(
                repo,
                _sample_item(
                    "know-m13-forms",
                    "Accessible react forms",
                    "Form validation patterns for accessible UI",
                ),
            )
            os.environ["COMPASS_VECTOR_PROVIDER"] = "mock"
            os.environ["COMPASS_VECTOR_NAMESPACE"] = "sandbox-repo"
            os.environ["COMPASS_EMBEDDING_PROVIDER"] = "fixture"
            try:
                report = sync_knowledge_vectors(repo)
                self.assertEqual(report["upserted"], 2)
                self.assertEqual(report["namespace"], "sandbox-repo")

                results = query_knowledge(repo, "matcher routing", mode="vector", top_n=5)
                self.assertTrue(results)
                self.assertEqual(results[0]["item_id"], "know-m13-routing")
                self.assertEqual(results[0].get("vector_backend"), "pgvector-mock")
            finally:
                pass

    def test_hosted_beats_tfidf_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_knowledge_item(
                repo,
                _sample_item(
                    "know-m13-routing",
                    "Matcher routing weights",
                    "Bounded autonomy and matcher tuning for experience routing",
                ),
            )
            write_knowledge_item(
                repo,
                _sample_item(
                    "know-m13-forms",
                    "Accessible react forms",
                    "Form validation patterns for accessible UI",
                ),
            )
            write_vector_index(repo)
            os.environ["COMPASS_VECTOR_PROVIDER"] = "mock"
            os.environ["COMPASS_EMBEDDING_PROVIDER"] = "fixture"
            try:
                sync_knowledge_vectors(repo)
                results = query_knowledge(repo, "matcher routing", mode="vector", top_n=5)
                self.assertEqual(results[0].get("vector_backend"), "pgvector-mock")
            finally:
                pass


if __name__ == "__main__":
    unittest.main()
