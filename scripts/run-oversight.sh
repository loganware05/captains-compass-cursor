#!/usr/bin/env bash
# run-oversight.sh — Read-only persistent oversight (brain + Overseer compose).
#
# Requires COMPASS_STATUS_ENABLED=1. Optional brain sync when
# COMPASS_BRAIN_ENABLED=1. Pass --enable-gates to export both for this process.
#
# Proposal-only: never auto-applies reconcile edits or grants authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
SINCE=""
ENABLE_GATES=0
EVIDENCE_DIR=""
WRITE_EVIDENCE=1
INCLUDE_BRAIN=""

usage() {
  cat <<'USAGE'
Usage:
  run-oversight.sh [--repo-root PATH] [--since SHA] [--enable-gates]
                   [--include-brain|--skip-brain] [--evidence-dir PATH]
                   [--no-write-evidence]

Requires COMPASS_STATUS_ENABLED=1 (or --enable-gates).
Brain sync runs when COMPASS_BRAIN_ENABLED=1 unless --skip-brain.

Writes a schema-validated report under
  .agent/evidence/read-only-persistent-oversight/
and a copy under
  .agent/status/oversight-runs/
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root|--repo)
      REPO_ROOT="$2"
      shift 2
      ;;
    --since)
      SINCE="$2"
      shift 2
      ;;
    --enable-gates)
      ENABLE_GATES=1
      shift
      ;;
    --include-brain)
      INCLUDE_BRAIN="1"
      shift
      ;;
    --skip-brain)
      INCLUDE_BRAIN="0"
      shift
      ;;
    --evidence-dir)
      EVIDENCE_DIR="$2"
      shift 2
      ;;
    --no-write-evidence)
      WRITE_EVIDENCE=0
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

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_STATUS_ENABLED=1
  export COMPASS_BRAIN_ENABLED=1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$SINCE" "$EVIDENCE_DIR" "$WRITE_EVIDENCE" "$INCLUDE_BRAIN" <<'PY'
import json
import sys
from pathlib import Path

_root, repo, since, evidence_dir, write_flag, include_brain = sys.argv[1:7]

from orchestrator.oversight.enabled import require_oversight_status_gate
from orchestrator.oversight.service import OversightServiceError, run_oversight

try:
    require_oversight_status_gate()
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

kwargs = {"write_evidence": write_flag == "1"}
if since.strip():
    kwargs["since_sha"] = since.strip()
if evidence_dir.strip():
    kwargs["evidence_dir"] = Path(evidence_dir)
if include_brain == "1":
    kwargs["include_brain"] = True
elif include_brain == "0":
    kwargs["include_brain"] = False

try:
    report = run_oversight(Path(repo), **kwargs)
except (OversightServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(report, indent=2, sort_keys=True))
sys.exit(0 if report.get("overall_status") in {"pass", "warn"} else 1)
PY
