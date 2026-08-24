#!/usr/bin/env bash
# refresh-ti-cache.sh — Explicit refresh of offline GitHub Stars TI cache (M8+).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
LIMIT=100
IF_STALE=""

usage() {
  cat <<'USAGE'
Usage: refresh-ti-cache.sh [--repo-root PATH] [--limit N] [--if-stale HOURS]

Fetch starred repositories via authenticated gh and write
.agent/intelligence/ti-cache/starred-repos.json (explicit CLI only).

Options:
  --if-stale HOURS   Skip network fetch when cache fetched_at is newer than HOURS
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --if-stale) IF_STALE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$LIMIT" "$IF_STALE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.providers.technology_intelligence.ti_cache import (
    cache_fetched_at,
    refresh_ti_cache,
)

repo = Path(sys.argv[1]).resolve()
limit = int(sys.argv[2])
if_stale_raw = sys.argv[3].strip()
if_stale = float(if_stale_raw) if if_stale_raw else None
before = cache_fetched_at(repo)
path = refresh_ti_cache(repo, limit=limit, if_stale_hours=if_stale)
payload = json.loads(path.read_text(encoding="utf-8"))
after = payload.get("fetched_at") or payload.get("refreshed_at")
skipped = if_stale is not None and before is not None and before == after
print(
    json.dumps(
        {
            "cache_path": str(path),
            "record_count": payload.get("record_count", 0),
            "fetched_at": after,
            "skipped_fresh": skipped,
        },
        indent=2,
    )
)
PY
