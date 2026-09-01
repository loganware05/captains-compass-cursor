"""Live Notion MCP knowledge ingest (M15) — allowlist-gated, explicit CLI."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from orchestrator.knowledge.index import write_index
from orchestrator.knowledge.ingest import IngestError, ingest_log_dir, item_from_notion_export
from orchestrator.knowledge.store import ensure_store_layout, write_knowledge_item

ALLOWLIST_REL = ".agent/knowledge/notion-allowlist.txt"
NOTION_LIVE_CACHE_DIR = ".agent/knowledge/external/notion-live"
FIXTURES_REL = "tests/fixtures/knowledge/external/notion-live/pages.json"

_PAGE_ID_HEX = re.compile(r"[a-f0-9]{32}", re.I)


class NotionLiveError(IngestError):
    """Raised when live Notion ingest fails."""


def normalize_page_id(raw: str) -> str:
    """Normalize a Notion page ID from UUID or Notion URL."""
    raw = raw.strip()
    if not raw:
        raise NotionLiveError("empty Notion page id")
    # Extract p= parameter for database peek URLs before stripping query string
    if '?' in raw:
        query = raw.split('?', 1)[1].split('#')[0]
        for param in query.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                if key == 'p':
                    raw = value
                    break
    # Strip query parameters and fragments to prevent corruption
    clean = raw.split('?')[0].split('#')[0]
    compact = re.sub(r"[^a-f0-9]", "", clean.lower())
    if len(compact) == 32:
        return compact
    if len(compact) > 32:
        tail = compact[-32:]
        if _PAGE_ID_HEX.fullmatch(tail):
            return tail
    match = _PAGE_ID_HEX.search(clean.replace("-", ""))
    if match:
        return match.group(0).lower()
    raise NotionLiveError(f"invalid Notion page id: {raw!r}")


def load_allowlist(repo_root: Path, *, allowlist_path: Path | None = None) -> list[str]:
    """Load normalized page IDs from the Captain-maintained allowlist."""
    path = allowlist_path or (Path(repo_root) / ALLOWLIST_REL)
    if not path.is_file():
        raise NotionLiveError(f"missing allowlist: {path}")
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        ids.append(normalize_page_id(line))
    if not ids:
        raise NotionLiveError("allowlist is empty")
    return ids


def assert_allowlisted(page_id: str, allowlist: list[str]) -> None:
    if page_id not in allowlist:
        raise NotionLiveError(f"page {page_id} not in allowlist")


def notion_live_cache_dir(repo_root: Path) -> Path:
    return Path(repo_root) / NOTION_LIVE_CACHE_DIR


def item_from_notion_live(
    text: str,
    source_path: str,
    *,
    page_id: str,
    source_url: str | None = None,
) -> dict:
    """Map MCP-fetched Notion page markdown to kind: knowledge."""
    item = item_from_notion_export(text, source_path)
    item["item_id"] = f"know-notion-{page_id[:12]}"
    item["source_artifact"]["type"] = "notion-mcp-live"
    item["source_artifact"]["id"] = page_id
    provenance = dict(item.get("provenance") or {})
    provenance["export_mode"] = "mcp_live"
    provenance["notion_page_id"] = page_id
    if source_url:
        provenance["source_url"] = source_url
    item["provenance"] = provenance
    keywords = list(item.get("keywords") or [])
    if "mcp_live" not in keywords:
        keywords.append("mcp_live")
    item["keywords"] = keywords
    return item


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_fixture_pages(repo_root: Path) -> dict[str, dict[str, Any]]:
    path = Path(repo_root) / FIXTURES_REL
    if not path.is_file():
        raise NotionLiveError(f"missing fixtures: {FIXTURES_REL}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    pages_raw = payload.get("pages")
    if not isinstance(pages_raw, dict):
        raise NotionLiveError(f"invalid fixtures payload: {FIXTURES_REL}")
    pages: dict[str, dict[str, Any]] = {}
    for key, value in pages_raw.items():
        if not isinstance(value, dict):
            continue
        norm = normalize_page_id(str(key))
        pages[norm] = value
    return pages


def _load_cache_pages(repo_root: Path, page_ids: list[str]) -> dict[str, dict[str, Any]]:
    cache_dir = notion_live_cache_dir(repo_root)
    pages: dict[str, dict[str, Any]] = {}
    for raw_id in page_ids:
        page_id = normalize_page_id(raw_id)
        cache_path = cache_dir / f"{page_id}.md"
        if not cache_path.is_file():
            continue
        pages[page_id] = {
            "markdown": cache_path.read_text(encoding="utf-8"),
            "source_url": None,
        }
    return pages


def _load_payload_pages(payload_path: Path) -> dict[str, dict[str, Any]]:
    text = payload_path.read_text(encoding="utf-8")
    payload = json.loads(text)
    entries = payload.get("pages")
    if not isinstance(entries, list):
        raise NotionLiveError("live payload must contain a pages array")
    pages: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        page_id = normalize_page_id(str(entry.get("page_id") or ""))
        markdown = str(entry.get("markdown") or "")
        if not markdown.strip():
            raise NotionLiveError(f"empty markdown for page {page_id}")
        pages[page_id] = {
            "markdown": markdown,
            "source_url": entry.get("source_url"),
            "title": entry.get("title"),
        }
    return pages


def write_notion_live_cache(repo_root: Path, page_id: str, markdown: str) -> Path:
    """Persist MCP-fetched markdown for later cache-source ingest."""
    norm = normalize_page_id(page_id)
    cache_dir = notion_live_cache_dir(repo_root)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{norm}.md"
    path.write_text(markdown, encoding="utf-8")
    return path


def ingest_notion_live_pages(
    repo_root: Path,
    *,
    source: str = "cache",
    page_ids: list[str] | None = None,
    allowlist_path: Path | None = None,
    payload_path: Path | None = None,
    fetch_page: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """Ingest allowlisted Notion pages from fixtures, cache, live payload, or fetcher."""
    repo_root = Path(repo_root)
    ensure_store_layout(repo_root)
    notion_live_cache_dir(repo_root).mkdir(parents=True, exist_ok=True)

    allowlist = load_allowlist(repo_root, allowlist_path=allowlist_path)
    targets = [normalize_page_id(pid) for pid in (page_ids or allowlist)]
    for pid in targets:
        assert_allowlisted(pid, allowlist)

    source_key = source.strip().lower()
    if source_key == "fixtures":
        pages = _load_fixture_pages(repo_root)
    elif source_key == "cache":
        pages = _load_cache_pages(repo_root, targets)
    elif source_key == "live":
        if payload_path is not None:
            pages = _load_payload_pages(payload_path)
        elif fetch_page is not None:
            pages = {
                pid: {"markdown": fetch_page(pid), "source_url": None}
                for pid in targets
            }
        else:
            raise NotionLiveError("live source requires --payload or an injectable fetcher")
    else:
        raise NotionLiveError(f"unsupported source: {source!r}")

    written: list[dict] = []
    sources: list[str] = []
    missing: list[str] = []
    for pid in targets:
        page = pages.get(pid)
        if page is None:
            missing.append(pid)
            continue
        markdown = str(page.get("markdown") or "")
        if not markdown.strip():
            missing.append(pid)
            continue
        rel = f"{NOTION_LIVE_CACHE_DIR}/{pid}.md"
        item = item_from_notion_live(
            markdown,
            rel,
            page_id=pid,
            source_url=page.get("source_url"),
        )
        write_knowledge_item(repo_root, item)
        written.append(item)
        sources.append(rel)

    if not written:
        raise NotionLiveError(
            f"no pages ingested; missing or empty: {', '.join(missing) or 'all targets'}"
        )

    write_index(repo_root)
    batch_id = f"ingest-{uuid4().hex[:12]}"
    audit = {
        "batch_id": batch_id,
        "kind": "notion-mcp-live-ingest",
        "source": source_key,
        "sources": sources,
        "item_count": len(written),
        "item_ids": [str(i["item_id"]) for i in written],
        "missing_page_ids": missing,
        "ingested_at": _utc_now(),
    }
    log_dir = ingest_log_dir(repo_root)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{batch_id}.json"
    with log_path.open("w", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {"audit": audit, "audit_path": str(log_path), "items": written, "missing": missing}
