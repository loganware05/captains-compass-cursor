"""M5 Knowledge Steward ingest, index, query, and procedure promotion tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.knowledge.index import build_index, tokenize, write_index
from orchestrator.knowledge.ingest import ingest_path, ingest_store_roots, items_from_decisions_md
from orchestrator.knowledge.promote import (
    ProcedurePromotionError,
    build_procedure_proposal,
    write_procedure_proposal,
)
from orchestrator.knowledge.query import query_knowledge
from orchestrator.knowledge.store import KnowledgeStoreError, list_knowledge_items
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
EXPERIENCE_FIXTURE = ROOT / "tests" / "fixtures" / "experience" / "contact-counter.json"
DECISIONS_MD = ROOT / "DECISIONS.md"


class KnowledgeSchemaTests(unittest.TestCase):
    def test_tokenize_deterministic(self) -> None:
        a = tokenize("Knowledge Steward evaluator routing")
        b = tokenize("Knowledge Steward evaluator routing")
        self.assertEqual(a, b)


class IngestTests(unittest.TestCase):
    def test_ingest_experience_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            written = ingest_path(repo, EXPERIENCE_FIXTURE)
            self.assertEqual(len(written), 1)
            validate_document(written[0], "knowledge-item.schema.json")
            write_index(repo)
            self.assertTrue(list_knowledge_items(repo))

    def test_adr_headings_from_decisions(self) -> None:
        items = items_from_decisions_md(
            "## ADR-099: Test decision\n\nContext line.\n",
            "DECISIONS.md",
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["kind"], "decision")
        self.assertTrue(items[0]["item_id"].startswith("know-adr-"))

    def test_ingest_decisions_store_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "DECISIONS.md").write_text(
                "## ADR-001: Sample\n\nSample context.\n", encoding="utf-8"
            )
            result = ingest_store_roots(repo, ["decisions"])
            self.assertGreaterEqual(result["audit"]["item_count"], 1)

    def test_rejects_secret_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            secret = repo / ".env"
            secret.write_text("X=1", encoding="utf-8")
            with self.assertRaises(KnowledgeStoreError):
                ingest_path(repo, secret)


class QueryTests(unittest.TestCase):
    def test_query_returns_ranked_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ingest_path(repo, EXPERIENCE_FIXTURE)
            write_index(repo)
            results = query_knowledge(repo, "react testing validation", top_n=5)
            self.assertTrue(results)
            self.assertIn("query_score", results[0])


class ProcedurePromotionTests(unittest.TestCase):
    def test_staging_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            items = items_from_decisions_md(
                "## ADR-010: Procedure source\n\nGate test.\n", "DECISIONS.md"
            )
            for item in items:
                from orchestrator.knowledge.store import write_knowledge_item

                write_knowledge_item(repo, item)
            proposal = build_procedure_proposal(
                items, procedure_title="Test Procedure Playbook"
            )
            path = write_procedure_proposal(repo, proposal, items)
            self.assertTrue(path.is_file())
            written = json.loads(path.read_text(encoding="utf-8"))
            playbook = repo / written["staging_paths"]["playbook_markdown"]
            self.assertTrue(playbook.is_file())
            self.assertFalse((repo / ".cursor" / "skills" / "x").exists())

    def test_rejects_empty_items(self) -> None:
        with self.assertRaises(ProcedurePromotionError):
            build_procedure_proposal([], procedure_title="Empty")


class PlanKnowledgeContextTests(unittest.TestCase):
    def test_plan_renders_knowledge_context_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            # Copy minimal structure for capability plan
            import shutil

            for name in (".cursor", "orchestrator", "scripts", "tests"):
                src = ROOT / name
                if src.is_dir():
                    shutil.copytree(src, repo / name, dirs_exist_ok=True)
            ingest_path(repo, EXPERIENCE_FIXTURE)
            write_index(repo)
            plan = build_capability_plan(repo, "react testing dashboard", plan_id="m5-kc")
            markdown = render_capability_plan_sections(plan)
            self.assertIn("## Knowledge Context", markdown)

    def test_empty_store_plan_unchanged_rankings(self) -> None:
        first = build_capability_plan(ROOT, "Build a React dashboard", plan_id="m5-empty-a")
        second = build_capability_plan(ROOT, "Build a React dashboard", plan_id="m5-empty-b")
        self.assertEqual(first.resolve["ranked_skills"], second.resolve["ranked_skills"])


class RealDecisionsIngestTests(unittest.TestCase):
    def test_real_decisions_has_adrs(self) -> None:
        items = items_from_decisions_md(DECISIONS_MD.read_text(encoding="utf-8"), "DECISIONS.md")
        self.assertGreater(len(items), 5)
        self.assertTrue(any("ADR-020" in i["title"] for i in items))


if __name__ == "__main__":
    unittest.main()
