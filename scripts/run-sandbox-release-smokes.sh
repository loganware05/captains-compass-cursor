#!/usr/bin/env bash
# run-sandbox-release-smokes.sh — Deterministic sandbox release smokes (M18).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX="${COMPASS_SANDBOX_PATH:-/Users/loganware/Documents/Personal/Code/captain-compass-sandbox}"
VERSION=""
WRITE_EVIDENCE=1

usage() {
  cat <<'USAGE'
Usage: run-sandbox-release-smokes.sh [--sandbox PATH] [--version X.Y.Z] [--no-write]

Runs fixture-based automated release smokes against the control repo and sandbox path.
Writes .agent/evidence/release-vX.Y.Z/sandbox-smokes-automated.json when --version is set.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sandbox) SANDBOX="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    --no-write) WRITE_EVIDENCE=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$VERSION" ]]; then
  VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export COMPASS_SANDBOX_PATH="$SANDBOX"

python3 - "$ROOT" "$SANDBOX" "$VERSION" "$WRITE_EVIDENCE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.release.sandbox_smokes import (
    run_automated_sandbox_smokes,
    write_smoke_report,
)

control = Path(sys.argv[1]).resolve()
sandbox = Path(sys.argv[2]).resolve()
version = sys.argv[3].lstrip("v")
write_evidence = sys.argv[4] == "1"

report = run_automated_sandbox_smokes(control, sandbox)
print(json.dumps(report, indent=2))

if write_evidence:
    evidence_dir = control / ".agent" / "evidence" / f"release-v{version}"
    path = evidence_dir / "sandbox-smokes-automated.json"
    write_smoke_report(report, path)
    print(json.dumps({"evidence": str(path)}, indent=2), file=sys.stderr)

raise SystemExit(0 if report.get("passed") else 1)
PY
