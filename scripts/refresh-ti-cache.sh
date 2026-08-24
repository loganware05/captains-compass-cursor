#!/usr/bin/env bash
# refresh-ti-cache.sh — Explicit refresh of offline GitHub Stars TI cache (M8).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
LIMIT=100

usage() {
  cat <<'USAGE'
Usage: refresh-ti-cache.sh [--repo-root PATH] [--limit N]

Fetch starred repositories via authenticated gh and write
.agent/intelligence/ti-cache/starred-repos.json (explicit CLI only).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$LIMIT" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.providers.technology_intelligence.ti_cache import refresh_ti_cache

repo = Path(sys.argv[1]).resolve()
limit = int(sys.argv[2])
path = refresh_ti_cache(repo, limit=limit)
payload = json.loads(path.read_text(encoding="utf-8"))
print(json.dumps({"cache_path": str(path), "record_count": payload.get("record_count", 0), "refreshed_at": payload.get("refreshed_at")}, indent=2))
PY
