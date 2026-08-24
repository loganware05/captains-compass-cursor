#!/usr/bin/env bash
# query-knowledge.sh — Keyword, vector, or hybrid search over .agent/knowledge/ (read-only).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUERY=""
KIND=""
TOP=10
MODE="keyword"
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: query-knowledge.sh --query TEXT [--mode keyword|vector|hybrid] [--kind knowledge|decision|procedure|performance|artifact] [--top N]

Read-only knowledge search with provenance. Does not mutate matcher weights.
Default mode is keyword; use hybrid when vector-index.json exists.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --query) QUERY="$2"; shift 2 ;;
    --kind) KIND="$2"; shift 2 ;;
    --top) TOP="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "error: --query is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$QUERY" "$KIND" "$TOP" "$MODE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.knowledge.query import query_knowledge

repo = Path(sys.argv[1]).resolve()
query = sys.argv[2]
kind = sys.argv[3].strip() or None
top_n = int(sys.argv[4])
mode = sys.argv[5].strip() or "keyword"
results = query_knowledge(repo, query, kind=kind, top_n=top_n, mode=mode)
print(json.dumps({"query": query, "mode": mode, "results": results}, indent=2))
PY
