#!/usr/bin/env bash
# run-explain.sh — Gated Scrimba Explain surface (I4).
#
# Requires COMPASS_EXPLAIN_ENABLED=1. Fixture-first; live dual-gated.
# Never auto-publishes. Distinct from `northstar status explain`.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
TOPIC=""
PACKET_ID=""
FORCE_LIVE="0"
MCP="main"

usage() {
  cat <<'USAGE'
Usage:
  run-explain.sh create --topic TEXT [--mcp main|pr] [--live] [--repo-root PATH]
  run-explain.sh show --packet-id ID [--repo-root PATH]
  run-explain.sh list [--repo-root PATH]

Requires COMPASS_EXPLAIN_ENABLED=1.
Default mode is fixture. Live Scrimba MCP streaming is deferred.
Distinct from: northstar status explain
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    create|show|list)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --topic|-t)
      TOPIC="$2"
      shift 2
      ;;
    --packet-id|--id)
      PACKET_ID="$2"
      shift 2
      ;;
    --mcp)
      MCP="$2"
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

if [[ "${COMPASS_EXPLAIN_ENABLED:-}" != "1" && \
      "${COMPASS_EXPLAIN_ENABLED:-}" != "true" && \
      "${COMPASS_EXPLAIN_ENABLED:-}" != "yes" && \
      "${COMPASS_EXPLAIN_ENABLED:-}" != "on" ]]; then
  echo "error: scrimba explain disabled — set COMPASS_EXPLAIN_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$CMD" "$REPO_ROOT" "$TOPIC" "$PACKET_ID" "$FORCE_LIVE" "$MCP" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.integrations.scrimba import service

cmd, repo_root, topic, packet_id, force_live, mcp = sys.argv[1:7]
root = Path(repo_root)
live = force_live in {"1", "true", "yes", "on"}

try:
    if cmd == "create":
        if not topic.strip():
            print("error: --topic required", file=sys.stderr)
            sys.exit(2)
        result = service.create(root, topic, live=live, mcp=mcp)
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
