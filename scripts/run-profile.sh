#!/usr/bin/env bash
# northstar profile — list / show / export additive COMPASS_PROFILE bundles (v0).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$ROOT"

usage() {
  cat <<'USAGE'
Usage:
  northstar profile list
  northstar profile show [NAME]
  northstar profile export [NAME]

NAME defaults to $COMPASS_PROFILE (core|integrations).
export prints shell assignments for unset gates only (safe for eval).
USAGE
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

cmd="$1"
shift

case "$cmd" in
  list)
    PYTHONPATH="$ROOT" python3 - <<'PY'
from orchestrator.env_profiles import expand_profile, list_profiles
for name in list_profiles():
    gates = expand_profile(name)
    print(f"{name}: {', '.join(sorted(gates))}")
PY
    ;;
  show)
    name="${1:-}"
    PYTHONPATH="$ROOT" python3 - "$name" <<'PY'
import json, sys
from orchestrator.env_profiles import ProfileError, active_profile_name, expand_profile
name = sys.argv[1] or None
try:
    gates = expand_profile(name if name else None)
    resolved = name or active_profile_name() or ""
except ProfileError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
print(json.dumps({"profile": resolved or name, "gates": gates}, indent=2, sort_keys=True))
PY
    ;;
  export)
    name="${1:-}"
    PYTHONPATH="$ROOT" python3 - "$name" <<'PY'
import sys
from orchestrator.env_profiles import ProfileError, export_shell
name = sys.argv[1] or None
try:
    text = export_shell(name if name else None)
except ProfileError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
sys.stdout.write(text)
PY
    ;;
  *)
    echo "error: unknown profile subcommand: $cmd" >&2
    usage >&2
    exit 2
    ;;
esac
