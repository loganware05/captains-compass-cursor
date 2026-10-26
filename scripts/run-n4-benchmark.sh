#!/usr/bin/env bash
# run-n4-benchmark.sh — N4 cross-stack baseline vs evidence-informed benchmark.
#
# Requires COMPASS_N4_BENCHMARK_ENABLED=1 (or --enable-gates).
# Hermetic default; live evaluate scaffolding requires COMPASS_N4_STACK_ROOTS.
# Never auto-promotes Skills/policies; never authorizes Level 3 spend.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
MODE="hermetic"
SEED="20261026"
ENABLE_GATES=0

usage() {
  cat <<'USAGE'
Usage:
  run-n4-benchmark.sh [--mode hermetic|live] [--seed N]
                      [--repo-root PATH] [--enable-gates]

Requires COMPASS_N4_BENCHMARK_ENABLED=1 (or --enable-gates).
Hermetic mode uses tests/fixtures/n4 only (CI-safe).
Live mode requires COMPASS_N4_STACK_ROOTS and remains evaluate-only in v1.75.0.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root|--repo) REPO_ROOT="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --seed) SEED="$2"; shift 2 ;;
    --enable-gates) ENABLE_GATES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_N4_BENCHMARK_ENABLED=1
fi

export COMPASS_CONTROL_ROOT="${COMPASS_CONTROL_ROOT:-$ROOT}"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$ROOT" "$REPO_ROOT" "$MODE" "$SEED" <<'PY'
import json
import sys
from pathlib import Path

control_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
mode = sys.argv[3]
seed = int(sys.argv[4])
sys.path.insert(0, str(control_root))

from orchestrator.benchmark.n4.enabled import n4_enabled
from orchestrator.benchmark.n4.service import N4ServiceError, run_n4_benchmark

if not n4_enabled():
    print(
        "error: COMPASS_N4_BENCHMARK_ENABLED is unset/off — "
        "set COMPASS_N4_BENCHMARK_ENABLED=1 (or pass --enable-gates)",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    report = run_n4_benchmark(
        repo_root, mode=mode, seed=seed, persist=True
    )
except (N4ServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps({"status": "n4_complete", "report": report}, indent=2, sort_keys=True))
PY
