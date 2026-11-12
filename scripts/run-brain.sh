#!/usr/bin/env bash
# run-brain.sh — Cognitive Core project-state + memory/retrieval (C1/C2).
#
# Requires COMPASS_BRAIN_ENABLED=1. Session-memory subcommands also require
# COMPASS_SESSION_MEMORY_ENABLED=1. Read-oriented: never approves plans,
# promotes Skills/Policies, merges, deploys, or rewrites project memory docs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
MEMORY_CMD=""
SNAPSHOT_ID=""
QUERY=""
MODE="hybrid"
TOP="10"
OBS_ID=""
INGEST_PATH=""
TIMELINE_LIMIT="20"
INCLUDE_SESSION_MEMORY=0

usage() {
  cat <<'USAGE'
Usage:
  run-brain.sh sync [--repo-root PATH]
  run-brain.sh status [--repo-root PATH]
  run-brain.sh show --snapshot-id ID [--repo-root PATH]
  run-brain.sh context --query TEXT [--mode hybrid|keyword|vector] [--top N]
                       [--include-session-memory] [--repo-root PATH]
  run-brain.sh memory ingest --path FILE [--repo-root PATH]
  run-brain.sh memory search --query TEXT [--top N] [--repo-root PATH]
  run-brain.sh memory timeline [--limit N] [--repo-root PATH]
  run-brain.sh memory show --id ID [--repo-root PATH]

Requires COMPASS_BRAIN_ENABLED=1.
Session-memory commands and --include-session-memory also require
COMPASS_SESSION_MEMORY_ENABLED=1.
Read-oriented: never mutates authority or auto-writes canonical memory docs.
C1 persists under .agent/project-state/; C2 context is ephemeral JSON.
Session observations persist under .agent/session-memory/ (gitignored).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    sync|status|show|context|memory)
      CMD="$1"
      shift
      if [[ "$CMD" == "memory" ]]; then
        if [[ $# -lt 1 ]]; then
          echo "error: memory requires a subcommand" >&2
          usage >&2
          exit 2
        fi
        MEMORY_CMD="$1"
        shift
      fi
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --snapshot-id)
      SNAPSHOT_ID="$2"
      shift 2
      ;;
    --query)
      QUERY="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --top)
      TOP="$2"
      shift 2
      ;;
    --id)
      OBS_ID="$2"
      shift 2
      ;;
    --path)
      INGEST_PATH="$2"
      shift 2
      ;;
    --limit)
      TIMELINE_LIMIT="$2"
      shift 2
      ;;
    --include-session-memory)
      INCLUDE_SESSION_MEMORY=1
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

if [[ "$CMD" == "context" && -z "$QUERY" ]]; then
  echo "error: --query is required for brain context" >&2
  usage >&2
  exit 2
fi

if [[ "$CMD" == "memory" ]]; then
  case "$MEMORY_CMD" in
    ingest)
      if [[ -z "$INGEST_PATH" ]]; then
        echo "error: --path is required for memory ingest" >&2
        usage >&2
        exit 2
      fi
      ;;
    search)
      if [[ -z "$QUERY" ]]; then
        echo "error: --query is required for memory search" >&2
        usage >&2
        exit 2
      fi
      ;;
    show)
      if [[ -z "$OBS_ID" ]]; then
        echo "error: --id is required for memory show" >&2
        usage >&2
        exit 2
      fi
      ;;
    timeline)
      ;;
    *)
      echo "error: unknown memory subcommand: $MEMORY_CMD" >&2
      usage >&2
      exit 2
      ;;
  esac
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$MEMORY_CMD" "$SNAPSHOT_ID" "$QUERY" "$MODE" "$TOP" "$OBS_ID" "$INGEST_PATH" "$TIMELINE_LIMIT" "$INCLUDE_SESSION_MEMORY" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
cmd = sys.argv[3]
memory_cmd = sys.argv[4]
snapshot_id = sys.argv[5]
query = sys.argv[6]
mode = sys.argv[7]
try:
    top_n = int(sys.argv[8] or "10")
except ValueError:
    print("error: --top must be an integer", file=sys.stderr)
    sys.exit(2)
obs_id = sys.argv[9]
ingest_path = sys.argv[10]
try:
    timeline_limit = int(sys.argv[11] or "20")
except ValueError:
    print("error: --limit must be an integer", file=sys.stderr)
    sys.exit(2)
include_session_memory = sys.argv[12] == "1"

sys.path.insert(0, str(control_root))

from orchestrator.cognitive.enabled import brain_enabled, session_memory_enabled
from orchestrator.cognitive.service import (
    BrainServiceError,
    context,
    show,
    status,
    sync,
)
from orchestrator.cognitive.session_memory import (
    SessionMemoryError,
    ingest_observation,
    search_observations,
    show_observation,
    timeline_observations,
)

if not brain_enabled():
    print(
        "error: COMPASS_BRAIN_ENABLED is unset/off — "
        "set COMPASS_BRAIN_ENABLED=1 to run northstar brain",
        file=sys.stderr,
    )
    sys.exit(2)

needs_session = cmd == "memory" or (cmd == "context" and include_session_memory)
if needs_session and not session_memory_enabled():
    print(
        "error: COMPASS_SESSION_MEMORY_ENABLED is unset/off — "
        "set COMPASS_SESSION_MEMORY_ENABLED=1 for session memory",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    if cmd == "sync":
        result = sync(repo_root)
    elif cmd == "status":
        result = status(repo_root)
    elif cmd == "show":
        result = show(repo_root, snapshot_id=snapshot_id)
    elif cmd == "context":
        result = context(
            repo_root,
            query=query,
            mode=mode,
            top_n=top_n,
            include_session_memory=include_session_memory,
        )
    elif cmd == "memory":
        if memory_cmd == "ingest":
            result = ingest_observation(repo_root, path=Path(ingest_path))
        elif memory_cmd == "search":
            result = search_observations(repo_root, query, top_n=top_n)
        elif memory_cmd == "timeline":
            result = timeline_observations(repo_root, limit=timeline_limit)
        elif memory_cmd == "show":
            result = show_observation(repo_root, obs_id)
        else:
            print(f"error: unknown memory subcommand: {memory_cmd}", file=sys.stderr)
            sys.exit(2)
    else:
        print(f"error: unknown command: {cmd}", file=sys.stderr)
        sys.exit(2)
except (BrainServiceError, SessionMemoryError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(result, indent=2, sort_keys=True))
PY
