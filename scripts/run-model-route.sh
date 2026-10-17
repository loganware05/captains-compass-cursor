#!/usr/bin/env bash
# run-model-route.sh — Cognitive Core adaptive model routing (C5).
#
# Requires COMPASS_ROUTE_ENABLED=1.
# Advisory only: never binds Cursor models, auto-spends, or grants authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
OBJECTIVE=""
FIXTURE=""

usage() {
  cat <<'USAGE'
Usage:
  run-model-route.sh route --objective TEXT [--repo-root PATH]
  run-model-route.sh evaluate [--fixture PATH] [--repo-root PATH]

Requires COMPASS_ROUTE_ENABLED=1.
Advisory only — never auto-switches live models or mutates authority.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    route|evaluate)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --objective)
      OBJECTIVE="$2"
      shift 2
      ;;
    --fixture)
      FIXTURE="$2"
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

if [[ -z "$CMD" ]]; then
  usage >&2
  exit 2
fi

if [[ "$CMD" == "route" && -z "$OBJECTIVE" ]]; then
  echo "error: --objective is required for model route" >&2
  usage >&2
  exit 2
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$OBJECTIVE" "$FIXTURE" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
objective = sys.argv[4]
fixture = sys.argv[5]

sys.path.insert(0, str(control_root))

from orchestrator.route.enabled import route_enabled
from orchestrator.route.service import RouteServiceError, model_evaluate, model_route

if not route_enabled():
    print(
        "error: COMPASS_ROUTE_ENABLED is unset/off — "
        "set COMPASS_ROUTE_ENABLED=1 to run northstar model route|evaluate",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "route":
        result = model_route(repo_root, objective)
    elif cmd == "evaluate":
        result = model_evaluate(
            repo_root,
            fixture_path=Path(fixture) if fixture else None,
        )
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (RouteServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
PY
