"""M8 procedure knowledge ingest and offline TI cache tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.knowledge.ingest import (
    ingest_procedure_playbook,
    ingest_store_roots,
    item_from_procedure_playbook,
)
from orchestrator.knowledge.index import write_index
from orchestrator.knowledge.query import query_knowledge
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections, render_procedure_context
from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider
from orchestrator.providers.technology_intelligence.ti_cache import (
    CachedGithubStarsTechnologyIntelligenceProvider,
    load_recorded_cache_fixtures,
    read_ti_cache,
    write_ti_cache,
)
from orchestrator.providers.technology_intelligence import StubTechnologyIntelligenceProvider
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK_FIXTURE = (
    ROOT / "tests" / "fixtures" / "knowledge" / "procedures" / "bounded-autonomy-apply" / "playbook.md"
)
CACHE_FIXTURES = ROOT / "tests" / "fixtures" / "ti" / "cache-recorded"


class ProcedureIngestTests(unittest.TestCase):
    def test_playbook_maps_to_procedure_kind(self) -> None:
        text = PLAYBOOK_FIXTURE.read_text(encoding="utf-8")
        item = item_from_procedure_playbook(text, str(PLAYBOOK_FIXTURE), lifecycle="staging")
        self.assertEqual(item["kind"], "procedure")
        self.assertEqual(item["item_id"], "know-proc-bounded-autonomy-apply")
        self.assertEqual(item["provenance"]["procedure_lifecycle"], "staging")
        validate_document(item, "knowledge-item.schema.json")

    def test_ingest_procedures_store_root(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            dest = repo / "tests" / "fixtures" / "knowledge" / "procedures" / "bounded-autonomy-apply"
            dest.mkdir(parents=True)
            shutil.copy(PLAYBOOK_FIXTURE, dest / "playbook.md")
            written = ingest_store_roots(repo, ["procedures"])
            self.assertGreaterEqual(written["audit"]["item_count"], 1)
            self.assertTrue(any(i["kind"] == "procedure" for i in written["items"]))

    def test_reingest_overwrites_know_proc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            first = ingest_procedure_playbook(repo, PLAYBOOK_FIXTURE, lifecycle="staging")
            second = ingest_procedure_playbook(repo, PLAYBOOK_FIXTURE, lifecycle="staging")
            self.assertEqual(first[0]["item_id"], second[0]["item_id"])


class ProcedureContextTests(unittest.TestCase):
    def test_renders_empty_procedure_context(self) -> None:
        artifacts = build_capability_plan(ROOT, "unrelated quantum objective", plan_id="m8-proc-empty")
        markdown = render_procedure_context(artifacts)
        self.assertIn("## Procedure Context", markdown)
        self.assertIn("No procedure knowledge items matched", markdown)

    def test_plan_includes_procedure_context_section(self) -> None:
        markdown = render_capability_plan_sections(
            build_capability_plan(ROOT, "Build a React dashboard", plan_id="m8-proc-section")
        )
        self.assertIn("## Procedure Context", markdown)

    def test_procedure_query_after_ingest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ingest_procedure_playbook(repo, PLAYBOOK_FIXTURE, lifecycle="staging")
            write_index(repo)
            results = query_knowledge(repo, "bounded autonomy apply", kind="procedure", top_n=5)
            self.assertTrue(results)
            self.assertEqual(results[0]["kind"], "procedure")


class TiCacheTests(unittest.TestCase):
    def test_cached_provider_reads_fixtures(self) -> None:
        records = load_recorded_cache_fixtures(CACHE_FIXTURES)
        self.assertEqual(len(records), 2)

        def load(_repo: Path) -> list[dict]:
            return records

        provider = CachedGithubStarsTechnologyIntelligenceProvider(load_cache=load)
        candidates = provider.discover_candidates("accessible react forms", {})
        self.assertGreaterEqual(len(candidates), 1)
        for candidate in candidates:
            self.assertFalse(candidate.to_dict()["approved_for_execution"])

    def test_write_and_read_cache_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sample = [{"full_name": "example-org/demo", "description": "demo repo", "topics": ["demo"]}]
            write_ti_cache(repo, sample)
            loaded = read_ti_cache(repo)
            self.assertEqual(len(loaded), 1)

    def test_select_github_stars_cached_provider(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TI_PROVIDER": "github-stars-cached"}):
            provider = select_ti_provider(ROOT)
        self.assertIsInstance(provider, CachedGithubStarsTechnologyIntelligenceProvider)

    def test_select_defaults_stub(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_TI_PROVIDER", None)
            provider = select_ti_provider()
        self.assertIsInstance(provider, StubTechnologyIntelligenceProvider)


if __name__ == "__main__":
    unittest.main()
