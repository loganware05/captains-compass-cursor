#!/usr/bin/env bash
# promote-candidate.sh — Advance TI candidate lifecycle (ceiling: PROVEN_SKILL).
# Stages after SANDBOX_TESTED require --captain-approved.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANDIDATE=""
DRAFT_SKILL=""
TARGET_STAGE="ANALYZED"
EVIDENCE=""
REPO_ROOT="$ROOT"
CAPTAIN_APPROVED=0
SKILL_SLUG=""

usage() {
  cat <<'USAGE'
Usage: promote-candidate.sh --candidate <file.json> [options]

Options:
  --stage STAGE          DISCOVERED…PROVEN_SKILL (default: ANALYZED)
  --evidence PATHS       Comma-separated evidence paths (required for SECURITY_REVIEWED+)
  --captain-approved     Required for APPROVED, AVAILABLE_SKILL, PROVEN_SKILL
  --skill-slug SLUG      Skill slug for AVAILABLE/PROVEN proposals and Experience matching
  --draft-skill SLUG     Also write Skill sidecar draft under staging
  --repo-root PATH       Repository root (default: control repo)

Post-sandbox stages write staging candidates; AVAILABLE_SKILL also writes an
install proposal under .agent/capabilities/candidates/available-proposals/
(never auto-installs into .cursor/skills/).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --candidate) CANDIDATE="$2"; shift 2 ;;
    --draft-skill) DRAFT_SKILL="$2"; shift 2 ;;
    --stage) TARGET_STAGE="$2"; shift 2 ;;
    --evidence) EVIDENCE="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --skill-slug) SKILL_SLUG="$2"; shift 2 ;;
    --captain-approved) CAPTAIN_APPROVED=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$CANDIDATE" ]]; then
  echo "error: --candidate is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$CANDIDATE" "$DRAFT_SKILL" "$TARGET_STAGE" "$EVIDENCE" "$CAPTAIN_APPROVED" "$SKILL_SLUG" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.promotion.advance import (
    load_candidate_json,
    write_available_skill_proposal,
    write_skill_sidecar_draft,
    write_staging_candidate,
)

repo = Path(sys.argv[1]).resolve()
candidate_path = Path(sys.argv[2]).resolve()
draft_skill = sys.argv[3].strip()
target_stage = sys.argv[4].strip() or "ANALYZED"
evidence_raw = sys.argv[5].strip()
captain_approved = sys.argv[6].strip() == "1"
skill_slug = sys.argv[7].strip() or None
evidence = [p.strip() for p in evidence_raw.split(",") if p.strip()] or None
candidate = load_candidate_json(candidate_path)
slug = skill_slug or draft_skill or None
staging = write_staging_candidate(
    repo,
    candidate,
    target_stage=target_stage,
    evidence_paths=evidence,
    captain_approved=captain_approved,
    skill_slug=slug,
)
# Reload staged candidate for proposal writer
staged = load_candidate_json(staging)
result = {
    "staging_candidate": str(staging),
    "lifecycle_stage": target_stage,
    "captain_approved": captain_approved,
}
if draft_skill:
    draft = write_skill_sidecar_draft(repo, staged, draft_skill)
    result["skill_draft_capability_yaml"] = str(draft)
if target_stage in ("AVAILABLE_SKILL",) and slug:
    proposal = write_available_skill_proposal(repo, staged, slug)
    result["available_skill_proposal"] = str(proposal)
print(json.dumps(result, indent=2))
PY
