#!/usr/bin/env bash
# run-formal.sh — Opt-in Bend proof spike for the policy-lifecycle decision core (#278).
#
# Requires COMPASS_BEND_PROOF_ENABLED=1. Bend is an optional local tool: when it
# is absent the check is reported as "skipped" (exit 0) unless --require-tool.
# Never edits production code; never grants authority.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  run-formal.sh check policy-lifecycle [--no-mutations] [--no-verdict] [--no-write]
                                       [--require-tool] [--base-ref REF] [--strict-laws]
  run-formal.sh lock  policy-lifecycle

check   proofs (+ Lean kernel --verdict), Python<->model conformance, drift lock,
        mutation controls, law integrity vs base ref; writes
        .agent/evidence/bend-policy-proof-spike/LATEST_check.json
lock    re-record the states.py table hash after the proofs and conformance pass

Requires COMPASS_BEND_PROOF_ENABLED=1.
Exit: 0 ok/skipped, 1 failed, 2 usage or gate.
USAGE
}

if [[ $# -eq 1 && ( "$1" == "-h" || "$1" == "--help" ) ]]; then
  usage
  exit 0
fi

if [[ $# -lt 2 ]]; then
  usage >&2
  exit 2
fi

CMD="$1"
TARGET="$2"
shift 2

if [[ "$CMD" == "-h" || "$CMD" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$TARGET" != "policy-lifecycle" ]]; then
  echo "error: unknown formal target: $TARGET (supported: policy-lifecycle)" >&2
  exit 2
fi

MUTATIONS=1
VERDICT=1
WRITE=1
REQUIRE_TOOL=0
STRICT_LAWS=0
BASE_REF="origin/main"

need_value() {
  if [[ $# -lt 2 || "$2" == -* ]]; then
    echo "error: $1 requires a value" >&2
    usage >&2
    exit 2
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-mutations) MUTATIONS=0; shift ;;
    --no-verdict) VERDICT=0; shift ;;
    --no-write) WRITE=0; shift ;;
    --require-tool) REQUIRE_TOOL=1; shift ;;
    --strict-laws) STRICT_LAWS=1; shift ;;
    --base-ref) need_value "$@"; BASE_REF="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

export COMPASS_CONTROL_ROOT="${COMPASS_CONTROL_ROOT:-$ROOT}"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
# Run from the control repo so a stray module in the caller's cwd cannot shadow ours.
cd "$ROOT"

python3 - "$CMD" "$ROOT" "$MUTATIONS" "$VERDICT" "$WRITE" "$REQUIRE_TOOL" "$STRICT_LAWS" "$BASE_REF" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.formal import policy_lifecycle as pl
from orchestrator.formal.gates import require_bend_proof_enabled

cmd = sys.argv[1]
root = Path(sys.argv[2])
mutations, verdict, write, require_tool, strict_laws = (a == "1" for a in sys.argv[3:8])
base_ref = sys.argv[8]

try:
    require_bend_proof_enabled()
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

try:
    if cmd == "check":
        result = pl.check(
            root,
            mutations=mutations,
            verdict=verdict,
            write_evidence=write,
            require_tool=require_tool,
            strict_laws=strict_laws,
            base_ref=base_ref,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        sys.exit(0 if result["status"] in {"ok", "skipped"} else 1)
    elif cmd == "lock":
        result = pl.check(root, mutations=False, write_evidence=False, require_tool=True, base_ref=base_ref)
        # Only a stale lock ("drift") may be outstanding; proofs and conformance must pass.
        failures = [f for f in result.get("failures", []) if f != "drift"]
        if failures or "proofs" not in result:
            print(json.dumps({"status": "refused",
                              "reason": "proofs and conformance must pass before locking",
                              "failures": failures or ["toolchain"]}, indent=2))
            sys.exit(1)
        lock = pl.write_lock(root)
        print(json.dumps({"status": "locked", "tables_sha256": lock["tables_sha256"]}, indent=2))
        sys.exit(0)
    else:
        print(f"error: unknown command {cmd}", file=sys.stderr)
        sys.exit(2)
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)
except Exception as exc:  # noqa: BLE001
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)
PY
