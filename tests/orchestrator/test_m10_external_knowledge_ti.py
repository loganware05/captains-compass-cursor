"""M10 external knowledge ingest + Hugging Face file TI tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from shutil import copytree

from orchestrator.knowledge.ingest import (
    ingest_store_roots,
    item_from_notebooklm_note,
    item_from_notion_export,
)
from orchestrator.providers.technology_intelligence.huggingface_file_provider import (
    HuggingFaceFileTechnologyIntelligenceProvider,
)
from orchestrator.providers.technology_intelligence.mapper import (
    candidate_from_huggingface_shaped,
)
from orchestrator.providers.technology_intelligence.ti_cache import (
    cache_age_hours,
    is_cache_stale,
    refresh_ti_cache,
    write_ti_cache,
)

ROOT = Path(__file__).resolve().parents[2]
NOTION_FIXTURE = (
    ROOT / "tests" / "fixtures" / "knowledge" / "external" / "notion" / "compass-approval-gate.md"
)
NLM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "knowledge"
    / "external"
    / "notebooklm"
    / "agent-orchestration-notes.md"
)
HF_FIXTURES = ROOT / "tests" / "fixtures" / "ti" / "huggingface-recorded"


class ExternalKnowledgeIngestTests(unittest.TestCase):
    def test_notion_mapper(self) -> None:
        text = NOTION_FIXTURE.read_text(encoding="utf-8")
        item = item_from_notion_export(text, "tests/fixtures/knowledge/external/notion/compass-approval-gate.md")
        self.assertEqual(item["kind"], "knowledge")
        self.assertTrue(item["item_id"].startswith("know-notion-"))
        self.assertEqual(item["provenance"]["external_source"], "notion")
        self.assertEqual(item["provenance"]["export_mode"], "file")

    def test_notebooklm_mapper(self) -> None:
        text = NLM_FIXTURE.read_text(encoding="utf-8")
        item = item_from_notebooklm_note(
            text, "tests/fixtures/knowledge/external/notebooklm/agent-orchestration-notes.md"
        )
        self.assertEqual(item["kind"], "knowledge")
        self.assertTrue(item["item_id"].startswith("know-nlm-"))
        self.assertEqual(item["provenance"]["external_source"], "notebooklm")

    def test_ingest_store_roots_notion_notebooklm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            dest = repo / "tests" / "fixtures" / "knowledge" / "external"
            dest.parent.mkdir(parents=True, exist_ok=True)
            copytree(ROOT / "tests" / "fixtures" / "knowledge" / "external", dest)
            result = ingest_store_roots(repo, ["notion", "notebooklm"])
            ids = {i["item_id"] for i in result["items"]}
            self.assertTrue(any(i.startswith("know-notion-") for i in ids))
            self.assertTrue(any(i.startswith("know-nlm-") for i in ids))


class HuggingFaceFileTITests(unittest.TestCase):
    def test_mapper_and_provider(self) -> None:
        raw = json.loads((HF_FIXTURES / "model-cards.json").read_text(encoding="utf-8"))[0]
        cand = candidate_from_huggingface_shaped(raw)
        self.assertFalse(cand.to_dict()["approved_for_execution"])
        provider = HuggingFaceFileTechnologyIntelligenceProvider(HF_FIXTURES)
        found = provider.discover_candidates("sentence embeddings semantic", {})
        self.assertTrue(found)
        self.assertIn("sentence", found[0].discovery_signal.lower() + " ".join(found[0].capabilities_provided).lower())


class TiCacheFreshnessTests(unittest.TestCase):
    def test_fetched_at_and_if_stale_skip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_ti_cache(repo, [{"id": 1, "full_name": "org/demo"}])
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("fetched_at", payload)
            self.assertIn("refreshed_at", payload)
            self.assertFalse(is_cache_stale(repo, max_age_hours=24))
            age = cache_age_hours(repo)
            self.assertIsNotNone(age)
            self.assertLess(age, 1.0)

            # Force stale by rewriting old timestamp
            payload["fetched_at"] = (
                datetime.now(timezone.utc) - timedelta(hours=48)
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            payload["refreshed_at"] = payload["fetched_at"]
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            self.assertTrue(is_cache_stale(repo, max_age_hours=24))

            calls = {"n": 0}

            def fake_fetch(*, limit: int = 100):
                del limit
                calls["n"] += 1
                return [{"id": 2, "full_name": "org/fresh"}]

            import orchestrator.providers.technology_intelligence.ti_cache as mod

            original = mod.fetch_starred_repos
            mod.fetch_starred_repos = fake_fetch  # type: ignore[assignment]
            try:
                # Fresh enough → skip
                payload["fetched_at"] = (
                    datetime.now(timezone.utc) - timedelta(hours=1)
                ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
                payload["refreshed_at"] = payload["fetched_at"]
                path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                refresh_ti_cache(repo, if_stale_hours=24)
                self.assertEqual(calls["n"], 0)
                # Stale → fetch
                payload["fetched_at"] = (
                    datetime.now(timezone.utc) - timedelta(hours=48)
                ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
                payload["refreshed_at"] = payload["fetched_at"]
                path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                refresh_ti_cache(repo, if_stale_hours=24)
                self.assertEqual(calls["n"], 1)
            finally:
                mod.fetch_starred_repos = original  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()
