#!/usr/bin/env bash
# run-plan-waves.sh — Multi-wave ledger + continue-after-merge (#274).
#
# Never auto-merges; never forges IMPLEMENTATION_PLAN APPROVED.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
WAVES_CMD=""
PLAN_ID=""
FROM_PATH=""
PR_URL=""
FORCE=0
PAUSE=0

usage() {
  cat <<'USAGE'
Usage:
  run-plan-waves.sh waves init --plan-id ID [--from PATH] [--force] [--pause-between-waves]
       [--repo-root PATH]
  run-plan-waves.sh waves status --plan-id ID [--repo-root PATH]
  run-plan-waves.sh waves advance --plan-id ID --pr URL [--repo-root PATH]
  run-plan-waves.sh continue-after-merge --plan-id ID --pr URL [--from PATH]
       [--repo-root PATH]

northstar aliases:
  northstar plan waves init|status|advance …
  northstar plan continue-after-merge …

Never auto-merges. Never sets plan status to APPROVED.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    waves)
      CMD="waves"
      shift
      if [[ $# -lt 1 ]]; then
        echo "error: waves requires init|status|advance" >&2
        usage >&2
        exit 2
      fi
      WAVES_CMD="$1"
      shift
      ;;
    continue-after-merge)
      CMD="continue-after-merge"
      shift
      ;;
    --plan-id)
      PLAN_ID="$2"
      shift 2
      ;;
    --from)
      FROM_PATH="$2"
      shift 2
      ;;
    --pr)
      PR_URL="$2"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --pause-between-waves)
      PAUSE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$CMD" ]]; then
  usage >&2
  exit 2
fi

if [[ -z "$PLAN_ID" ]]; then
  echo "error: --plan-id is required" >&2
  usage >&2
  exit 2
fi

if [[ "$CMD" == "waves" ]]; then
  case "$WAVES_CMD" in
    init|status|advance) ;;
    *)
      echo "error: unknown waves subcommand: $WAVES_CMD" >&2
      usage >&2
      exit 2
      ;;
  esac
  if [[ "$WAVES_CMD" == "advance" && -z "$PR_URL" ]]; then
    echo "error: --pr is required for waves advance" >&2
    exit 2
  fi
fi

if [[ "$CMD" == "continue-after-merge" && -z "$PR_URL" ]]; then
  echo "error: --pr is required for continue-after-merge" >&2
  exit 2
fi

export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT"

python3 - "$CMD" "${WAVES_CMD:-}" "$REPO_ROOT" "$PLAN_ID" "$FROM_PATH" "$PR_URL" "$FORCE" "$PAUSE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.plan_waves.errors import PlanWavesError
from orchestrator.plan_waves.service import (
    advance_wave,
    continue_after_merge,
    init_wave_ledger,
    wave_ledger_status,
)

cmd, waves_cmd, repo_root, plan_id, from_path, pr_url, force, pause = sys.argv[1:9]
root = Path(repo_root)
from_arg = Path(from_path) if from_path else None

try:
    if cmd == "waves" and waves_cmd == "init":
        result = init_wave_ledger(
            root,
            plan_id=plan_id,
            from_path=from_arg,
            pause_between_waves=pause == "1",
            force=force == "1",
        )
    elif cmd == "waves" and waves_cmd == "status":
        result = wave_ledger_status(root, plan_id)
    elif cmd == "waves" and waves_cmd == "advance":
        result = advance_wave(root, plan_id=plan_id, pr_url=pr_url)
    elif cmd == "continue-after-merge":
        result = continue_after_merge(
            root,
            plan_id=plan_id,
            pr_url=pr_url,
            plan_path=from_arg,
        )
    else:
        print(f"error: unknown command {cmd} {waves_cmd}", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(result, indent=2, sort_keys=True))
    sys.exit(0)
except PlanWavesError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
except Exception as exc:  # noqa: BLE001
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)
PY
