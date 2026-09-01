"""M15 live Notion MCP knowledge ingest tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from shutil import copytree

from orchestrator.knowledge.notion_live import (
    NotionLiveError,
    ingest_notion_live_pages,
    item_from_notion_live,
    load_allowlist,
    normalize_page_id,
    write_notion_live_cache,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PAGE_ID = "3cae6a901c4381fd8482e9158ac9e6cc"


class NotionLiveIngestTests(unittest.TestCase):
    def test_normalize_page_id_from_url(self) -> None:
        url = f"https://www.notion.so/workspace/Page-{FIXTURE_PAGE_ID}"
        self.assertEqual(normalize_page_id(url), FIXTURE_PAGE_ID)

    def test_item_from_notion_live_provenance(self) -> None:
        text = "# Demo\n\nBody text for MCP live ingest."
        item = item_from_notion_live(
            text,
            ".agent/knowledge/external/notion-live/demo.md",
            page_id=FIXTURE_PAGE_ID,
            source_url="https://www.notion.so/example/demo",
        )
        self.assertEqual(item["kind"], "knowledge")
        self.assertEqual(item["provenance"]["export_mode"], "mcp_live")
        self.assertEqual(item["provenance"]["notion_page_id"], FIXTURE_PAGE_ID)
        self.assertEqual(item["item_id"], f"know-notion-{FIXTURE_PAGE_ID[:12]}")

    def test_ingest_fixtures_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            allowlist_src = ROOT / "tests" / "fixtures" / "knowledge" / "notion-allowlist.txt"
            fixtures_src = ROOT / "tests" / "fixtures" / "knowledge" / "external" / "notion-live"
            (repo / ".agent" / "knowledge").mkdir(parents=True)
            (repo / ".agent" / "knowledge" / "notion-allowlist.txt").write_text(
                allowlist_src.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            copytree(fixtures_src, repo / "tests" / "fixtures" / "knowledge" / "external" / "notion-live")
            result = ingest_notion_live_pages(repo, source="fixtures")
            self.assertEqual(len(result["items"]), 1)
            self.assertEqual(result["items"][0]["provenance"]["export_mode"], "mcp_live")

    def test_allowlist_rejects_unknown_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".agent" / "knowledge").mkdir(parents=True)
            (repo / ".agent" / "knowledge" / "notion-allowlist.txt").write_text(
                f"{FIXTURE_PAGE_ID}\n",
                encoding="utf-8",
            )
            copytree(
                ROOT / "tests" / "fixtures" / "knowledge" / "external" / "notion-live",
                repo / "tests" / "fixtures" / "knowledge" / "external" / "notion-live",
            )
            with self.assertRaises(NotionLiveError):
                ingest_notion_live_pages(
                    repo,
                    source="fixtures",
                    page_ids=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
                )

    def test_cache_source_after_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".agent" / "knowledge").mkdir(parents=True)
            (repo / ".agent" / "knowledge" / "notion-allowlist.txt").write_text(
                f"{FIXTURE_PAGE_ID}\n",
                encoding="utf-8",
            )
            write_notion_live_cache(
                repo,
                FIXTURE_PAGE_ID,
                "# Cached page\n\nFrom MCP fetch cache.\n",
            )
            result = ingest_notion_live_pages(repo, source="cache")
            self.assertEqual(len(result["items"]), 1)

    def test_live_payload_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".agent" / "knowledge").mkdir(parents=True)
            (repo / ".agent" / "knowledge" / "notion-allowlist.txt").write_text(
                f"{FIXTURE_PAGE_ID}\n",
                encoding="utf-8",
            )
            payload = repo / "mcp-payload.json"
            payload.write_text(
                json.dumps(
                    {
                        "pages": [
                            {
                                "page_id": FIXTURE_PAGE_ID,
                                "markdown": "# Payload page\n\nLive MCP payload ingest.\n",
                                "source_url": "https://www.notion.so/example/payload",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = ingest_notion_live_pages(repo, source="live", payload_path=payload)
            self.assertEqual(len(result["items"]), 1)
            self.assertEqual(result["items"][0]["provenance"]["export_mode"], "mcp_live")

    def test_load_allowlist_fixture(self) -> None:
        path = ROOT / "tests" / "fixtures" / "knowledge" / "notion-allowlist.txt"
        ids = load_allowlist(ROOT, allowlist_path=path)
        self.assertIn(FIXTURE_PAGE_ID, ids)


if __name__ == "__main__":
    unittest.main()
