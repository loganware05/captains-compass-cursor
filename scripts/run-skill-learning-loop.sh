#!/usr/bin/env bash
# run-skill-learning-loop.sh — Explicit Captain-gated skill learning loop (M19).
# Categorize Stars → staging → fixture harness → drafts / improvement proposals.
# Never auto-installs into .cursor/skills/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
SOURCE="fixtures"
OBJECTIVE="improve agent skills from categorized github stars"
TOP_N=3
CATEGORY=""
THRESHOLD=""
SKIP_CATEGORIZE=0

usage() {
  cat <<'USAGE'
Usage: run-skill-learning-loop.sh [options]

Options:
  --repo-root PATH         Repository root (default: control repo)
  --source fixtures|ti-cache|live
                           Input for categorization (default: fixtures)
  --objective TEXT         Ranking objective (required for meaningful selection)
  --top N                  Max candidates to process (default: 3)
  --category NAME          Optional star_category filter
  --similarity-threshold F Jaccard threshold for existing-Skill matches (default: 0.22)
  --skip-categorize        Reuse existing categorized.json

Explicit CLI only — never auto-runs on hooks/close/CI defaults.
Live Skill install still requires Captain approval (promote-candidate --captain-approved).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    --objective) OBJECTIVE="$2"; shift 2 ;;
    --top) TOP_N="$2"; shift 2 ;;
    --category) CATEGORY="$2"; shift 2 ;;
    --similarity-threshold) THRESHOLD="$2"; shift 2 ;;
    --skip-categorize) SKIP_CATEGORIZE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$SOURCE" "$OBJECTIVE" "$TOP_N" "$CATEGORY" "$THRESHOLD" "$SKIP_CATEGORIZE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.learning.loop import LearningLoopError, run_skill_learning_loop

control = Path(sys.argv[1]).resolve()
repo = Path(sys.argv[2]).resolve()
source = sys.argv[3]
objective = sys.argv[4]
top_n = int(sys.argv[5])
category = sys.argv[6].strip() or None
threshold_raw = sys.argv[7].strip()
skip = sys.argv[8].strip() == "1"
kwargs = {
    "objective": objective,
    "source": source,
    "top_n": top_n,
    "category_filter": category,
    "control_root": control,
    "skip_categorize": skip,
}
if threshold_raw:
    kwargs["similarity_threshold"] = float(threshold_raw)

try:
    report = run_skill_learning_loop(repo, **kwargs)
except LearningLoopError as exc:
    print(json.dumps({"error": str(exc)}, indent=2))
    raise SystemExit(1) from exc
print(json.dumps(report, indent=2))
PY
