"""M6 Vector Experience Store — TF-IDF index, hybrid query, plan integration tests."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from orchestrator.knowledge.index import write_index
from orchestrator.knowledge.ingest import ingest_path, items_from_decisions_md
from orchestrator.knowledge.query import query_knowledge
from orchestrator.knowledge.store import write_knowledge_item
from orchestrator.knowledge.vector_index import (
    build_vector_index,
    cosine_similarity,
    select_knowledge_search_mode,
    vector_index_exists,
    write_vector_index,
)
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
EXPERIENCE_FIXTURE = ROOT / "tests" / "fixtures" / "experience" / "contact-counter.json"


def _seed_items(repo: Path) -> None:
    ingest_path(repo, EXPERIENCE_FIXTURE)
    for item in items_from_decisions_md(
        "## ADR-050: Matcher tuning policy\n\nRouting weights require Captain approval.\n",
        "DECISIONS.md",
    ):
        write_knowledge_item(repo, item)
    write_index(repo)
    write_vector_index(repo)


class VectorIndexTests(unittest.TestCase):
    def test_build_vector_index_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_items(repo)
            first = build_vector_index(repo)
            second = build_vector_index(repo)
            self.assertEqual(first["item_count"], second["item_count"])
            self.assertEqual(first["vectors"], second["vectors"])
            validate_document(first, "vector-index.schema.json")

    def test_cosine_similarity(self) -> None:
        score = cosine_similarity({"a": 1.0, "b": 1.0}, {"a": 1.0, "b": 1.0})
        self.assertAlmostEqual(score, 1.0, places=4)

    def test_select_mode_hybrid_when_vector_index_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_items(repo)
            self.assertTrue(vector_index_exists(repo))
            self.assertEqual(select_knowledge_search_mode(repo), "hybrid")


class HybridQueryTests(unittest.TestCase):
    def test_keyword_default_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_items(repo)
            results = query_knowledge(repo, "react testing", mode="keyword", top_n=3)
            self.assertTrue(results)
            self.assertEqual(results[0]["search_mode"], "keyword")

    def test_vector_mode_requires_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ingest_path(repo, EXPERIENCE_FIXTURE)
            write_index(repo)
            results = query_knowledge(repo, "react testing", mode="vector", top_n=3)
            self.assertEqual(results, [])

    def test_hybrid_fallback_without_vector_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ingest_path(repo, EXPERIENCE_FIXTURE)
            write_index(repo)
            results = query_knowledge(repo, "react testing", mode="hybrid", top_n=3)
            self.assertTrue(results)
            self.assertEqual(results[0]["search_mode"], "hybrid")
            self.assertEqual(results[0].get("search_fallback"), "keyword-only")

    def test_hybrid_merge_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _seed_items(repo)
            results = query_knowledge(repo, "matcher routing captain", mode="hybrid", top_n=5)
            self.assertTrue(results)
            top = results[0]
            self.assertEqual(top["search_mode"], "hybrid")
            self.assertIn("keyword_score", top)
            self.assertIn("vector_score", top)


class PlanHybridKnowledgeContextTests(unittest.TestCase):
    def test_plan_renders_hybrid_knowledge_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            for name in (".cursor", "orchestrator", "scripts", "tests"):
                shutil.copytree(ROOT / name, repo / name, dirs_exist_ok=True)
            _seed_items(repo)
            plan = build_capability_plan(repo, "matcher routing captain approval", plan_id="m6-kc")
            self.assertEqual(plan.knowledge_search_mode, "hybrid")
            markdown = render_capability_plan_sections(plan)
            self.assertIn("## Knowledge Context", markdown)
            self.assertIn("hybrid search", markdown)


if __name__ == "__main__":
    unittest.main()
