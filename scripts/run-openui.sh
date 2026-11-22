#!/usr/bin/env bash
# run-openui.sh — Open UI control plane emitters, preview/serve, gated approve/reject.
#
# Requires COMPASS_OPENUI_ENABLED=1 (or --enable-gates).
# Approve requires COMPASS_CAPTAIN_APPROVE=1. Never auto-approves.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
SURFACE=""
FEEDBACK=""
ENABLE_GATES=0
NO_FENCE=0
NO_PERSIST=0
HOST="127.0.0.1"
PORT="8765"
TIMEOUT=""

usage() {
  cat <<'USAGE'
Usage:
  run-openui.sh emit --surface plan|tower|scorecard|closeout [--repo-root PATH]
  run-openui.sh validate --surface SURFACE [--repo-root PATH]
  run-openui.sh preview [--surface SURFACE] [--repo-root PATH]
  run-openui.sh serve [--surface SURFACE] [--host 127.0.0.1] [--port 8765]
                      [--timeout SECONDS] [--repo-root PATH]
  run-openui.sh approve [--repo-root PATH]          # requires COMPASS_CAPTAIN_APPROVE=1
  run-openui.sh reject --feedback TEXT [--repo-root PATH]

Requires COMPASS_OPENUI_ENABLED=1 (or --enable-gates).
preview writes .agent/ui/preview.html from persisted *.openui (emits plan if empty).
serve is localhost-only (127.0.0.1 / localhost).
Fail-closed: invalid OpenUI Lang → error; markdown/CLI remains the fallback.
USAGE
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

CMD="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root|--repo) REPO_ROOT="$2"; shift 2 ;;
    --surface) SURFACE="$2"; shift 2 ;;
    --feedback) FEEDBACK="$2"; shift 2 ;;
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --enable-gates) ENABLE_GATES=1; shift ;;
    --no-fence) NO_FENCE=1; shift ;;
    --no-persist) NO_PERSIST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_OPENUI_ENABLED=1
fi

# emit/validate historically defaulted to plan when --surface omitted.
if [[ -z "$SURFACE" && ( "$CMD" == "emit" || "$CMD" == "validate" ) ]]; then
  SURFACE="plan"
fi

export COMPASS_CONTROL_ROOT="${COMPASS_CONTROL_ROOT:-$ROOT}"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$SURFACE" "$FEEDBACK" "$NO_FENCE" "$NO_PERSIST" "$HOST" "$PORT" "$TIMEOUT" <<'PY'
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
surface = sys.argv[4] or None
feedback = sys.argv[5]
no_fence = sys.argv[6] == "1"
no_persist = sys.argv[7] == "1"
host = sys.argv[8] or "127.0.0.1"
port = int(sys.argv[9] or "8765")
timeout_raw = sys.argv[10] or ""
timeout_seconds = float(timeout_raw) if timeout_raw.strip() else None
sys.path.insert(0, str(control_root))

from orchestrator.openui.enabled import openui_enabled
from orchestrator.openui.service import OpenUIServiceError, dump_json, run_ui_command

if not openui_enabled():
    print(
        "error: COMPASS_OPENUI_ENABLED is unset/off — "
        "set COMPASS_OPENUI_ENABLED=1 (or pass --enable-gates)",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "emit":
        result = run_ui_command(
            repo_root,
            "emit",
            surface=surface,
            fence=not no_fence,
            persist=not no_persist,
        )
        print(result["lang"], end="" if str(result["lang"]).endswith("\n") else "\n")
        meta = {k: v for k, v in result.items() if k != "lang"}
        print(dump_json({"openui": meta}), file=sys.stderr)
    else:
        result = run_ui_command(
            repo_root,
            cmd,
            surface=surface,
            decision=cmd if cmd in {"approve", "reject"} else None,
            feedback=feedback,
            host=host,
            port=port,
            timeout_seconds=timeout_seconds,
        )
        print(dump_json(result))
except OpenUIServiceError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
PY
