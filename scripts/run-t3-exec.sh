#!/usr/bin/env bash
# run-t3-exec.sh — Gated T3 Code ExecutionAdapter (I2).
#
# Requires COMPASS_T3_EXEC_ENABLED=1. Fixture-first; live dual-gated.
# Never bypasses plan approval gates.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
PLAN_ID=""
OBJECTIVE=""
PROVIDER="fixture"
MODEL=""
EXECUTION_ID=""
ALLOW_FIXTURE_PLAN="0"
FORCE_LIVE="0"

usage() {
  cat <<'USAGE'
Usage:
  run-t3-exec.sh capabilities [--live] [--repo-root PATH]
  run-t3-exec.sh start --plan-id ID --objective TEXT
                 [--provider NAME] [--model NAME]
                 [--allow-fixture-plan] [--live] [--repo-root PATH]
  run-t3-exec.sh status --execution-id ID [--repo-root PATH]
  run-t3-exec.sh collect --execution-id ID [--repo-root PATH]
  run-t3-exec.sh cancel --execution-id ID [--repo-root PATH]
  run-t3-exec.sh show --execution-id ID [--repo-root PATH]
  run-t3-exec.sh list [--repo-root PATH]

Requires COMPASS_T3_EXEC_ENABLED=1.
start refuses unless IMPLEMENTATION_PLAN matches plan-id and is APPROVED
(or pass --allow-fixture-plan for hermetic tests).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    capabilities|start|status|collect|cancel|show|list)
      CMD="$1"
      shift
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --plan-id)
      PLAN_ID="$2"
      shift 2
      ;;
    --objective)
      OBJECTIVE="$2"
      shift 2
      ;;
    --provider)
      PROVIDER="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --execution-id|--id)
      EXECUTION_ID="$2"
      shift 2
      ;;
    --allow-fixture-plan)
      ALLOW_FIXTURE_PLAN="1"
      shift
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

if [[ "${COMPASS_T3_EXEC_ENABLED:-}" != "1" && \
      "${COMPASS_T3_EXEC_ENABLED:-}" != "true" && \
      "${COMPASS_T3_EXEC_ENABLED:-}" != "yes" && \
      "${COMPASS_T3_EXEC_ENABLED:-}" != "on" ]]; then
  echo "error: t3 execution adapter disabled — set COMPASS_T3_EXEC_ENABLED=1" >&2
  exit 2
fi

export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
cd "$REPO_ROOT"

python3 - "$CMD" "$REPO_ROOT" "$PLAN_ID" "$OBJECTIVE" "$PROVIDER" "$MODEL" "$EXECUTION_ID" "$ALLOW_FIXTURE_PLAN" "$FORCE_LIVE" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

(
    cmd,
    repo_root,
    plan_id,
    objective,
    provider,
    model,
    execution_id,
    allow_fixture,
    force_live,
) = sys.argv[1:10]
repo = Path(repo_root)

from orchestrator.integrations.t3.service import (
    T3ServiceError,
    cancel_execution,
    collect_execution,
    list_capabilities,
    list_executions,
    show_execution,
    start_execution,
    status_execution,
)

try:
    if cmd == "capabilities":
        result = list_capabilities(force_live=force_live == "1")
    elif cmd == "start":
        result = start_execution(
            repo,
            plan_id=plan_id,
            objective=objective,
            provider=provider or "fixture",
            model=model,
            allow_fixture_plan=allow_fixture == "1",
            force_live=force_live == "1",
        )
    elif cmd == "status":
        if not execution_id:
            raise T3ServiceError("--execution-id is required")
        result = status_execution(repo, execution_id)
    elif cmd == "collect":
        if not execution_id:
            raise T3ServiceError("--execution-id is required")
        result = collect_execution(repo, execution_id)
    elif cmd == "cancel":
        if not execution_id:
            raise T3ServiceError("--execution-id is required")
        result = cancel_execution(repo, execution_id)
    elif cmd == "show":
        if not execution_id:
            raise T3ServiceError("--execution-id is required")
        result = show_execution(repo, execution_id)
    elif cmd == "list":
        result = list_executions(repo)
    else:
        raise T3ServiceError(f"unknown command: {cmd}")
except (T3ServiceError, PermissionError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

print(json.dumps(result, indent=2, sort_keys=True))
PY
