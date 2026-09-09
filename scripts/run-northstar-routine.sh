#!/usr/bin/env bash
# run-northstar-routine.sh — NorthStar connected routine (fixtures default; optional live)
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: run-northstar-routine.sh [options]

Runs the NorthStar connected routine. Default --mode fixtures never sends live
Slack/Linear/GitHub traffic. Live mode requires secrets + allowlisted sandbox.

Options:
  --repo <path>           Target repo root (default: cwd)
  --provider <name>       slack|linear|github|cursor (default: slack)
  --event <json-file>     Raw event fixture (required unless --demo)
  --demo                  Use a built-in @NorthStar Slack objective fixture
  --plan-id <id>          Plan ID (default: m21-northstar-connected-operations)
  --mode fixtures|live    Default: fixtures (CI-safe)
  --product-repo <slug>   Product repo (must be sandbox allowlist; live default)
  --approve               Fixtures only: record canonical GitHub approval + dispatch
                          (live mode refuses this shortcut — GitHub digest only)
  --advance-to-review     After approve, drive fixture run to REVIEW_READY
  --propose-roles         After REVIEW_READY, propose persistent roles (staging only)
  --surface-routing       After REVIEW_READY, list pending routing proposals (no apply)
  --notion-mode <mode>    fixtures|live — Notion research context (non-authoritative)
  --run-id <id>           Stable run id (optional)
  -h, --help              Show help

Notes:
  Weight apply is intentionally NOT exposed here. Use apply-routing-proposal.sh
  with captain_approved proposals. NorthStar plan approval never applies weights.
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
PROPOSE_ROLES=0
SURFACE_ROUTING=0
NOTION_MODE=""
RUN_ID=""
MODE="fixtures"
PRODUCT_REPO=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --event) EVENT="$2"; shift 2 ;;
    --demo) DEMO=1; shift ;;
    --plan-id) PLAN_ID="$2"; shift 2 ;;
    --approve) APPROVE=1; shift ;;
    --advance-to-review) ADVANCE=1; shift ;;
    --propose-roles) PROPOSE_ROLES=1; shift ;;
    --surface-routing) SURFACE_ROUTING=1; shift ;;
    --notion-mode) NOTION_MODE="$2"; shift 2 ;;
    --run-id) RUN_ID="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --product-repo) PRODUCT_REPO="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

REPO="$(cd "$REPO" && pwd)"

PYTHONPATH="$ROOT" python3 - "$REPO" "$PROVIDER" "$EVENT" "$DEMO" "$PLAN_ID" "$APPROVE" "$ADVANCE" "$RUN_ID" "$PROPOSE_ROLES" "$SURFACE_ROUTING" "$NOTION_MODE" "$MODE" "$PRODUCT_REPO" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.integrations.routine import run_northstar_routine

(
    repo,
    provider,
    event_path,
    demo,
    plan_id,
    approve,
    advance,
    run_id,
    propose_roles,
    surface_routing,
    notion_mode,
    mode,
    product_repo,
) = sys.argv[1:14]
demo = demo == "1"
approve = approve == "1"
advance = advance == "1"
propose_roles = propose_roles == "1"
surface_routing = surface_routing == "1"
run_id = run_id or None
notion_mode = notion_mode or None
product_repo = product_repo or None

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
    propose_roles=propose_roles,
    surface_routing=surface_routing,
    notion_mode=notion_mode,
    mode=mode,
    product_repository=product_repo,
)
print(json.dumps(report, indent=2))
PY
