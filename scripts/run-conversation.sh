#!/usr/bin/env bash
# run-conversation.sh — ChatGPT / Obsidian AI Exporter trajectory ingest.
#
# Requires COMPASS_CONVERSATION_INGEST_ENABLED=1.
# Evidence-only — never grants authority or auto-promotes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
PATH_ARG=""
SOURCE="obsidian-ai-exporter"
MODEL=""
TRAJECTORY_ID=""
DRAFT_EXEMPLAR=""
NO_KNOWLEDGE="0"

usage() {
  cat <<'USAGE'
Usage:
  run-conversation.sh ingest --path FILE
                 [--source chatgpt|obsidian-ai-exporter|t3-attachment]
                 [--model LABEL] [--draft-exemplar positive|negative]
                 [--no-knowledge] [--repo-root PATH]
  run-conversation.sh show --id TRAJECTORY_ID [--repo-root PATH]
  run-conversation.sh list [--repo-root PATH]

Requires COMPASS_CONVERSATION_INGEST_ENABLED=1.
Writes trajectories under .agent/conversations/ and optional know-conv-* items.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    ingest|show|list)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --path)
      PATH_ARG="$2"
      shift 2
      ;;
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --id)
      TRAJECTORY_ID="$2"
      shift 2
      ;;
    --draft-exemplar)
      DRAFT_EXEMPLAR="$2"
      shift 2
      ;;
    --no-knowledge)
      NO_KNOWLEDGE="1"
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

if [[ "${COMPASS_CONVERSATION_INGEST_ENABLED:-}" != "1" && \
      "${COMPASS_CONVERSATION_INGEST_ENABLED:-}" != "true" && \
      "${COMPASS_CONVERSATION_INGEST_ENABLED:-}" != "yes" && \
      "${COMPASS_CONVERSATION_INGEST_ENABLED:-}" != "on" ]]; then
  echo "error: conversation ingest disabled — set COMPASS_CONVERSATION_INGEST_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$CMD" "$REPO_ROOT" "$PATH_ARG" "$SOURCE" "$MODEL" "$TRAJECTORY_ID" "$DRAFT_EXEMPLAR" "$NO_KNOWLEDGE" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

cmd, repo_root, path_arg, source, model, traj_id, draft, no_knowledge = sys.argv[1:9]
repo = Path(repo_root)

from orchestrator.conversation.service import (
    ConversationServiceError,
    ingest_conversation_export,
    list_trajectories,
    show_trajectory,
)

try:
    if cmd == "ingest":
        if not path_arg:
            raise ConversationServiceError("--path is required for ingest")
        result = ingest_conversation_export(
            repo,
            Path(path_arg),
            source=source or "obsidian-ai-exporter",
            model=model or None,
            draft_exemplar=draft or None,
            write_knowledge=no_knowledge != "1",
        )
    elif cmd == "show":
        if not traj_id:
            raise ConversationServiceError("--id is required for show")
        result = show_trajectory(repo, traj_id)
    elif cmd == "list":
        result = list_trajectories(repo)
    else:
        raise ConversationServiceError(f"unknown command: {cmd}")
except (ConversationServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

print(json.dumps(result, indent=2, sort_keys=True))
PY
