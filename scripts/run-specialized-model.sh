#!/usr/bin/env bash
# run-specialized-model.sh — Specialized Model Level 0 baseline + Level 1 LoRA.
#
# Requires COMPASS_SPECIALIZED_MODEL_ENABLED=1 (or --enable-gates).
# Never commits weight/adapter binaries; never auto-promotes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
LORA_PHASE=""
ENABLE_GATES=0
EVIDENCE_DIR=""
WRITE_EVIDENCE=1
GOLD_PATH=""
EXPORT_ID=""
EXPORT_PATH=""
DATASET_PATH=""
ADAPTER_ROOT=""
DRY_RUN=1
EXTERNAL_BLOB=""

usage() {
  cat <<'USAGE'
Usage:
  run-specialized-model.sh baseline [--repo-root PATH] [--enable-gates]
                                    [--gold PATH] [--export-id ID]
                                    [--export-path PATH]
                                    [--evidence-dir PATH] [--no-write-evidence]

  run-specialized-model.sh lora prepare|train|evaluate|pipeline
                                    [--repo-root PATH] [--enable-gates]
                                    [--export-id ID | --export-path PATH]
                                    [--dataset PATH] [--adapter-root PATH]
                                    [--gold PATH] [--external-blob PATH]
                                    [--dry-run|--no-dry-run]
                                    [--evidence-dir PATH] [--no-write-evidence]

Requires COMPASS_SPECIALIZED_MODEL_ENABLED=1 (or --enable-gates).

Level 0: hermetic baseline (no fine-tuning).
Level 1: prepare dataset from C7 export; train via external trainer or --dry-run;
         evaluate adapter vs Level 0 baseline. Weights stay outside this repo.
USAGE
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

CMD="$1"
shift

if [[ "$CMD" == "lora" ]]; then
  if [[ $# -lt 1 ]]; then
    echo "error: lora requires prepare|train|evaluate|pipeline" >&2
    usage >&2
    exit 2
  fi
  LORA_PHASE="$1"
  shift
fi

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
    --dataset)
      DATASET_PATH="$2"
      shift 2
      ;;
    --adapter-root)
      ADAPTER_ROOT="$2"
      shift 2
      ;;
    --external-blob)
      EXTERNAL_BLOB="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-dry-run)
      DRY_RUN=0
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

if [[ "$CMD" != "baseline" && "$CMD" != "lora" ]]; then
  echo "error: unknown command: $CMD (expected baseline|lora)" >&2
  usage >&2
  exit 2
fi

if [[ "$CMD" == "lora" ]]; then
  case "$LORA_PHASE" in
    prepare|train|evaluate|pipeline) ;;
    *)
      echo "error: unknown lora phase: $LORA_PHASE" >&2
      usage >&2
      exit 2
      ;;
  esac
fi

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_SPECIALIZED_MODEL_ENABLED=1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$LORA_PHASE" "$GOLD_PATH" "$EXPORT_ID" \
  "$EXPORT_PATH" "$DATASET_PATH" "$ADAPTER_ROOT" "$EXTERNAL_BLOB" \
  "$EVIDENCE_DIR" "$WRITE_EVIDENCE" "$DRY_RUN" <<'PY'
import json
import sys
from pathlib import Path

(
    _root,
    repo,
    cmd,
    lora_phase,
    gold,
    export_id,
    export_path,
    dataset_path,
    adapter_root,
    external_blob,
    evidence_dir,
    write_flag,
    dry_run_flag,
) = sys.argv[1:14]

from orchestrator.specialized.enabled import require_specialized_model_gate
from orchestrator.specialized.lora import (
    evaluate_lora,
    prepare_dataset,
    run_lora_pipeline,
    train_lora,
)
from orchestrator.specialized.service import SpecializedModelServiceError, run_baseline

try:
    require_specialized_model_gate()
except PermissionError as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(2)

write_evidence = write_flag == "1"
dry_run = dry_run_flag == "1"
repo_path = Path(repo)

try:
    if cmd == "baseline":
        kwargs = {"write_evidence": write_evidence}
        if gold.strip():
            kwargs["gold_path"] = Path(gold)
        if export_id.strip():
            kwargs["export_id"] = export_id.strip()
        if export_path.strip():
            kwargs["export_path"] = Path(export_path)
        if evidence_dir.strip():
            kwargs["evidence_dir"] = Path(evidence_dir)
        report = run_baseline(repo_path, **kwargs)
        print(json.dumps(report, indent=2, sort_keys=True))
        sys.exit(0 if report.get("overall_status") in {"pass", "warn"} else 1)

    if lora_phase == "prepare":
        prepared = prepare_dataset(
            repo_path,
            export_id=export_id.strip() or None,
            export_path=Path(export_path) if export_path.strip() else None,
            gold_path=Path(gold) if gold.strip() else None,
            external_blob_path=external_blob.strip() or None,
        )
        print(json.dumps(prepared, indent=2, sort_keys=True))
        sys.exit(0)

    if lora_phase == "train":
        if not dataset_path.strip():
            raise SpecializedModelServiceError("lora train requires --dataset PATH")
        result = train_lora(
            repo_path,
            dataset_path=Path(dataset_path),
            dry_run=dry_run,
            adapter_root=Path(adapter_root) if adapter_root.strip() else None,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        sys.exit(0)

    if lora_phase == "evaluate":
        report = evaluate_lora(
            repo_path,
            dataset_path=Path(dataset_path) if dataset_path.strip() else None,
            adapter_root=Path(adapter_root) if adapter_root.strip() else None,
            gold_path=Path(gold) if gold.strip() else None,
            dry_run=dry_run,
            evidence_dir=Path(evidence_dir) if evidence_dir.strip() else None,
            write_evidence=write_evidence,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        sys.exit(0 if report.get("overall_status") in {"pass", "warn"} else 1)

    # pipeline
    report = run_lora_pipeline(
        repo_path,
        export_id=export_id.strip() or None,
        export_path=Path(export_path) if export_path.strip() else None,
        dataset_path=Path(dataset_path) if dataset_path.strip() else None,
        dry_run=dry_run,
        adapter_root=Path(adapter_root) if adapter_root.strip() else None,
        gold_path=Path(gold) if gold.strip() else None,
        evidence_dir=Path(evidence_dir) if evidence_dir.strip() else None,
        write_evidence=write_evidence,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    sys.exit(0 if report.get("overall_status") in {"pass", "warn"} else 1)

except (SpecializedModelServiceError, PermissionError, ValueError, FileNotFoundError) as exc:
    print(f"error: {exc}", file=sys.stderr)
    sys.exit(1)
PY
