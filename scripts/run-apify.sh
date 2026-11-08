#!/usr/bin/env bash
# run-apify.sh — Gated Apify research surface (I3).
#
# Requires COMPASS_APIFY_ENABLED=1. Fixture-first; live dual-gated.
# Never auto-runs Actors (call-actor deferred).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
QUERY=""
PACKET_ID=""
FORCE_LIVE="0"

usage() {
  cat <<'USAGE'
Usage:
  run-apify.sh search --query TEXT [--live] [--repo-root PATH]
  run-apify.sh show --packet-id ID [--repo-root PATH]
  run-apify.sh list [--repo-root PATH]

Requires COMPASS_APIFY_ENABLED=1.
Default mode is fixture TI search. Live Actor runs are deferred.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    search|show|list)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --query|-q)
      QUERY="$2"
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

if [[ "${COMPASS_APIFY_ENABLED:-}" != "1" && \
      "${COMPASS_APIFY_ENABLED:-}" != "true" && \
      "${COMPASS_APIFY_ENABLED:-}" != "yes" && \
      "${COMPASS_APIFY_ENABLED:-}" != "on" ]]; then
  echo "error: apify surface disabled — set COMPASS_APIFY_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$CMD" "$REPO_ROOT" "$QUERY" "$PACKET_ID" "$FORCE_LIVE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.integrations.apify import service

cmd, repo_root, query, packet_id, force_live = sys.argv[1:6]
root = Path(repo_root)
live = force_live in {"1", "true", "yes", "on"}

try:
    if cmd == "search":
        if not query.strip():
            print("error: --query required", file=sys.stderr)
            sys.exit(2)
        result = service.search(root, query, live=live)
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
except RuntimeError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

print(json.dumps(result, indent=2, sort_keys=True))
PY
