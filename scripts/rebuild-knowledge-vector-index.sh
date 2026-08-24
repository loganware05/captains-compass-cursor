#!/usr/bin/env bash
# rebuild-knowledge-vector-index.sh — Explicit TF-IDF vector index rebuild (M6).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: rebuild-knowledge-vector-index.sh [--repo-root PATH]

Rebuild .agent/knowledge/vector-index.json from knowledge items.
Explicit CLI only — never auto-runs on workstream close.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.knowledge.vector_index import build_vector_index, write_vector_index

repo = Path(sys.argv[1]).resolve()
path = write_vector_index(repo)
index = build_vector_index(repo)
print(json.dumps({"vector_index": str(path.relative_to(repo)), "item_count": index["item_count"]}, indent=2))
PY
