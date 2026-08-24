#!/usr/bin/env bash
# ingest-knowledge.sh — Explicit CLI ingestion into .agent/knowledge/ (M5).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATHS=""
FROM_STORE=""
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: ingest-knowledge.sh [--paths file1[,file2...]] [--from-store experience,evaluations,routing,runs,decisions]

Explicit CLI only — never auto-runs on workstream close.
Rebuilds keyword index after ingest. Auto-ingests ADR headings from DECISIONS.md.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --paths) PATHS="$2"; shift 2 ;;
    --from-store) FROM_STORE="$2"; shift 2 ;;
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
python3 - "$REPO_ROOT" "$PATHS" "$FROM_STORE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.knowledge.ingest import IngestError, ingest_path, ingest_store_roots

repo = Path(sys.argv[1]).resolve()
paths_arg = sys.argv[2].strip()
store_arg = sys.argv[3].strip()
written = []
if store_arg:
    roots = [r.strip() for r in store_arg.split(",") if r.strip()]
    result = ingest_store_roots(repo, roots)
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
from orchestrator.knowledge.index import write_index
write_index(repo)
print(json.dumps({"items": [i["item_id"] for i in written], "count": len(written)}, indent=2))
PY
