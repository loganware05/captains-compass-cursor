#!/usr/bin/env bash
# run-behavior-learn.sh — Proposal-only behavior pattern learning (M47).
#
# Requires COMPASS_BEHAVIOR_LEARN_ENABLED=1. Never activates Policies or
# mutates Skills / routing / instructions / authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
PATTERN_ID=""
EXPORT_FORMAT=""
EXPORT_PATH=""

usage() {
  cat <<'USAGE'
Usage:
  run-behavior-learn.sh scan [--repo-root PATH]
  run-behavior-learn.sh list [--repo-root PATH]
  run-behavior-learn.sh show <pattern-id> [--repo-root PATH]
  run-behavior-learn.sh export --format csv [--out PATH] [--repo-root PATH]

Requires COMPASS_BEHAVIOR_LEARN_ENABLED=1.
Proposal-only: never activates Policies or mutates Skills/routing/authority.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    scan|list|show|export)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --format)
      EXPORT_FORMAT="$2"
      shift 2
      ;;
    --out)
      EXPORT_PATH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$PATTERN_ID" && "$CMD" == "show" ]]; then
        PATTERN_ID="$1"
        shift
      else
        echo "error: unknown argument: $1" >&2
        usage >&2
        exit 2
      fi
      ;;
  esac
done

if [[ -z "$CMD" ]]; then
  usage >&2
  exit 2
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$PATTERN_ID" "$EXPORT_FORMAT" "$EXPORT_PATH" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
pattern_id = sys.argv[4]
export_format = sys.argv[5]
export_path = sys.argv[6]

sys.path.insert(0, str(control_root))

from orchestrator.behavior.enabled import behavior_learn_enabled
from orchestrator.behavior.patterns.service import (
    BehaviorLearnServiceError,
    export_patterns_csv,
    list_learned_patterns,
    scan_and_persist,
    show_pattern,
)

if not behavior_learn_enabled():
    print(
        "error: COMPASS_BEHAVIOR_LEARN_ENABLED is unset/off — "
        "set COMPASS_BEHAVIOR_LEARN_ENABLED=1 to run northstar learn",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "scan":
        result = scan_and_persist(repo_root)
    elif cmd == "list":
        result = list_learned_patterns(repo_root)
    elif cmd == "show":
        if not pattern_id:
            print("error: pattern-id required for show", file=sys.stderr)
            sys.exit(2)
        result = show_pattern(repo_root, pattern_id)
    elif cmd == "export":
        if export_format and export_format != "csv":
            print("error: only --format csv is supported", file=sys.stderr)
            sys.exit(2)
        dest = Path(export_path) if export_path else (
            repo_root / ".agent" / "evaluations" / "behavior" / "patterns" / "export.csv"
        )
        path = export_patterns_csv(repo_root, dest)
        result = {"status": "exported", "path": str(path), "canonical_unchanged": True}
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (BehaviorLearnServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True, default=str))
PY
