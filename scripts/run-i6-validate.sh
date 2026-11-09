#!/usr/bin/env bash
# run-i6-validate.sh — Hermetic I1–I5 cross-provider validation (I6).
#
# Requires COMPASS_I6_VALIDATE_ENABLED=1.
# Never grants authority; no live network.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD="run"
NO_WRITE="0"

usage() {
  cat <<'USAGE'
Usage:
  run-i6-validate.sh run [--no-write] [--repo-root PATH]

Requires COMPASS_I6_VALIDATE_ENABLED=1.
Hermetic fail-closed + fixture probes for I1–I5; writes scorecard evidence.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    run)
      CMD="$1"
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

if [[ "${COMPASS_I6_VALIDATE_ENABLED:-}" != "1" && \
      "${COMPASS_I6_VALIDATE_ENABLED:-}" != "true" && \
      "${COMPASS_I6_VALIDATE_ENABLED:-}" != "yes" && \
      "${COMPASS_I6_VALIDATE_ENABLED:-}" != "on" ]]; then
  echo "error: i6 validation disabled — set COMPASS_I6_VALIDATE_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$CMD" "$REPO_ROOT" "$NO_WRITE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.integrations.i6 import service

cmd, repo_root, no_write = sys.argv[1:4]
root = Path(repo_root)
write = no_write not in {"1", "true", "yes", "on"}

try:
    if cmd != "run":
        print(f"error: unknown command {cmd}", file=sys.stderr)
        sys.exit(2)
    result = service.run(root, write_evidence=write)
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
except Exception as exc:  # noqa: BLE001
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
sys.exit(0 if result.get("status") == "ok" else 1)
PY
