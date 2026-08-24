#!/usr/bin/env bash
# propose-procedure-from-knowledge.sh — Staging-only procedure promotion (M5).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ITEM_IDS=""
TITLE=""
REPO_ROOT="$ROOT"
NOTES=""

usage() {
  cat <<'USAGE'
Usage: propose-procedure-from-knowledge.sh --item-ids id1,id2 --title "Procedure name"

Writes proposal + staging playbook only — never .cursor/skills/.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --item-ids) ITEM_IDS="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$ITEM_IDS" || -z "$TITLE" ]]; then
  echo "error: --item-ids and --title are required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$ITEM_IDS" "$TITLE" "$NOTES" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.knowledge.promote import (
    ProcedurePromotionError,
    build_procedure_proposal,
    select_items_by_ids,
    write_procedure_proposal,
)

repo = Path(sys.argv[1]).resolve()
ids = [i.strip() for i in sys.argv[2].split(",") if i.strip()]
title = sys.argv[3]
notes = sys.argv[4]
try:
    items = select_items_by_ids(repo, ids)
    proposal = build_procedure_proposal(items, procedure_title=title, notes=notes)
    path = write_procedure_proposal(repo, proposal, items)
except ProcedurePromotionError as exc:
    raise SystemExit(f"error: {exc}") from exc
written = json.loads(path.read_text(encoding="utf-8"))
print(
    json.dumps(
        {
            "proposal": str(path),
            "landing_mode": "staging_and_pr_only",
            "staging_paths": written.get("staging_paths"),
        },
        indent=2,
    )
)
PY
