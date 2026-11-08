"""I3 Apify TI provider + research CLI (fixture-first)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.integrations.apify import service
from orchestrator.providers.technology_intelligence.apify_file_provider import (
    ApifyFileTechnologyIntelligenceProvider,
)
from orchestrator.providers.technology_intelligence.apify_live_provider import (
    ApifyLiveTechnologyIntelligenceProvider,
)
from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider
from orchestrator.providers.technology_intelligence.mapper import (
    candidate_from_apify_shaped,
)
from orchestrator.status.development_refs import collect_research_refs


REPO = Path(__file__).resolve().parents[2]


class ApifyMapperTests(unittest.TestCase):
    def test_mapper_locks(self) -> None:
        cand = candidate_from_apify_shaped(
            {
                "actor_id": "apify/rag-web-browser",
                "title": "RAG Web Browser",
                "capabilities_provided": ["web-research"],
            }
        )
        doc = cand.to_dict()
        self.assertEqual(doc["kind"], "candidate")
        self.assertIs(doc["approved_for_execution"], False)
        self.assertTrue(doc["source"]["path"].startswith("apify:"))


class ApifyFileProviderTests(unittest.TestCase):
    def test_discover_from_fixtures(self) -> None:
        provider = ApifyFileTechnologyIntelligenceProvider()
        found = provider.discover_candidates("web research browser", {})
        self.assertGreaterEqual(len(found), 1)
        self.assertTrue(all(c.to_dict()["approved_for_execution"] is False for c in found))

    def test_select_apify_file(self) -> None:
        os.environ["COMPASS_TI_PROVIDER"] = "apify-file"
        try:
            provider = select_ti_provider()
            self.assertIsInstance(provider, ApifyFileTechnologyIntelligenceProvider)
        finally:
            os.environ.pop("COMPASS_TI_PROVIDER", None)


class ApifyLiveProviderTests(unittest.TestCase):
    def test_live_fail_closed_without_gates(self) -> None:
        provider = ApifyLiveTechnologyIntelligenceProvider()
        with self.assertRaises(PermissionError):
            provider.discover_candidates("anything", {})

    def test_live_skeleton_with_gates(self) -> None:
        provider = ApifyLiveTechnologyIntelligenceProvider()
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_APIFY_ENABLED": "1",
                "COMPASS_APIFY_LIVE": "1",
                "COMPASS_APIFY_TOKEN": "test-token",
            },
            clear=False,
        ):
            with self.assertRaises(RuntimeError) as ctx:
                provider.discover_candidates("anything", {})
            self.assertIn("skeleton", str(ctx.exception).lower())

    def test_select_apify_live(self) -> None:
        os.environ["COMPASS_TI_PROVIDER"] = "apify-live"
        try:
            provider = select_ti_provider()
            self.assertIsInstance(provider, ApifyLiveTechnologyIntelligenceProvider)
        finally:
            os.environ.pop("COMPASS_TI_PROVIDER", None)


class ApifyServiceTests(unittest.TestCase):
    def test_search_persist_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Minimal schema for soft/jsonschema validation
            schema_dir = root / "orchestrator" / "schemas"
            schema_dir.mkdir(parents=True)
            schema_dir.joinpath("apify-research-packet.schema.json").write_text(
                (REPO / "orchestrator/schemas/apify-research-packet.schema.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"COMPASS_APIFY_ENABLED": "1"}, clear=False):
                result = service.search(root, "web research")
                packet = result["packet"]
                self.assertEqual(packet["provider"], "apify")
                self.assertIs(packet["called_actor"], False)
                self.assertIs(packet["approved_for_execution"], False)
                listed = service.list_packets(root)
                self.assertEqual(listed["count"], 1)
                shown = service.show(root, packet["packet_id"])
                self.assertEqual(shown["packet"]["packet_id"], packet["packet_id"])
            refs = collect_research_refs(root)
            self.assertEqual(len(refs), 1)
            self.assertEqual(refs[0]["claim_kind"], "external")

    def test_search_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ.pop("COMPASS_APIFY_ENABLED", None)
                with self.assertRaises(PermissionError):
                    service.search(Path(tmp), "x")

    def test_live_search_deferred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(
                os.environ,
                {"COMPASS_APIFY_ENABLED": "1", "COMPASS_APIFY_LIVE": "1"},
                clear=False,
            ):
                with self.assertRaises(RuntimeError):
                    service.search(Path(tmp), "x", live=True)


if __name__ == "__main__":
    unittest.main()
