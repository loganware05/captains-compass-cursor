#!/usr/bin/env bash
# promote-candidate.sh — Advance TI candidate to ANALYZED staging (+ optional Skill draft).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANDIDATE=""
DRAFT_SKILL=""
REPO_ROOT="$ROOT"

usage() {
  cat <<'USAGE'
Usage: promote-candidate.sh --candidate <file.json> [--draft-skill <slug>] [--repo-root PATH]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --candidate) CANDIDATE="$2"; shift 2 ;;
    --draft-skill) DRAFT_SKILL="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$CANDIDATE" ]]; then
  echo "error: --candidate is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$CANDIDATE" "$DRAFT_SKILL" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.promotion.advance import (
    load_candidate_json,
    write_skill_sidecar_draft,
    write_staging_candidate,
)

repo = Path(sys.argv[1]).resolve()
candidate_path = Path(sys.argv[2]).resolve()
draft_skill = sys.argv[3].strip()
candidate = load_candidate_json(candidate_path)
staging = write_staging_candidate(repo, candidate)
result = {"staging_candidate": str(staging)}
if draft_skill:
    draft = write_skill_sidecar_draft(repo, candidate, draft_skill)
    result["skill_draft_capability_yaml"] = str(draft)
print(json.dumps(result, indent=2))
PY
