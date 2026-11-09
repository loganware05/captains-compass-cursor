#!/usr/bin/env bash
# run-identity.sh — Gated WorkOS AuthKit identity surface (I5).
#
# Requires COMPASS_IDENTITY_ENABLED=1 (alias COMPASS_WORKOS_ENABLED=1).
# Fixture-first; live dual-gated. Never grants Captain approval.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
PACKET_ID=""
FORCE_LIVE="0"

usage() {
  cat <<'USAGE'
Usage:
  run-identity.sh sync [--live] [--repo-root PATH]
  run-identity.sh show --packet-id ID [--repo-root PATH]
  run-identity.sh list [--repo-root PATH]

Requires COMPASS_IDENTITY_ENABLED=1 (alias COMPASS_WORKOS_ENABLED=1).
Default mode is fixture. Live WorkOS API sync is deferred.
WorkOS roles never replace GitHub Captain approval.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    sync|show|list)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --packet-id|--id)
      PACKET_ID="$2"
      shift 2
      ;;
    --live)
      FORCE_LIVE="1"
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

enabled="${COMPASS_IDENTITY_ENABLED:-}"
alias_enabled="${COMPASS_WORKOS_ENABLED:-}"
if [[ "$enabled" != "1" && "$enabled" != "true" && "$enabled" != "yes" && "$enabled" != "on" && \
      "$alias_enabled" != "1" && "$alias_enabled" != "true" && "$alias_enabled" != "yes" && "$alias_enabled" != "on" ]]; then
  echo "error: identity surface disabled — set COMPASS_IDENTITY_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$CMD" "$REPO_ROOT" "$PACKET_ID" "$FORCE_LIVE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.integrations.workos import service

cmd, repo_root, packet_id, force_live = sys.argv[1:5]
root = Path(repo_root)
live = force_live in {"1", "true", "yes", "on"}

try:
    if cmd == "sync":
        result = service.sync(root, live=live)
    elif cmd == "show":
        if not packet_id.strip():
            print("error: --packet-id required", file=sys.stderr)
            sys.exit(2)
        result = service.show(root, packet_id)
    elif cmd == "list":
        result = service.list_packets(root)
    else:
        print(f"error: unknown command {cmd}", file=sys.stderr)
        sys.exit(2)
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
except FileNotFoundError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)
except (RuntimeError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

print(json.dumps(result, indent=2, sort_keys=True))
PY
