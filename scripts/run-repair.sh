#!/usr/bin/env bash
# run-repair.sh — Start a hermetic B4 repair run from a verified finding.
# Default: dry-run evidence only. Never auto-merges. Live dispatch requires
# --captain-approve-dispatch AND a wakeable routing decision.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
REPORT=""
FINDING_ID=""
SEVERITY_FLOOR="medium"
TARGET_REPO=""
REGISTRY=""
CLOUD_AGENTS=""
CAPTAIN_DISPATCH=0
PREPARE_PR=0

usage() {
  cat <<'USAGE'
Usage: run-repair.sh --report PATH --finding-id ID [options]

Options:
  --report PATH                 code-review report.json (required)
  --finding-id ID               verified finding id (required)
  --repo-root PATH              Repository root for evidence (default: control repo)
  --severity-floor LEVEL        critical|high|medium|low|info (default: medium)
  --target-repository SLUG      owner/name (default: report.repository or sandbox)
  --registry PATH               Agent registry JSON for routing packet
  --cloud-agents-json PATH      Optional M26 cloud agents snapshot
  --captain-approve-dispatch    Authorize dispatch_authorized=true when routing is ready
  --prepare-pr                  Request draft PR metadata (still never merges)
  -h, --help                    Show help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --report) REPORT="$2"; shift 2 ;;
    --finding-id) FINDING_ID="$2"; shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --severity-floor) SEVERITY_FLOOR="$2"; shift 2 ;;
    --target-repository) TARGET_REPO="$2"; shift 2 ;;
    --registry) REGISTRY="$2"; shift 2 ;;
    --cloud-agents-json) CLOUD_AGENTS="$2"; shift 2 ;;
    --captain-approve-dispatch) CAPTAIN_DISPATCH=1; shift ;;
    --prepare-pr) PREPARE_PR=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$REPORT" || -z "$FINDING_ID" ]]; then
  echo "error: --report and --finding-id are required" >&2
  usage >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REPO_ROOT" "$REPORT" "$FINDING_ID" "$SEVERITY_FLOOR" "$TARGET_REPO" \
  "$REGISTRY" "$CLOUD_AGENTS" "$CAPTAIN_DISPATCH" "$PREPARE_PR" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.repair import RepairError, start_repair

repo = Path(sys.argv[1]).resolve()
report = Path(sys.argv[2]).resolve()
finding_id = sys.argv[3]
floor = sys.argv[4]
target = sys.argv[5]
registry = Path(sys.argv[6]) if sys.argv[6] else None
cloud = Path(sys.argv[7]) if sys.argv[7] else None
captain = sys.argv[8] == "1"
prepare = sys.argv[9] == "1"

try:
    result = start_repair(
        repo_root=repo,
        report_path=report,
        finding_id=finding_id,
        severity_floor=floor,
        target_repository=target,
        registry_path=registry,
        cloud_agents_path=cloud,
        captain_approve_dispatch=captain,
        prepare_pr=prepare,
        dry_run=True,
    )
except RepairError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

print(json.dumps(result, indent=2))
PY
