#!/usr/bin/env bash
# run-rea.sh — Cognitive Core governed REA deep analysis (C6).
#
# Requires COMPASS_REA_ENABLED=1.
# Default is hermetic fixture mode. Live requires --allow-live and a complete
# permission checklist. Never grants authority or presents speculation as fact.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
TARGET=""
QUESTION=""
MODE="native"
ALLOW_LIVE="0"
FIXTURE=""
TARGET_AUTHORIZED="0"
LICENSE_REVIEWED="0"
EXECUTION_PERMITTED="0"
SOURCE_DOCS_INSUFFICIENT="0"
ISOLATION_ACK="0"

usage() {
  cat <<'USAGE'
Usage:
  run-rea.sh investigate --target PATH_OR_URL --question TEXT
                 [--mode native|js-electron|dotnet|browser|android|network-capture]
                 [--allow-live]
                 [--fixture PATH]
                 [--target-authorized] [--license-reviewed]
                 [--execution-permitted] [--source-docs-insufficient]
                 [--isolation-acknowledged]
                 [--repo-root PATH]

Requires COMPASS_REA_ENABLED=1.
Default: hermetic fixture. Live needs --allow-live + complete checklist.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    investigate)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
      shift 2
      ;;
    --question)
      QUESTION="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --fixture)
      FIXTURE="$2"
      shift 2
      ;;
    --allow-live)
      ALLOW_LIVE="1"
      shift
      ;;
    --target-authorized)
      TARGET_AUTHORIZED="1"
      shift
      ;;
    --license-reviewed)
      LICENSE_REVIEWED="1"
      shift
      ;;
    --execution-permitted)
      EXECUTION_PERMITTED="1"
      shift
      ;;
    --source-docs-insufficient)
      SOURCE_DOCS_INSUFFICIENT="1"
      shift
      ;;
    --isolation-acknowledged)
      ISOLATION_ACK="1"
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

if [[ "$CMD" == "investigate" ]]; then
  if [[ -z "$TARGET" || -z "$QUESTION" ]]; then
    echo "error: --target and --question are required" >&2
    usage >&2
    exit 2
  fi
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$TARGET" "$QUESTION" "$MODE" \
  "$ALLOW_LIVE" "$FIXTURE" \
  "$TARGET_AUTHORIZED" "$LICENSE_REVIEWED" "$EXECUTION_PERMITTED" \
  "$SOURCE_DOCS_INSUFFICIENT" "$ISOLATION_ACK" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
target = sys.argv[4]
question = sys.argv[5]
mode = sys.argv[6]
allow_live = sys.argv[7] == "1"
fixture = sys.argv[8]
checklist = {
    "target_authorized": sys.argv[9] == "1",
    "license_reviewed": sys.argv[10] == "1",
    "execution_permitted": sys.argv[11] == "1",
    "source_docs_insufficient": sys.argv[12] == "1",
    "isolation_acknowledged": sys.argv[13] == "1",
}

sys.path.insert(0, str(control_root))

from orchestrator.rea.enabled import rea_enabled
from orchestrator.rea.service import ReaServiceError, investigate

if not rea_enabled():
    print(
        "error: COMPASS_REA_ENABLED is unset/off — "
        "set COMPASS_REA_ENABLED=1 to run northstar rea",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "investigate":
        result = investigate(
            repo_root,
            target=target,
            question=question,
            mode=mode,
            allow_live=allow_live,
            checklist=checklist,
            fixture_path=Path(fixture) if fixture else None,
        )
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (ReaServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
PY
