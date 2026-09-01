#!/usr/bin/env bash
# validate-sandbox-release-smokes.sh — Gate release closeout on sandbox smoke evidence (M18).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=""
REQUIRE_INTERACTIVE=1

usage() {
  cat <<'USAGE'
Usage: validate-sandbox-release-smokes.sh --version X.Y.Z [--skip-interactive]

Validates automated + interactive sandbox smoke evidence under
.agent/evidence/release-vX.Y.Z/ before release closeout.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --skip-interactive) REQUIRE_INTERACTIVE=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$VERSION" ]]; then
  echo "error: --version is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$ROOT" "$VERSION" "$REQUIRE_INTERACTIVE" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.release.sandbox_smokes import (
    SandboxSmokeError,
    validate_release_smoke_evidence,
)

root = Path(sys.argv[1])
version = sys.argv[2]
require_interactive = sys.argv[3] == "1"

try:
    result = validate_release_smoke_evidence(
        root,
        version,
        require_interactive=require_interactive,
    )
except SandboxSmokeError as exc:
    print(json.dumps({"passed": False, "error": str(exc)}, indent=2))
    raise SystemExit(1)

print(json.dumps({"passed": True, **result}, indent=2))
PY
