"""M7 performance knowledge ingest and live GitHub Stars TI tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.knowledge.ingest import item_from_execution_run, item_from_experience, ingest_path
from orchestrator.knowledge.index import write_index
from orchestrator.knowledge.query import query_knowledge
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections, render_performance_context
from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider
from orchestrator.providers.technology_intelligence.github_stars_provider import (
    GithubStarsTechnologyIntelligenceProvider,
    gh_authenticated,
    load_recorded_starred_fixtures,
)
from orchestrator.providers.technology_intelligence import StubTechnologyIntelligenceProvider
from orchestrator.schemas.validate import validate_document
from orchestrator.telemetry.record import build_execution_run

ROOT = Path(__file__).resolve().parents[2]
EXPERIENCE_FIXTURE = ROOT / "tests" / "fixtures" / "experience" / "contact-counter.json"
STARRED_FIXTURES = ROOT / "tests" / "fixtures" / "ti" / "github-stars-recorded"


class PerformanceIngestTests(unittest.TestCase):
    def test_execution_run_maps_to_performance_kind(self) -> None:
        run = build_execution_run(
            plan_id="plan-m7",
            task_id="task-m7",
            outcome="success",
            skills=["testing-validation"],
            retries=2,
            agents=["implementation-agent"],
            models=["inherit"],
        )
        item = item_from_execution_run(run, "tests/fixtures/runs/demo.json")
        self.assertEqual(item["kind"], "performance")
        self.assertEqual(item["item_id"], f"know-run-{run['run_id']}")
        metrics = item["performance_metrics"]
        self.assertEqual(metrics["outcome"], "success")
        self.assertEqual(metrics["retries"], 2)
        self.assertEqual(metrics["plan_id"], "plan-m7")
        validate_document(item, "knowledge-item.schema.json")

    def test_experience_enriched_with_performance_metrics(self) -> None:
        doc = json.loads(EXPERIENCE_FIXTURE.read_text(encoding="utf-8"))
        item = item_from_experience(doc, str(EXPERIENCE_FIXTURE))
        self.assertEqual(item["kind"], "performance")
        metrics = item["performance_metrics"]
        self.assertIn("capabilities_exercised", metrics)
        self.assertEqual(metrics["run_id"], "run-fixture-contact-counter")
        validate_document(item, "knowledge-item.schema.json")

    def test_reingest_overwrites_know_run_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run = build_execution_run(plan_id="plan-overwrite", outcome="partial")
            run_path = repo / ".agent" / "runs" / f"{run['run_id']}.json"
            run_path.parent.mkdir(parents=True)
            run_path.write_text(json.dumps(run), encoding="utf-8")
            first = ingest_path(repo, run_path)
            self.assertEqual(first[0]["kind"], "performance")
            second = ingest_path(repo, run_path)
            self.assertEqual(second[0]["item_id"], first[0]["item_id"])
            self.assertEqual(second[0]["kind"], "performance")


class PerformanceContextTests(unittest.TestCase):
    def test_renders_empty_performance_context(self) -> None:
        artifacts = build_capability_plan(ROOT, "quantum unrelated objective", plan_id="m7-perf-empty")
        markdown = render_performance_context(artifacts)
        self.assertIn("## Performance Context", markdown)
        self.assertIn("No performance knowledge items matched", markdown)

    def test_plan_includes_performance_context_section(self) -> None:
        markdown = render_capability_plan_sections(
            build_capability_plan(ROOT, "Build a React dashboard", plan_id="m7-perf-section")
        )
        self.assertIn("## Performance Context", markdown)

    def test_performance_query_after_ingest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ingest_path(repo, EXPERIENCE_FIXTURE)
            write_index(repo)
            results = query_knowledge(repo, "react testing", kind="performance", top_n=5)
            self.assertTrue(results)
            self.assertEqual(results[0]["kind"], "performance")


class GithubStarsTiTests(unittest.TestCase):
    def test_recorded_fixtures_map_to_candidates(self) -> None:
        recorded = load_recorded_starred_fixtures(STARRED_FIXTURES)
        self.assertEqual(len(recorded), 3)

        def fetch(**kwargs):
            del kwargs
            return recorded

        provider = GithubStarsTechnologyIntelligenceProvider(fetch_starred=fetch)
        candidates = provider.discover_candidates("accessible react forms", {})
        self.assertGreaterEqual(len(candidates), 1)
        ids = {c.id for c in candidates}
        self.assertTrue(any("accessible-react-forms" in cid for cid in ids))
        for candidate in candidates:
            payload = candidate.to_dict()
            self.assertFalse(payload["approved_for_execution"])

    def test_fails_closed_without_gh_auth(self) -> None:
        with mock.patch(
            "orchestrator.providers.technology_intelligence.github_stars_provider.gh_authenticated",
            return_value=False,
        ):
            provider = GithubStarsTechnologyIntelligenceProvider()
            self.assertEqual(provider.discover_candidates("react", {}), [])

    def test_select_github_stars_provider(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TI_PROVIDER": "github-stars"}):
            provider = select_ti_provider()
        self.assertIsInstance(provider, GithubStarsTechnologyIntelligenceProvider)

    def test_select_defaults_stub(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_TI_PROVIDER", None)
            provider = select_ti_provider()
        self.assertIsInstance(provider, StubTechnologyIntelligenceProvider)

    def test_gh_authenticated_without_gh(self) -> None:
        with mock.patch(
            "orchestrator.providers.technology_intelligence.github_stars_provider.gh_available",
            return_value=False,
        ):
            self.assertFalse(gh_authenticated())


if __name__ == "__main__":
    unittest.main()
