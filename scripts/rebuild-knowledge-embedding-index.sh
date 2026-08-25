#!/usr/bin/env bash
# rebuild-knowledge-embedding-index.sh — Explicit dense embedding index rebuild (M11).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: rebuild-knowledge-embedding-index.sh [--repo-root PATH]

Rebuild .agent/knowledge/embedding-index.json using COMPASS_EMBEDDING_PROVIDER
(default for this script: fixture). TF-IDF vector-index.json is unchanged.
Requires COMPASS_EMBEDDING_PROVIDER=fixture (or sets it for this run).
Explicit CLI only — never auto-runs on workstream close. No network.
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
export COMPASS_EMBEDDING_PROVIDER="${COMPASS_EMBEDDING_PROVIDER:-fixture}"
python3 - "$REPO_ROOT" <<'PY'
import json
import os
import sys
from pathlib import Path

from orchestrator.knowledge.adapters.embeddings import select_embedding_provider
from orchestrator.knowledge.embedding_index import build_embedding_index, write_embedding_index

repo = Path(sys.argv[1]).resolve()
provider = select_embedding_provider()
if provider is None:
    print(
        "error: COMPASS_EMBEDDING_PROVIDER must be 'fixture' "
        f"(got {os.environ.get('COMPASS_EMBEDDING_PROVIDER', '')!r})",
        file=sys.stderr,
    )
    sys.exit(1)
path = write_embedding_index(repo, provider=provider)
index = build_embedding_index(repo, provider=provider)
print(
    json.dumps(
        {
            "embedding_index": str(path.relative_to(repo)),
            "backend": index["backend"],
            "dimensions": index["dimensions"],
            "item_count": index["item_count"],
        },
        indent=2,
    )
)
PY
