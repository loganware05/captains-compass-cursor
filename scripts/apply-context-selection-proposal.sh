#!/usr/bin/env bash
# apply-context-selection-proposal.sh — Captain-flagged context slice profile apply (M17).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROPOSAL=""
REPO_ROOT="$ROOT"
BUDGET=""

usage() {
  cat <<'USAGE'
Usage: apply-context-selection-proposal.sh --proposal PATH [--budget PATH] [--repo-root PATH]

Applies context_profile_suggestions only when the proposal has captain_approved=true.
Respects autonomy budget weight-apply limits.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --proposal) PROPOSAL="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --budget) BUDGET="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$PROPOSAL" ]]; then
  echo "error: --proposal is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$PROPOSAL" "$BUDGET" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.planning.context_selection import (
    ContextSelectionError,
    apply_context_selection_proposal,
)

repo = Path(sys.argv[1]).resolve()
proposal = Path(sys.argv[2]).resolve()
budget_arg = sys.argv[3].strip()
budget = Path(budget_arg).resolve() if budget_arg else None
try:
    result = apply_context_selection_proposal(repo, proposal, budget_path=budget)
except ContextSelectionError as exc:
    raise SystemExit(f"error: {exc}") from exc
print(json.dumps(result, indent=2, default=str))
PY
