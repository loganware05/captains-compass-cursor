#!/usr/bin/env bash
# run-specialized-model.sh — Specialized Model Level 0/1/2 harness.
#
# Requires COMPASS_SPECIALIZED_MODEL_ENABLED=1 (or --enable-gates).
# Never commits weight/adapter binaries; never auto-promotes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$ROOT"
CMD=""
PHASE=""
ENABLE_GATES=0
EVIDENCE_DIR=""
WRITE_EVIDENCE=1
GOLD_PATH=""
EXPORT_ID=""
EXPORT_PATH=""
DATASET_PATH=""
JOB_PATH=""
ADAPTER_ROOT=""
DRY_RUN=1
COST_ACK=0
EXTERNAL_BLOB=""

usage() {
  cat <<'USAGE'
Usage:
  run-specialized-model.sh baseline […]
  run-specialized-model.sh lora prepare|train|evaluate|pipeline […]
  run-specialized-model.sh gpu prepare|submit|evaluate|pipeline […]
                                    [--repo-root PATH] [--enable-gates]
                                    [--export-id ID | --export-path PATH]
                                    [--dataset PATH] [--job PATH]
                                    [--adapter-root PATH] [--gold PATH]
                                    [--dry-run|--no-dry-run] [--cost-ack]
                                    [--evidence-dir PATH] [--no-write-evidence]

Requires COMPASS_SPECIALIZED_MODEL_ENABLED=1 (or --enable-gates).

Level 0: hermetic baseline (no fine-tuning).
Level 1: LoRA prepare/train/evaluate (external trainer or --dry-run).
Level 2: GPU QLoRA prepare/submit/evaluate; non-dry-run submit needs --cost-ack.
Weights stay outside this control repo; never auto-promote.
USAGE
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 2
fi

CMD="$1"
shift

if [[ "$CMD" == "lora" || "$CMD" == "gpu" ]]; then
  if [[ $# -lt 1 ]]; then
    echo "error: $CMD requires a phase subcommand" >&2
    usage >&2
    exit 2
  fi
  PHASE="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root|--repo) REPO_ROOT="$2"; shift 2 ;;
    --enable-gates) ENABLE_GATES=1; shift ;;
    --gold) GOLD_PATH="$2"; shift 2 ;;
    --export-id) EXPORT_ID="$2"; shift 2 ;;
    --export-path) EXPORT_PATH="$2"; shift 2 ;;
    --dataset) DATASET_PATH="$2"; shift 2 ;;
    --job) JOB_PATH="$2"; shift 2 ;;
    --adapter-root) ADAPTER_ROOT="$2"; shift 2 ;;
    --external-blob) EXTERNAL_BLOB="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --no-dry-run) DRY_RUN=0; shift ;;
    --cost-ack) COST_ACK=1; shift ;;
    --evidence-dir) EVIDENCE_DIR="$2"; shift 2 ;;
    --no-write-evidence) WRITE_EVIDENCE=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$CMD" in
  baseline) ;;
  lora)
    case "$PHASE" in
      prepare|train|evaluate|pipeline) ;;
      *) echo "error: unknown lora phase: $PHASE" >&2; usage >&2; exit 2 ;;
    esac
    ;;
  gpu)
    case "$PHASE" in
      prepare|submit|evaluate|pipeline) ;;
      *) echo "error: unknown gpu phase: $PHASE" >&2; usage >&2; exit 2 ;;
    esac
    ;;
  *)
    echo "error: unknown command: $CMD (expected baseline|lora|gpu)" >&2
    usage >&2
    exit 2
    ;;
esac

if [[ "$ENABLE_GATES" -eq 1 ]]; then
  export COMPASS_SPECIALIZED_MODEL_ENABLED=1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$ROOT" "$REPO_ROOT" "$CMD" "$PHASE" "$GOLD_PATH" "$EXPORT_ID" \
  "$EXPORT_PATH" "$DATASET_PATH" "$JOB_PATH" "$ADAPTER_ROOT" "$EXTERNAL_BLOB" \
  "$EVIDENCE_DIR" "$WRITE_EVIDENCE" "$DRY_RUN" "$COST_ACK" <<'PY'
import json
import sys
from pathlib import Path

(
    _root,
    repo,
    cmd,
    phase,
    gold,
    export_id,
    export_path,
    dataset_path,
    job_path,
    adapter_root,
    external_blob,
    evidence_dir,
    write_flag,
    dry_run_flag,
    cost_ack_flag,
) = sys.argv[1:16]

from orchestrator.specialized.enabled import require_specialized_model_gate
from orchestrator.specialized.gpu import (
    evaluate_gpu,
    prepare_gpu_job,
    run_gpu_pipeline,
    submit_gpu_job,
)
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
cost_ack = cost_ack_flag == "1"
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

    if cmd == "lora":
        if phase == "prepare":
            prepared = prepare_dataset(
                repo_path,
                export_id=export_id.strip() or None,
                export_path=Path(export_path) if export_path.strip() else None,
                gold_path=Path(gold) if gold.strip() else None,
                external_blob_path=external_blob.strip() or None,
            )
            print(json.dumps(prepared, indent=2, sort_keys=True))
            sys.exit(0)
        if phase == "train":
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
        if phase == "evaluate":
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

    # gpu
    if phase == "prepare":
        if not dataset_path.strip():
            raise SpecializedModelServiceError("gpu prepare requires --dataset PATH")
        prepared = prepare_gpu_job(
            repo_path,
            dataset_path=Path(dataset_path),
            gold_path=Path(gold) if gold.strip() else None,
            adapter_root=adapter_root.strip() or None,
        )
        print(json.dumps(prepared, indent=2, sort_keys=True))
        sys.exit(0)
    if phase == "submit":
        if not job_path.strip():
            raise SpecializedModelServiceError("gpu submit requires --job PATH")
        result = submit_gpu_job(
            repo_path,
            job_path=Path(job_path),
            dry_run=dry_run,
            cost_ack=cost_ack,
            adapter_root=Path(adapter_root) if adapter_root.strip() else None,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        sys.exit(0)
    if phase == "evaluate":
        report = evaluate_gpu(
            repo_path,
            job_path=Path(job_path) if job_path.strip() else None,
            dataset_path=Path(dataset_path) if dataset_path.strip() else None,
            adapter_root=Path(adapter_root) if adapter_root.strip() else None,
            gold_path=Path(gold) if gold.strip() else None,
            dry_run=dry_run,
            cost_ack=cost_ack,
            evidence_dir=Path(evidence_dir) if evidence_dir.strip() else None,
            write_evidence=write_evidence,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        sys.exit(0 if report.get("overall_status") in {"pass", "warn"} else 1)
    if not dataset_path.strip():
        raise SpecializedModelServiceError("gpu pipeline requires --dataset PATH")
    report = run_gpu_pipeline(
        repo_path,
        dataset_path=Path(dataset_path),
        dry_run=dry_run,
        cost_ack=cost_ack,
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
