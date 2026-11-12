#!/usr/bin/env bash
# run-xrv-readiness.sh — Hermetic eight-pillar readiness assessor (XRV W2).
#
# Requires COMPASS_XRV_READINESS_ENABLED=1.
# Never invents scores; never grants authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
NO_WRITE="0"

usage() {
  cat <<'USAGE'
Usage:
  run-xrv-readiness.sh run [--no-write] [--repo-root PATH]

Requires COMPASS_XRV_READINESS_ENABLED=1.
Hermetic path probes for eight pillars + NorthStar effectiveness signals.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    run)
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --no-write)
      NO_WRITE="1"
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

if [[ "${COMPASS_XRV_READINESS_ENABLED:-}" != "1" && \
      "${COMPASS_XRV_READINESS_ENABLED:-}" != "true" && \
      "${COMPASS_XRV_READINESS_ENABLED:-}" != "yes" && \
      "${COMPASS_XRV_READINESS_ENABLED:-}" != "on" ]]; then
  echo "error: XRV readiness disabled — set COMPASS_XRV_READINESS_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$REPO_ROOT" "$NO_WRITE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.xrv.readiness import assess_readiness

repo_root = Path(sys.argv[1])
write = sys.argv[2] not in {"1", "true", "yes", "on"}

try:
    result = assess_readiness(repo_root, require_gate=True, write_evidence=write)
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
except Exception as exc:  # noqa: BLE001
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
sys.exit(0 if result.get("status") == "ok" else 1)
PY
