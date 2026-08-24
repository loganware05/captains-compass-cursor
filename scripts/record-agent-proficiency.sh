#!/usr/bin/env bash
# record-agent-proficiency.sh — Write Captain-gated subagent proficiency metadata.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT_ID=""
CLASSIFICATIONS=""
LEVEL="developing"
SKILLS=""
CAPTAIN_APPROVED="false"
REPO_ROOT="$ROOT"
NOTES=""

usage() {
  cat <<'USAGE'
Usage: record-agent-proficiency.sh --agent-id ID --classifications a,b [options]

Options:
  --level novice|developing|proficient|expert (default: developing)
  --skills LIST              Comma-separated Skills trained
  --captain-approved true|false (default: false — draft until Captain sets true)
  --notes TEXT
  --repo-root PATH
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent-id) AGENT_ID="$2"; shift 2 ;;
    --classifications) CLASSIFICATIONS="$2"; shift 2 ;;
    --level) LEVEL="$2"; shift 2 ;;
    --skills) SKILLS="$2"; shift 2 ;;
    --captain-approved) CAPTAIN_APPROVED="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$AGENT_ID" || -z "$CLASSIFICATIONS" ]]; then
  echo "error: --agent-id and --classifications are required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$AGENT_ID" "$CLASSIFICATIONS" "$LEVEL" "$SKILLS" "$CAPTAIN_APPROVED" "$NOTES" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.agents.proficiency import (
    build_proficiency_record,
    write_proficiency_record,
)

repo = Path(sys.argv[1]).resolve()
agent_id = sys.argv[2]
classifications = [c.strip() for c in sys.argv[3].split(",") if c.strip()]
level = sys.argv[4]
skills = [s.strip() for s in sys.argv[5].split(",") if s.strip()]
captain_approved = sys.argv[6].strip().lower() in ("1", "true", "yes")
notes = sys.argv[7]
record = build_proficiency_record(
    agent_id=agent_id,
    classifications=classifications,
    proficiency_level=level,
    skills_trained=skills,
    captain_approved=captain_approved,
    notes=notes,
)
path = write_proficiency_record(repo, record)
print(json.dumps({"proficiency": str(path), "captain_approved": captain_approved}, indent=2))
PY
