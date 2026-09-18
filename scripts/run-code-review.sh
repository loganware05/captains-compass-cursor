#!/usr/bin/env bash
# run-code-review.sh — Hermetic NorthStar Code Reviewer CLI (M27–M30).
# Default: evidence-only under .agent/evidence/code-review/<run-id>/.
# Opt-in M30: --post-github-draft posts a PENDING draft review for allowlisted repos.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT=""
BASE_REF=""
HEAD_REF="HEAD"
DIFF_FILE=""
CANDIDATES=""
CANDIDATES_MODE="specialists"
PLAN_PATH=""
INTENT_JSON=""
PLAN_ID="m30-github-draft-reviews"
RUN_ID=""
CHANGED=""
POST_GITHUB_DRAFT=0
GITHUB_REPO=""
PULL_NUMBER=""
GITHUB_ALLOWLIST=""
SEVERITY_FLOOR=""
GITHUB_COMMIT=""
BOUNDARY_CHECK=1

usage() {
  cat <<'USAGE'
Usage: run-code-review.sh --repo-root PATH [options]

Options:
  --repo-root PATH         Repository to review (required)
  --base REF               Git base ref (uses git diff base...head)
  --head REF               Git head ref (default HEAD)
  --diff-file PATH         Use a unified diff file instead of git
  --candidates PATH        Fixture candidates JSON (hermetic CI)
  --candidates-mode MODE   specialists|heuristics|specialists+heuristics (default: specialists)
  --plan PATH              IMPLEMENTATION_PLAN.md / INTENT_PACK.md (intent)
  --intent-json PATH       Normalized intent pack JSON (never sets captain_approval)
  --plan-id ID             Plan id recorded in report
  --run-id ID              Stable run id (default: generated)
  --changed PATHS          Comma-separated changed paths override
  --post-github-draft      Opt-in M30: post PENDING draft review (allowlist-gated)
  --github-repo OWNER/NAME GitHub repo slug (required with --post-github-draft)
  --pull-number N          Pull request number (required with --post-github-draft)
  --github-allowlist PATH  Allowlist YAML/JSON (default: .agent/review/github-allowlist.yml)
  --severity-floor LEVEL    critical|high|medium|low|info (default from allowlist)
  --github-commit SHA      Optional commit_id for the draft review
  --boundary-check         M40: cross-boundary verification against inode store (default: on)
  --no-boundary-check      Disable the M40 boundary gate
  -h, --help               Show help

Default path never posts GitHub reviews and never invokes a model.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --base) BASE_REF="$2"; shift 2 ;;
    --head) HEAD_REF="$2"; shift 2 ;;
    --diff-file) DIFF_FILE="$2"; shift 2 ;;
    --candidates) CANDIDATES="$2"; shift 2 ;;
    --candidates-mode) CANDIDATES_MODE="$2"; shift 2 ;;
    --plan) PLAN_PATH="$2"; shift 2 ;;
    --intent-json) INTENT_JSON="$2"; shift 2 ;;
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --run-id) RUN_ID="$2"; shift 2 ;;
    --changed) CHANGED="$2"; shift 2 ;;
    --post-github-draft) POST_GITHUB_DRAFT=1; shift ;;
    --github-repo) GITHUB_REPO="$2"; shift 2 ;;
    --pull-number) PULL_NUMBER="$2"; shift 2 ;;
    --github-allowlist) GITHUB_ALLOWLIST="$2"; shift 2 ;;
    --severity-floor) SEVERITY_FLOOR="$2"; shift 2 ;;
    --github-commit) GITHUB_COMMIT="$2"; shift 2 ;;
    --boundary-check) BOUNDARY_CHECK=1; shift ;;
    --no-boundary-check) BOUNDARY_CHECK=0; shift ;;
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
python3 - "$REPO_ROOT" "$BASE_REF" "$HEAD_REF" "$DIFF_FILE" "$CANDIDATES" "$PLAN_PATH" "$INTENT_JSON" "$PLAN_ID" "$RUN_ID" "$CHANGED" "$CANDIDATES_MODE" "$POST_GITHUB_DRAFT" "$GITHUB_REPO" "$PULL_NUMBER" "$GITHUB_ALLOWLIST" "$SEVERITY_FLOOR" "$GITHUB_COMMIT" "$BOUNDARY_CHECK" <<'PY'
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
intent_json = sys.argv[7]
plan_id = sys.argv[8]
run_id = sys.argv[9]
changed = sys.argv[10]
candidates_mode = sys.argv[11] if len(sys.argv) > 11 else "specialists"
post_github_draft = sys.argv[12] == "1"
github_repo = sys.argv[13]
pull_number_raw = sys.argv[14]
github_allowlist = sys.argv[15]
severity_floor = sys.argv[16]
github_commit = sys.argv[17]
boundary_check = sys.argv[18] == "1" if len(sys.argv) > 18 else True

kwargs = {
    "repo_root": repo,
    "base_ref": base_ref,
    "head_ref": head_ref,
    "plan_id": plan_id,
    "hermetic": True,
    "candidates_mode": candidates_mode or "specialists",
    "post_github_draft": post_github_draft,
    "boundary_check": boundary_check,
}
if diff_file:
    kwargs["diff_file"] = Path(diff_file)
if candidates:
    kwargs["candidates_path"] = Path(candidates)
if plan_path:
    kwargs["plan_path"] = Path(plan_path)
if intent_json:
    kwargs["intent_json"] = Path(intent_json)
if run_id:
    kwargs["run_id"] = run_id
if changed:
    kwargs["changed_paths"] = [p.strip() for p in changed.split(",") if p.strip()]
if github_repo:
    kwargs["github_repo"] = github_repo
if pull_number_raw:
    kwargs["pull_number"] = int(pull_number_raw)
if github_allowlist:
    kwargs["github_allowlist"] = Path(github_allowlist)
if severity_floor:
    kwargs["severity_floor"] = severity_floor
if github_commit:
    kwargs["github_commit_id"] = github_commit

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
    "candidates_source": result["report"]["provenance"].get("candidates_source"),
    "intent_source": (result.get("detection") or {}).get("intent", {}).get("source"),
    "boundary": result.get("boundary"),
    "github_draft": result.get("github_draft"),
}, indent=2))
PY
