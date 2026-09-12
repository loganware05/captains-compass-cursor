#!/usr/bin/env bash
# run-code-review.sh — Hermetic NorthStar Code Reviewer CLI (M27).
# Evidence-only: writes .agent/evidence/code-review/<run-id>/ — never posts GitHub reviews.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT=""
BASE_REF=""
HEAD_REF="HEAD"
DIFF_FILE=""
CANDIDATES=""
PLAN_PATH=""
PLAN_ID="m27-northstar-code-reviewer"
RUN_ID=""
CHANGED=""

usage() {
  cat <<'USAGE'
Usage: run-code-review.sh --repo-root PATH [options]

Options:
  --repo-root PATH       Repository to review (required)
  --base REF             Git base ref (uses git diff base...head)
  --head REF             Git head ref (default HEAD)
  --diff-file PATH       Use a unified diff file instead of git
  --candidates PATH      Fixture candidates JSON (hermetic CI)
  --plan PATH            IMPLEMENTATION_PLAN.md (intent)
  --plan-id ID           Plan id recorded in report
  --run-id ID            Stable run id (default: generated)
  --changed PATHS        Comma-separated changed paths override
  -h, --help             Show help

Never posts GitHub reviews. Never invokes a model in the default path.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --base) BASE_REF="$2"; shift 2 ;;
    --head) HEAD_REF="$2"; shift 2 ;;
    --diff-file) DIFF_FILE="$2"; shift 2 ;;
    --candidates) CANDIDATES="$2"; shift 2 ;;
    --plan) PLAN_PATH="$2"; shift 2 ;;
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --run-id) RUN_ID="$2"; shift 2 ;;
    --changed) CHANGED="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$REPO_ROOT" ]]; then
  echo "error: --repo-root is required" >&2
  usage >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$BASE_REF" "$HEAD_REF" "$DIFF_FILE" "$CANDIDATES" "$PLAN_PATH" "$PLAN_ID" "$RUN_ID" "$CHANGED" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.review.pipeline import ReviewError, run_code_review

repo = Path(sys.argv[1]).resolve()
base_ref = sys.argv[2]
head_ref = sys.argv[3] or "HEAD"
diff_file = sys.argv[4]
candidates = sys.argv[5]
plan_path = sys.argv[6]
plan_id = sys.argv[7]
run_id = sys.argv[8]
changed = sys.argv[9]

kwargs = {
    "repo_root": repo,
    "base_ref": base_ref,
    "head_ref": head_ref,
    "plan_id": plan_id,
    "hermetic": True,
}
if diff_file:
    kwargs["diff_file"] = Path(diff_file)
if candidates:
    kwargs["candidates_path"] = Path(candidates)
if plan_path:
    kwargs["plan_path"] = Path(plan_path)
if run_id:
    kwargs["run_id"] = run_id
if changed:
    kwargs["changed_paths"] = [p.strip() for p in changed.split(",") if p.strip()]

try:
    result = run_code_review(**kwargs)
except ReviewError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

summary = result["report"]["summary"]
print(json.dumps({
    "run_id": result["run_id"],
    "report_path": result["report_path"],
    "summary": summary,
    "github_review_posted": result["report"]["provenance"].get("github_review_posted", False),
}, indent=2))
PY
