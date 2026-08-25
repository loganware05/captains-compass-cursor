"""M11 fixture embedding provider + package-registry file TI tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from orchestrator.knowledge.adapters.embeddings import (
    FixtureEmbeddingProvider,
    select_embedding_provider,
)
from orchestrator.knowledge.embedding_index import (
    write_embedding_index,
)
from orchestrator.knowledge.query import query_knowledge
from orchestrator.knowledge.store import write_knowledge_item
from orchestrator.knowledge.vector_index import write_vector_index
from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider
from orchestrator.providers.technology_intelligence.mapper import (
    candidate_from_package_registry_shaped,
)
from orchestrator.providers.technology_intelligence.package_registry_file_provider import (
    PackageRegistryFileTechnologyIntelligenceProvider,
)

ROOT = Path(__file__).resolve().parents[2]
PKG_FIXTURES = ROOT / "tests" / "fixtures" / "ti" / "package-registry-recorded"


def _sample_item(item_id: str, title: str, summary: str) -> dict:
    return {
        "item_id": item_id,
        "kind": "knowledge",
        "title": title,
        "summary": summary,
        "tags": ["m11"],
        "provenance": {"source": "test"},
        "source_artifact": {"type": "fixture", "id": item_id, "path": f"tests/{item_id}.md"},
        "created_at": "2026-08-24T00:00:00Z",
        "updated_at": "2026-08-24T00:00:00Z",
    }


class FixtureEmbeddingTests(unittest.TestCase):
    def test_select_default_is_tfidf_none(self) -> None:
        old = os.environ.pop("COMPASS_EMBEDDING_PROVIDER", None)
        try:
            self.assertIsNone(select_embedding_provider())
        finally:
            if old is not None:
                os.environ["COMPASS_EMBEDDING_PROVIDER"] = old

    def test_fixture_provider_deterministic(self) -> None:
        provider = FixtureEmbeddingProvider()
        a = provider.embed(["matcher tuning routing weights"])[0]
        b = provider.embed(["matcher tuning routing weights"])[0]
        self.assertEqual(a, b)
        self.assertEqual(len(a), provider.dimensions)

    def test_dense_then_tfidf_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_knowledge_item(
                repo,
                _sample_item(
                    "know-m11-routing",
                    "Matcher routing weights",
                    "Bounded autonomy and matcher tuning for experience routing",
                ),
            )
            write_knowledge_item(
                repo,
                _sample_item(
                    "know-m11-forms",
                    "Accessible react forms",
                    "Form validation patterns for accessible UI",
                ),
            )
            write_vector_index(repo)

            # Without embedding provider → TF-IDF backend
            old_emb = os.environ.pop("COMPASS_EMBEDDING_PROVIDER", None)
            try:
                results = query_knowledge(repo, "matcher routing", mode="vector", top_n=5)
                self.assertTrue(results)
                self.assertEqual(results[0].get("vector_backend"), "tfidf")
            finally:
                if old_emb is not None:
                    os.environ["COMPASS_EMBEDDING_PROVIDER"] = old_emb

            # With fixture + dense index → fixture-embedding backend
            os.environ["COMPASS_EMBEDDING_PROVIDER"] = "fixture"
            try:
                write_embedding_index(repo)
                results = query_knowledge(repo, "matcher routing", mode="vector", top_n=5)
                self.assertTrue(results)
                self.assertEqual(results[0].get("vector_backend"), "fixture-embedding")

                # Remove dense index → TF-IDF fallback while provider still fixture
                (repo / ".agent" / "knowledge" / "embedding-index.json").unlink()
                results = query_knowledge(repo, "matcher routing", mode="vector", top_n=5)
                self.assertTrue(results)
                self.assertEqual(results[0].get("vector_backend"), "tfidf")
            finally:
                os.environ.pop("COMPASS_EMBEDDING_PROVIDER", None)
                if old_emb is not None:
                    os.environ["COMPASS_EMBEDDING_PROVIDER"] = old_emb


class PackageRegistryFileTITests(unittest.TestCase):
    def test_mapper_and_provider(self) -> None:
        raw = json.loads((PKG_FIXTURES / "packages.json").read_text(encoding="utf-8"))[0]
        cand = candidate_from_package_registry_shaped(raw)
        self.assertFalse(cand.to_dict()["approved_for_execution"])
        provider = PackageRegistryFileTechnologyIntelligenceProvider(PKG_FIXTURES)
        found = provider.discover_candidates("schema validation typescript", {})
        self.assertTrue(found)
        blob = (found[0].discovery_signal + " ".join(found[0].capabilities_provided)).lower()
        self.assertTrue("schema" in blob or "zod" in blob or "typescript" in blob)

    def test_select_ti_provider_package_registry_file(self) -> None:
        old = os.environ.get("COMPASS_TI_PROVIDER")
        os.environ["COMPASS_TI_PROVIDER"] = "package-registry-file"
        os.environ["COMPASS_PACKAGE_TI_FIXTURES_DIR"] = str(PKG_FIXTURES)
        try:
            provider = select_ti_provider()
            self.assertIsInstance(provider, PackageRegistryFileTechnologyIntelligenceProvider)
            found = provider.discover_candidates("react forms accessible", {})
            self.assertTrue(found)
        finally:
            if old is None:
                os.environ.pop("COMPASS_TI_PROVIDER", None)
            else:
                os.environ["COMPASS_TI_PROVIDER"] = old
            os.environ.pop("COMPASS_PACKAGE_TI_FIXTURES_DIR", None)


if __name__ == "__main__":
    unittest.main()
