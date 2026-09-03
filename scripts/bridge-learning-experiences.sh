#!/usr/bin/env bash
# bridge-learning-experiences.sh — Record Experiences from a skill-learning-run (M20).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
RUN_PATH=""
PLAN_ID=""
SOURCE_INSTANCE="control-test"
PROMOTE_PROVEN=0
CANDIDATE=""
SKILL_SLUG=""
EVIDENCE=""
CAPTAIN_APPROVED=0

usage() {
  cat <<'USAGE'
Usage: bridge-learning-experiences.sh --run PATH [options]

Options:
  --repo-root PATH
  --plan-id ID
  --source-instance control-test|control-live|product-import
  --promote-proven --candidate PATH --skill-slug SLUG --evidence PATHS --captain-approved

Writes ExecutionRun + Experience per learning-run result. PROVEN still needs
--captain-approved and the Experience success threshold.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) RUN_PATH="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --source-instance) SOURCE_INSTANCE="$2"; shift 2 ;;
    --promote-proven) PROMOTE_PROVEN=1; shift ;;
    --candidate) CANDIDATE="$2"; shift 2 ;;
    --skill-slug) SKILL_SLUG="$2"; shift 2 ;;
    --evidence) EVIDENCE="$2"; shift 2 ;;
    --captain-approved) CAPTAIN_APPROVED=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$RUN_PATH" ]]; then
  echo "error: --run is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$RUN_PATH" "$PLAN_ID" "$SOURCE_INSTANCE" "$PROMOTE_PROVEN" "$CANDIDATE" "$SKILL_SLUG" "$EVIDENCE" "$CAPTAIN_APPROVED" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.learning.experience_bridge import (
    ExperienceBridgeError,
    bridge_learning_run_to_experiences,
    promote_proven_from_bridge,
)

repo = Path(sys.argv[1]).resolve()
run_path = Path(sys.argv[2]).resolve()
plan_id = sys.argv[3].strip() or None
source_instance = sys.argv[4]
promote = sys.argv[5] == "1"
candidate = sys.argv[6].strip()
skill_slug = sys.argv[7].strip()
evidence_raw = sys.argv[8].strip()
captain = sys.argv[9] == "1"

try:
    result = bridge_learning_run_to_experiences(
        repo,
        run_path,
        source_instance=source_instance,
        plan_id=plan_id,
    )
    if promote:
        if not candidate or not skill_slug:
            raise ExperienceBridgeError("--promote-proven requires --candidate and --skill-slug")
        evidence = [p.strip() for p in evidence_raw.split(",") if p.strip()]
        proven = promote_proven_from_bridge(
            repo,
            candidate_path=Path(candidate),
            skill_slug=skill_slug,
            evidence_paths=evidence or [str(run_path)],
            captain_approved=captain,
        )
        result["proven_staging"] = str(proven)
except ExperienceBridgeError as exc:
    print(json.dumps({"error": str(exc)}, indent=2))
    raise SystemExit(1) from exc
print(json.dumps(result, indent=2))
PY
