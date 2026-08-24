#!/usr/bin/env bash
# query-technology-intelligence.sh — Read-only TI candidate discovery (explicit opt-in).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUERY=""
TOP=10
PROVIDER="${COMPASS_TI_PROVIDER:-stub}"

usage() {
  cat <<'USAGE'
Usage: query-technology-intelligence.sh --query TEXT [--top N] [--provider stub|file|github-stars]

Read-only Technology Intelligence discovery. Does not install or execute external repos.
Default provider is stub; set COMPASS_TI_PROVIDER=github-stars for live starred repos (gh auth required).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --query) QUERY="$2"; shift 2 ;;
    --top) TOP="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "error: --query is required" >&2
  exit 1
fi

export COMPASS_TI_PROVIDER="$PROVIDER"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$QUERY" "$TOP" <<'PY'
import json
import sys

from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider

query = sys.argv[1]
top_n = int(sys.argv[2])
provider = select_ti_provider()
candidates = provider.discover_candidates(query, {})
if top_n > 0:
    candidates = candidates[:top_n]
payload = {
    "query": query,
    "provider": __import__("os").environ.get("COMPASS_TI_PROVIDER", "stub"),
    "candidates": [item.to_dict() for item in candidates],
}
print(json.dumps(payload, indent=2))
PY
