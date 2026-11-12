#!/usr/bin/env bash
# run-xrv-readiness.sh — Hermetic eight-pillar readiness / portfolio (XRV).
#
# Requires COMPASS_XRV_READINESS_ENABLED=1.
# Never invents scores; never grants authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
NO_WRITE="0"
CMD="run"
PROFILE=""
PORTFOLIO_ARGS=()

usage() {
  cat <<'USAGE'
Usage:
  run-xrv-readiness.sh run [--profile control|product] [--no-write] [--repo-root PATH]
  run-xrv-readiness.sh portfolio --repo LABEL=PATH [--repo LABEL=PATH ...] [--no-write]

Requires COMPASS_XRV_READINESS_ENABLED=1.
Imports/schemas always load from the control repo (this script's parent).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    run|portfolio)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --repo)
      PORTFOLIO_ARGS+=("$2")
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

export COMPASS_CONTROL_ROOT="${COMPASS_CONTROL_ROOT:-$ROOT}"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$CMD" "$ROOT" "$REPO_ROOT" "$NO_WRITE" "$PROFILE" "${PORTFOLIO_ARGS[@]+"${PORTFOLIO_ARGS[@]}"}" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.xrv.portfolio import assess_portfolio
from orchestrator.xrv.readiness import assess_readiness

cmd = sys.argv[1]
control_root = Path(sys.argv[2])
repo_root = Path(sys.argv[3])
no_write = sys.argv[4] in {"1", "true", "yes", "on"}
profile = sys.argv[5] or None
portfolio_args = sys.argv[6:]

write = not no_write

try:
    if cmd == "run":
        if profile is not None and profile not in {"control", "product"}:
            print("error: --profile must be control|product", file=sys.stderr)
            sys.exit(2)
        result = assess_readiness(
            repo_root,
            require_gate=True,
            write_evidence=write,
            profile=profile,
            control_root=control_root,
            evidence_root=control_root if repo_root != control_root else None,
        )
    elif cmd == "portfolio":
        if not portfolio_args:
            print("error: portfolio requires one or more --repo LABEL=PATH", file=sys.stderr)
            sys.exit(2)
        entries = []
        for item in portfolio_args:
            if "=" not in item:
                print(f"error: expected LABEL=PATH, got {item!r}", file=sys.stderr)
                sys.exit(2)
            label, path = item.split("=", 1)
            entries.append((label, Path(path), None))
        result = assess_portfolio(
            entries,
            require_gate=True,
            write_evidence=write,
            control_root=control_root,
        )
    else:
        print(f"error: unknown command {cmd}", file=sys.stderr)
        sys.exit(2)
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
except Exception as exc:  # noqa: BLE001
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
sys.exit(0 if result.get("status") == "ok" else 1)
PY
