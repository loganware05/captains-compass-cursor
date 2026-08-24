#!/usr/bin/env bash
# propose-persistent-role.sh — Draft persistent-role promotion (staging + PR only).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT_ID=""
REPO_ROOT="$ROOT"
NOTES=""

usage() {
  cat <<'USAGE'
Usage: propose-persistent-role.sh --agent-id ID [--repo-root PATH] [--notes TEXT]

Requires a Captain-approved proficiency record at proficient|expert with enough
Experiences. Writes proposal + staging drafts only — never .cursor/agents/.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent-id) AGENT_ID="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$AGENT_ID" ]]; then
  echo "error: --agent-id is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$AGENT_ID" "$NOTES" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.agents.promote import (
    PromotionProposeError,
    build_persistent_role_proposal,
    load_proficiency_records,
    select_proficiency_for_agent,
    write_persistent_role_proposal,
)

repo = Path(sys.argv[1]).resolve()
agent_id = sys.argv[2]
notes = sys.argv[3]
record = select_proficiency_for_agent(load_proficiency_records(repo), agent_id)
if record is None:
    raise SystemExit(f"error: no proficiency record for agent_id={agent_id!r}")
try:
    proposal = build_persistent_role_proposal(record, notes=notes)
    path = write_persistent_role_proposal(repo, proposal, record)
except PromotionProposeError as exc:
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
