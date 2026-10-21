#!/usr/bin/env bash
# run-specialized-model.sh — Specialized Model Level 0 local baseline.
#
# Requires COMPASS_SPECIALIZED_MODEL_ENABLED=1 (or --enable-gates).
# No fine-tuning, no weight training, no auto-upload.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
ENABLE_GATES=0
EVIDENCE_DIR=""
WRITE_EVIDENCE=1
GOLD_PATH=""
EXPORT_ID=""
EXPORT_PATH=""

usage() {
  cat <<'USAGE'
Usage:
  run-specialized-model.sh baseline [--repo-root PATH] [--enable-gates]
                                    [--gold PATH] [--export-id ID]
                                    [--export-path PATH]
                                    [--evidence-dir PATH] [--no-write-evidence]

Requires COMPASS_SPECIALIZED_MODEL_ENABLED=1 (or --enable-gates).

Level 0 only: hermetic retrieval / prompt / stub-student baseline against a
held-out gold set. Optional C7 training-export attach. Never trains weights.
USAGE
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

CMD="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root|--repo)
      REPO_ROOT="$2"
      shift 2
      ;;
    --enable-gates)
      ENABLE_GATES=1
      shift
      ;;
    --gold)
      GOLD_PATH="$2"
      shift 2
      ;;
    --export-id)
      EXPORT_ID="$2"
      shift 2
      ;;
    --export-path)
      EXPORT_PATH="$2"
      shift 2
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

if [[ "$CMD" != "baseline" ]]; then
  echo "error: unknown command: $CMD (expected baseline)" >&2
  usage >&2
  exit 2
fi

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_SPECIALIZED_MODEL_ENABLED=1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$GOLD_PATH" "$EXPORT_ID" "$EXPORT_PATH" "$EVIDENCE_DIR" "$WRITE_EVIDENCE" <<'PY'
import json
import sys
from pathlib import Path

_root, repo, gold, export_id, export_path, evidence_dir, write_flag = sys.argv[1:8]

from orchestrator.specialized.enabled import require_specialized_model_gate
from orchestrator.specialized.service import SpecializedModelServiceError, run_baseline

try:
    require_specialized_model_gate()
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

kwargs = {"write_evidence": write_flag == "1"}
if gold.strip():
    kwargs["gold_path"] = Path(gold)
if export_id.strip():
    kwargs["export_id"] = export_id.strip()
if export_path.strip():
    kwargs["export_path"] = Path(export_path)
if evidence_dir.strip():
    kwargs["evidence_dir"] = Path(evidence_dir)

try:
    report = run_baseline(Path(repo), **kwargs)
except (SpecializedModelServiceError, PermissionError, ValueError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)

print(json.dumps(report, indent=2, sort_keys=True))
sys.exit(0 if report.get("overall_status") in {"pass", "warn"} else 1)
PY
