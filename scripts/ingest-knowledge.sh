#!/usr/bin/env bash
# ingest-knowledge.sh — Explicit CLI ingestion into .agent/knowledge/ (M5+).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATHS=""
FROM_STORE=""
REBUILD_VECTOR=0
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: ingest-knowledge.sh [--paths file1[,file2...]] [--from-store experience,evaluations,routing,runs,decisions,procedures,notion,notebooklm] [--rebuild-vector]

Explicit CLI only — never auto-runs on workstream close.
Rebuilds keyword index after ingest. Use --rebuild-vector to also rebuild vector-index.json.
Auto-ingests ADR headings from DECISIONS.md.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --paths) PATHS="$2"; shift 2 ;;
    --from-store) FROM_STORE="$2"; shift 2 ;;
    --rebuild-vector) REBUILD_VECTOR=1; shift ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$PATHS" && -z "$FROM_STORE" ]]; then
  echo "error: --paths or --from-store is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$PATHS" "$FROM_STORE" "$REBUILD_VECTOR" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.knowledge.ingest import IngestError, ingest_path, ingest_store_roots
from orchestrator.knowledge.index import write_index
from orchestrator.knowledge.vector_index import write_vector_index

repo = Path(sys.argv[1]).resolve()
paths_arg = sys.argv[2].strip()
store_arg = sys.argv[3].strip()
rebuild_vector = sys.argv[4].strip() == "1"
written = []
if store_arg:
    result = ingest_store_roots(repo, roots=[r.strip() for r in store_arg.split(",") if r.strip()])
    if rebuild_vector:
        write_vector_index(repo)
        result["vector_index_rebuilt"] = True
    print(json.dumps(result, indent=2, default=str))
    raise SystemExit(0)
for raw in paths_arg.split(","):
    raw = raw.strip()
    if not raw:
        continue
    path = Path(raw).resolve()
    try:
        written.extend(ingest_path(repo, path))
    except IngestError as exc:
        raise SystemExit(f"error: {exc}") from exc
write_index(repo)
payload = {"items": [i["item_id"] for i in written], "count": len(written)}
if rebuild_vector:
    write_vector_index(repo)
    payload["vector_index_rebuilt"] = True
print(json.dumps(payload, indent=2))
PY
