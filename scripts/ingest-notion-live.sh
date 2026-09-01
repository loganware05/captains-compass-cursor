#!/usr/bin/env bash
# ingest-notion-live.sh — Allowlist-gated Notion MCP live knowledge ingest (M15).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
SOURCE="cache"
PAYLOAD=""
PAGE_IDS=""

usage() {
  cat <<'USAGE'
Usage: ingest-notion-live.sh [--repo-root PATH] [--source cache|fixtures|live] [--payload FILE] [--page-ids id1,id2]

Ingest allowlisted Notion pages into .agent/knowledge/ with provenance export_mode: mcp_live.

Sources:
  cache      Read markdown from .agent/knowledge/external/notion-live/<page-id>.md (default)
  fixtures   Use tests/fixtures/knowledge/external/notion-live/pages.json (offline/CI)
  live       Read MCP payload JSON from --payload (Captain local after Notion MCP fetch)

Allowlist: .agent/knowledge/notion-allowlist.txt (one page ID or URL per line)

Explicit CLI only — never auto-runs on workstream close.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    --payload) PAYLOAD="$2"; shift 2 ;;
    --page-ids) PAGE_IDS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ "$SOURCE" == "live" && -z "$PAYLOAD" ]]; then
  echo "error: --source live requires --payload" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$SOURCE" "$PAYLOAD" "$PAGE_IDS" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.knowledge.notion_live import NotionLiveError, ingest_notion_live_pages

repo = Path(sys.argv[1]).resolve()
source = sys.argv[2].strip().lower() or "cache"
payload = sys.argv[3].strip()
page_ids_raw = sys.argv[4].strip()
page_ids = [p.strip() for p in page_ids_raw.split(",") if p.strip()] or None
payload_path = Path(payload).resolve() if payload else None

try:
    result = ingest_notion_live_pages(
        repo,
        source=source,
        page_ids=page_ids,
        payload_path=payload_path,
    )
except NotionLiveError as exc:
    print(json.dumps({"error": str(exc)}, indent=2))
    raise SystemExit(1) from exc

print(json.dumps({
    "item_ids": [i["item_id"] for i in result["items"]],
    "count": len(result["items"]),
    "missing": result.get("missing") or [],
    "audit_path": result.get("audit_path"),
}, indent=2))
PY
