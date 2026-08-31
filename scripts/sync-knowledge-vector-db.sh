#!/usr/bin/env bash
# sync-knowledge-vector-db.sh — Explicit hosted pgvector upsert for knowledge items (M13).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: sync-knowledge-vector-db.sh [--repo-root PATH]

Upsert knowledge item embeddings into the hosted pgvector store.
Requires COMPASS_VECTOR_PROVIDER=pgvector|mock and an embedding provider
(COMPASS_EMBEDDING_PROVIDER=fixture or openai-compatible).

Env:
  COMPASS_VECTOR_DATABASE_URL   Neon/Postgres DSN (pgvector provider)
  COMPASS_VECTOR_NAMESPACE      Namespace within the shared index (default: repo dir name)
  COMPASS_EMBEDDING_PROVIDER    fixture | openai-compatible

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

from orchestrator.knowledge.adapters.pgvector import HostedVectorError, sync_knowledge_vectors

repo = Path(sys.argv[1]).resolve()
try:
    report = sync_knowledge_vectors(repo)
except HostedVectorError as exc:
    print(json.dumps({"error": str(exc)}, indent=2))
    raise SystemExit(1) from exc
print(json.dumps(report, indent=2))
PY
