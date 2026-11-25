#!/usr/bin/env bash
# run-xrv-live-local.sh — Local ops smoke (doctor + reconstruct) against tip SHA.
# Requires COMPASS_XRV_EER_ENABLED=1. Never sets live_deploy=true. Never grants authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
TIP_SHA=""
SMOKE_ID=""
SKIP_DOCTOR=0

usage() {
  cat <<'USAGE'
Usage:
  run-xrv-live-local.sh [--repo-root PATH] [--tip-sha SHA] [--smoke-id ID] [--skip-doctor]

Requires COMPASS_XRV_EER_ENABLED=1.
Writes evidence under .agent/evidence/xrv-ops-live-local/<smoke-id>/.
live_deploy is always false (production deploy out of scope).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --tip-sha) TIP_SHA="$2"; shift 2 ;;
    --smoke-id) SMOKE_ID="$2"; shift 2 ;;
    --skip-doctor) SKIP_DOCTOR=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "${COMPASS_XRV_EER_ENABLED:-}" != "1" && \
      "${COMPASS_XRV_EER_ENABLED:-}" != "true" && \
      "${COMPASS_XRV_EER_ENABLED:-}" != "yes" && \
      "${COMPASS_XRV_EER_ENABLED:-}" != "on" ]]; then
  echo "error: XRV EER validation disabled — set COMPASS_XRV_EER_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$REPO_ROOT" "$TIP_SHA" "$SMOKE_ID" "$SKIP_DOCTOR" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.xrv.live_local import LiveLocalError, run_live_local_smoke

root = Path(sys.argv[1])
tip = sys.argv[2] or None
smoke = sys.argv[3] or None
skip_doctor = sys.argv[4] == "1"

try:
    result = run_live_local_smoke(
        root,
        require_gate=True,
        tip_sha=tip,
        run_doctor=not skip_doctor,
        smoke_id=smoke,
    )
except LiveLocalError as exc:
    print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
    raise SystemExit(1)
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(2)

print(json.dumps({"ok": True, **result}, indent=2, sort_keys=True))
PY
