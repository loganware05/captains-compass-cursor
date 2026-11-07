#!/usr/bin/env bash
# run-sentry.sh — Read-only Sentry incident evidence ingest (I1).
#
# Requires COMPASS_SENTRY_INGEST_ENABLED=1.
# Live mode additionally requires COMPASS_SENTRY_LIVE=1 + auth token.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
ORG=""
PROJECT=""
ISSUE_ID=""
WINDOW_HOURS="24"
FIXTURE=""
PACKET_ID=""
FORCE_LIVE="0"

usage() {
  cat <<'USAGE'
Usage:
  run-sentry.sh fetch [--org ORG] [--project PROJECT] [--issue-id ID]
                 [--window-hours N] [--fixture PATH] [--live]
                 [--repo-root PATH]
  run-sentry.sh show --packet-id ID [--repo-root PATH]
  run-sentry.sh list [--repo-root PATH]

Requires COMPASS_SENTRY_INGEST_ENABLED=1.
Default mode is fixture. Live needs COMPASS_SENTRY_LIVE=1 and a read-only token.
Never writes to Sentry or grants authority.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    fetch|show|list)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --org)
      ORG="$2"
      shift 2
      ;;
    --project)
      PROJECT="$2"
      shift 2
      ;;
    --issue-id)
      ISSUE_ID="$2"
      shift 2
      ;;
    --window-hours)
      WINDOW_HOURS="$2"
      shift 2
      ;;
    --fixture)
      FIXTURE="$2"
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

if [[ "${COMPASS_SENTRY_INGEST_ENABLED:-}" != "1" && \
      "${COMPASS_SENTRY_INGEST_ENABLED:-}" != "true" && \
      "${COMPASS_SENTRY_INGEST_ENABLED:-}" != "yes" && \
      "${COMPASS_SENTRY_INGEST_ENABLED:-}" != "on" ]]; then
  echo "error: sentry ingest disabled — set COMPASS_SENTRY_INGEST_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$CMD" "$REPO_ROOT" "$ORG" "$PROJECT" "$ISSUE_ID" "$WINDOW_HOURS" "$FIXTURE" "$PACKET_ID" "$FORCE_LIVE" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

cmd, repo_root, org, project, issue_id, window_hours, fixture, packet_id, force_live = sys.argv[1:10]
repo = Path(repo_root)

from orchestrator.integrations.sentry.service import (
    SentryServiceError,
    fetch_incidents,
    list_packets,
    show_packet,
)

try:
    if cmd == "fetch":
        result = fetch_incidents(
            repo,
            org=org or None,
            project=project or None,
            issue_id=issue_id or None,
            window_hours=int(window_hours or "24"),
            fixture_path=Path(fixture) if fixture else None,
            force_live=force_live == "1",
        )
    elif cmd == "show":
        if not packet_id:
            raise SentryServiceError("--packet-id is required for show")
        result = show_packet(repo, packet_id)
    elif cmd == "list":
        result = list_packets(repo)
    else:
        raise SentryServiceError(f"unknown command: {cmd}")
except (SentryServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

print(json.dumps(result, indent=2, sort_keys=True))
PY
