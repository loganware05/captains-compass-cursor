#!/usr/bin/env bash
# init-pgvector-schema.sh — Print or apply pgvector DDL for Compass knowledge vectors (M13).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIMENSIONS="${COMPASS_VECTOR_DIMENSIONS:-32}"
APPLY=0

usage() {
  cat <<'USAGE'
Usage: init-pgvector-schema.sh [--dimensions N] [--apply]

Print pgvector DDL for compass_knowledge_vectors. With --apply and
COMPASS_VECTOR_DATABASE_URL set, runs the DDL against Neon/Postgres.

Default dimensions follow COMPASS_VECTOR_DIMENSIONS (32 for fixture embeddings).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dimensions) DIMENSIONS="$2"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
SQL="$(python3 - "$DIMENSIONS" <<'PY'
import sys
from orchestrator.knowledge.adapters.pgvector import pgvector_schema_sql

print(pgvector_schema_sql(int(sys.argv[1])))
PY
)"

if [[ "$APPLY" -eq 0 ]]; then
  printf '%s\n' "$SQL"
  exit 0
fi

if [[ -z "${COMPASS_VECTOR_DATABASE_URL:-}" ]]; then
  echo "error: COMPASS_VECTOR_DATABASE_URL is required with --apply" >&2
  exit 1
fi

python3 - "$SQL" <<'PY'
import os
import sys

from orchestrator.knowledge.adapters.pgvector import LivePgvectorBackend

sql = sys.argv[1]
backend = LivePgvectorBackend(os.environ["COMPASS_VECTOR_DATABASE_URL"])
with backend._connect() as conn:
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql)
print("ok: pgvector schema applied")
PY
