#!/usr/bin/env bash
# run-northstar-routine.sh — Fixture-safe NorthStar connected routine
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: run-northstar-routine.sh [options]

Runs the NorthStar connected routine against recorded/fixture adapters.
Never sends live Slack/Linear/GitHub/Cursor traffic from this script.

Options:
  --repo <path>           Target repo root (default: cwd)
  --provider <name>       slack|linear|github|cursor (default: slack)
  --event <json-file>     Raw event fixture (required unless --demo)
  --demo                  Use a built-in @NorthStar Slack objective fixture
  --plan-id <id>          Plan ID (default: m21-northstar-connected-operations)
  --approve               Record canonical GitHub Captain approval + dispatch
  --advance-to-review     After approve, drive fixture run to REVIEW_READY
  --run-id <id>           Stable run id (optional)
  -h, --help              Show help
USAGE
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="."
PROVIDER="slack"
EVENT=""
DEMO=0
PLAN_ID="m21-northstar-connected-operations"
APPROVE=0
ADVANCE=0
RUN_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --event) EVENT="$2"; shift 2 ;;
    --demo) DEMO=1; shift ;;
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --approve) APPROVE=1; shift ;;
    --advance-to-review) ADVANCE=1; shift ;;
    --run-id) RUN_ID="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

REPO="$(cd "$REPO" && pwd)"

PYTHONPATH="$ROOT" python3 - "$REPO" "$PROVIDER" "$EVENT" "$DEMO" "$PLAN_ID" "$APPROVE" "$ADVANCE" "$RUN_ID" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.integrations.routine import run_northstar_routine

repo, provider, event_path, demo, plan_id, approve, advance, run_id = sys.argv[1:9]
demo = demo == "1"
approve = approve == "1"
advance = advance == "1"
run_id = run_id or None

if demo:
    raw = {
        "event_id": "demo-slack-1",
        "ts": "1000.1",
        "thread_ts": "1000.1",
        "channel": "northstar",
        "text": "@NorthStar refresh connected operations docs",
        "mentions": ["NorthStar"],
        "user_id": "U-demo",
        "event_type": "objective",
        "product_name": "Captain's Compass",
    }
    provider = "slack"
elif event_path:
    raw = json.loads(Path(event_path).read_text(encoding="utf-8"))
else:
    print("error: provide --event or --demo", file=sys.stderr)
    sys.exit(2)

report = run_northstar_routine(
    Path(repo),
    raw_event=raw,
    provider=provider,
    plan_id=plan_id,
    approve=approve,
    advance_to_review=advance,
    run_id=run_id,
)
print(json.dumps(report, indent=2))
PY
