#!/usr/bin/env bash
# apply-routing-proposal.sh — Captain-flagged bounded Level 3 weight apply.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROPOSAL=""
REPO_ROOT="$ROOT"
BUDGET=""
SKIP_EVAL_GATE="false"

usage() {
  cat <<'USAGE'
Usage: apply-routing-proposal.sh --proposal PATH [--budget PATH] [--repo-root PATH]

Applies matcher_weight_suggestions only when the proposal has captain_approved=true.
Respects autonomy budget weight-apply limits. Never mutates Skills or agents.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --proposal) PROPOSAL="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --budget) BUDGET="$2"; shift 2 ;;
    --skip-eval-gate) SKIP_EVAL_GATE="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$PROPOSAL" ]]; then
  echo "error: --proposal is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$PROPOSAL" "$BUDGET" "$SKIP_EVAL_GATE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.routing.apply import ApplyError, apply_routing_proposal

repo = Path(sys.argv[1]).resolve()
proposal = Path(sys.argv[2]).resolve()
budget_arg = sys.argv[3].strip()
budget = Path(budget_arg).resolve() if budget_arg else None
skip = sys.argv[4].strip().lower() in ("1", "true", "yes")
try:
    result = apply_routing_proposal(
        repo,
        proposal,
        budget_path=budget,
        run_eval_gate=not skip,
    )
except ApplyError as exc:
    raise SystemExit(f"error: {exc}") from exc
print(json.dumps(result, indent=2, default=str))
PY
