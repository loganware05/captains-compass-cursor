#!/usr/bin/env bash
# run-xrv-eer.sh — Validate Experience Evidence Records (XRV).
#
# Requires COMPASS_XRV_EER_ENABLED=1.
# Never grants authority; never auto-closes issues.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD="validate"
EER_PATH=""

usage() {
  cat <<'USAGE'
Usage:
  run-xrv-eer.sh validate [--path PATH] [--repo-root PATH]
  run-xrv-eer.sh drift [--repo-root PATH]

validate: schema-check an Experience Evidence Record JSON file
  (default path: .agent/evidence/xrv/eer-i6-cross-provider-fixture.json)
  Requires COMPASS_XRV_EER_ENABLED=1.

drift: check VERSION ↔ README current-version consistency (no gate).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    validate|drift)
      CMD="$1"
      shift
      ;;
    --path)
      EER_PATH="$2"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
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

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

if [[ "$CMD" == "validate" ]]; then
  if [[ "${COMPASS_XRV_EER_ENABLED:-}" != "1" && \
      "${COMPASS_XRV_EER_ENABLED:-}" != "true" && \
      "${COMPASS_XRV_EER_ENABLED:-}" != "yes" && \
      "${COMPASS_XRV_EER_ENABLED:-}" != "on" ]]; then
    echo "error: XRV EER validation disabled — set COMPASS_XRV_EER_ENABLED=1" >&2
    exit 2
  fi
  if [[ -z "$EER_PATH" ]]; then
    EER_PATH="$REPO_ROOT/.agent/evidence/xrv/eer-i6-cross-provider-fixture.json"
  fi
fi

python3 - "$CMD" "$REPO_ROOT" "$EER_PATH" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.xrv.eer import validate_eer_path
from orchestrator.xrv.release_drift import check_release_document_drift

cmd, repo_root, eer_path = sys.argv[1:4]
root = Path(repo_root)

try:
    if cmd == "drift":
        result = check_release_document_drift(root)
        print(json.dumps(result, indent=2, sort_keys=True))
        sys.exit(0 if result.get("ok") else 1)
    if cmd == "validate":
        result = validate_eer_path(root, Path(eer_path), require_gate=True)
        print(json.dumps(result, indent=2, sort_keys=True))
        sys.exit(0 if result.get("status") == "ok" else 1)
    print(f"error: unknown command {cmd}", file=sys.stderr)
    sys.exit(2)
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
except Exception as exc:  # noqa: BLE001
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)
PY
