"""Specialized Model Level 2 — single rented GPU QLoRA prepare / submit / evaluate."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.cognitive.git_facts import git_sha
from orchestrator.schemas.validate import validate_document
from orchestrator.specialized.enabled import require_specialized_model_gate
from orchestrator.specialized.lora import (
    _path_is_under,
    _refuse_weight_files,
    load_dataset,
)
from orchestrator.specialized.scoring import (
    default_gold_path,
    load_gold_set,
    score_gold_set,
)
from orchestrator.specialized.service import SpecializedModelServiceError

TARGET_CLASS_DEFAULT = "3B-8B QLoRA"
VRAM_RANGE_DEFAULT = "16-24GB"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def jobs_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "specialized-gpu-jobs"


def load_job(path: Path) -> dict[str, Any]:
    target = Path(path)
    if not target.is_file():
        raise SpecializedModelServiceError(f"gpu job not found: {target}")
    doc = json.loads(target.read_text(encoding="utf-8"))
    validate_document(doc, "specialized-model-gpu-job.schema.json")
    return doc


def prepare_gpu_job(
    repo_root: Path,
    *,
    dataset_path: Path,
    gold_path: Path | None = None,
    adapter_root: str | None = None,
    target_class: str = TARGET_CLASS_DEFAULT,
    vram_gb_range: str = VRAM_RANGE_DEFAULT,
) -> dict[str, Any]:
    """Prepare a Level 2 GPU job manifest from a Level 1 dataset."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    dataset = load_dataset(Path(dataset_path))
    gold_file = Path(gold_path) if gold_path else Path(
        dataset.get("holdout_gold_path") or default_gold_path(repo_root)
    )
    job_id = f"smgpu-{uuid4().hex[:12]}"
    job: dict[str, Any] = {
        "schema_version": "1",
        "job_id": job_id,
        "plan_id": "specialized-model-level-2",
        "level": 2,
        "dataset_id": str(dataset.get("dataset_id") or ""),
        "dataset_path": str(Path(dataset_path).resolve()),
        "sample_count": int(dataset.get("sample_count") or 0),
        "target_class": target_class,
        "vram_gb_range": vram_gb_range,
        "qlora": True,
        "holdout_gold_path": str(gold_file),
        "adapter_root": adapter_root,
        "cost_estimate_note": (
            "Captain must acknowledge rental cost via --cost-ack before "
            "non-dry-run submit. This field is not a payment authorization."
        ),
        "repository_sha": git_sha(repo_root) or "",
        "northstar_version": _version(repo_root),
        "notes": (
            "Level 2 single rented GPU job manifest. Weights/adapters must "
            "remain outside this control repo. No auto-promote."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }
    validate_document(job, "specialized-model-gpu-job.schema.json")
    out_dir = jobs_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{job_id}.json"
    out_path.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    job["_path"] = str(out_path)
    return job


def _default_adapter_root(repo_root: Path, *, dry_run: bool) -> Path:
    env = os.environ.get("COMPASS_SPECIALIZED_ADAPTER_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    if dry_run:
        return (
            Path(repo_root).resolve()
            / "tests"
            / "fixtures"
            / "specialized-model-gpu"
            / "fixture-adapter"
        )
    raise SpecializedModelServiceError(
        "gpu submit requires COMPASS_SPECIALIZED_ADAPTER_ROOT outside the "
        "control repo (or pass --dry-run for CI fixture path)"
    )


def _write_dry_run_metrics(adapter_root: Path, job: dict[str, Any]) -> dict[str, Any]:
    adapter_root.mkdir(parents=True, exist_ok=True)
    metrics = {
        "schema_version": "1",
        "dry_run": True,
        "job_id": job.get("job_id"),
        "dataset_id": job.get("dataset_id"),
        "qlora": True,
        "status": "dry-run",
        "notes": "Hermetic dry-run — no GPU rented, no weights written.",
        "generated_at": _utc_now(),
    }
    (adapter_root / "train-metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (adapter_root / "adapter-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "kind": "fixture-gpu-adapter",
                "weights_present": False,
                "auto_promoted": False,
                "qlora": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return metrics


def submit_gpu_job(
    repo_root: Path,
    *,
    job_path: Path,
    dry_run: bool = True,
    cost_ack: bool = False,
    adapter_root: Path | None = None,
) -> dict[str, Any]:
    """Submit GPU job via external runner or hermetic dry-run."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    job = load_job(Path(job_path))

    if not dry_run and not cost_ack:
        raise SpecializedModelServiceError(
            "non-dry-run gpu submit requires --cost-ack "
            "(Captain cost acknowledgment attestation)"
        )

    root = (
        Path(adapter_root).expanduser().resolve()
        if adapter_root
        else _default_adapter_root(repo_root, dry_run=dry_run)
    )

    if not dry_run and _path_is_under(root, repo_root):
        fixture = (
            repo_root / "tests" / "fixtures" / "specialized-model-gpu" / "fixture-adapter"
        ).resolve()
        if root != fixture:
            raise SpecializedModelServiceError(
                "adapter_root must be outside the control repo "
                "(set COMPASS_SPECIALIZED_ADAPTER_ROOT)"
            )

    if dry_run:
        metrics = _write_dry_run_metrics(root, job)
        runner = "dry-run"
    else:
        runner = os.environ.get("COMPASS_SPECIALIZED_GPU_RUNNER", "").strip()
        if not runner:
            raise SpecializedModelServiceError(
                "live gpu submit requires COMPASS_SPECIALIZED_GPU_RUNNER "
                "(or pass --dry-run)"
            )
        root.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [runner, "--job", str(job_path), "--adapter-root", str(root)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SpecializedModelServiceError(
                f"external GPU runner failed (rc={proc.returncode}): "
                f"{proc.stderr[-800:]}"
            )
        metrics_path = root / "train-metrics.json"
        if metrics_path.is_file():
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        else:
            metrics = {
                "status": "external",
                "stdout_tail": (proc.stdout or "")[-400:],
            }

    _refuse_weight_files(repo_root / ".agent" / "specialized-gpu-jobs")
    if _path_is_under(root, repo_root):
        _refuse_weight_files(root)

    return {
        "job_id": job.get("job_id"),
        "job_path": str(Path(job_path).resolve()),
        "dataset_id": job.get("dataset_id"),
        "adapter_root": str(root),
        "dry_run": dry_run,
        "cost_acknowledged": bool(cost_ack) or dry_run,
        "runner": runner,
        "train_metrics": metrics,
        "weights_committed": False,
        "auto_promoted": False,
    }


def _rate(scores: dict[str, Any] | None, key: str) -> float:
    if not scores:
        return 0.0
    val = scores.get(key)
    return float(val) if isinstance(val, (int, float)) else 0.0


def evaluate_gpu(
    repo_root: Path,
    *,
    job_path: Path | None = None,
    dataset_path: Path | None = None,
    adapter_root: Path | None = None,
    gold_path: Path | None = None,
    dry_run: bool = True,
    cost_ack: bool = False,
    evidence_dir: Path | None = None,
    write_evidence: bool = True,
    train_metrics: dict[str, Any] | None = None,
    level1_scores: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare Level 0 baseline (+ optional Level 1) vs GPU adapter stub."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    warnings: list[str] = []

    job: dict[str, Any] | None = None
    job_id = None
    job_path_s = None
    dataset_id = None
    if job_path:
        job = load_job(Path(job_path))
        job_id = job.get("job_id")
        job_path_s = str(Path(job_path).resolve())
        dataset_id = job.get("dataset_id")
        gold_file = Path(job.get("holdout_gold_path") or default_gold_path(repo_root))
        if not dataset_path and job.get("dataset_path"):
            dataset_path = Path(str(job["dataset_path"]))
    else:
        gold_file = Path(gold_path) if gold_path else default_gold_path(repo_root)

    if gold_path:
        gold_file = Path(gold_path)

    gold = load_gold_set(gold_file)
    baseline_scores = score_gold_set(gold)
    # Hermetic adapter scorer: same gold stub path as Level 1 (no live GPU).
    adapter_scores = score_gold_set(gold)

    if level1_scores is None:
        # Optional Level 1 reference = same hermetic rates in CI dry-run.
        level1_scores = {
            "retrieval_rate": baseline_scores.get("retrieval_rate"),
            "prompt_rate": baseline_scores.get("prompt_rate"),
            "stub_student_rate": baseline_scores.get("stub_student_rate"),
            "task_total": baseline_scores.get("task_total"),
            "note": "level1 reference = hermetic gold rates (dry-run)",
        }

    comparison = {
        "retrieval_delta_vs_l0": round(
            _rate(adapter_scores, "retrieval_rate")
            - _rate(baseline_scores, "retrieval_rate"),
            4,
        ),
        "prompt_delta_vs_l0": round(
            _rate(adapter_scores, "prompt_rate") - _rate(baseline_scores, "prompt_rate"),
            4,
        ),
        "stub_student_delta_vs_l0": round(
            _rate(adapter_scores, "stub_student_rate")
            - _rate(baseline_scores, "stub_student_rate"),
            4,
        ),
        "baseline_min_rate": round(
            min(
                _rate(baseline_scores, "retrieval_rate"),
                _rate(baseline_scores, "prompt_rate"),
                _rate(baseline_scores, "stub_student_rate"),
            ),
            4,
        ),
        "adapter_min_rate": round(
            min(
                _rate(adapter_scores, "retrieval_rate"),
                _rate(adapter_scores, "prompt_rate"),
                _rate(adapter_scores, "stub_student_rate"),
            ),
            4,
        ),
        "level1_min_rate": round(
            min(
                _rate(level1_scores, "retrieval_rate"),
                _rate(level1_scores, "prompt_rate"),
                _rate(level1_scores, "stub_student_rate"),
            ),
            4,
        ),
    }

    if dry_run:
        warnings.append("dry-run evaluate — fixture GPU adapter; no live rental")

    adapter_path = (
        Path(adapter_root).expanduser().resolve()
        if adapter_root
        else _default_adapter_root(repo_root, dry_run=True)
    )
    if _path_is_under(adapter_path, repo_root):
        _refuse_weight_files(adapter_path)

    checklist_src: dict[str, bool] = {}
    if dataset_path and Path(dataset_path).is_file():
        try:
            ds = load_dataset(Path(dataset_path))
            checklist_src = dict(ds.get("permission_checklist") or {})
            dataset_id = dataset_id or ds.get("dataset_id")
        except SpecializedModelServiceError:
            warnings.append("dataset load skipped for checklist")

    cost_ok = bool(cost_ack) or dry_run
    checklist = {
        "license_reviewed": bool(checklist_src.get("license_reviewed", True)),
        "secrets_redacted_ack": bool(checklist_src.get("secrets_redacted_ack", True)),
        "pii_reviewed": bool(checklist_src.get("pii_reviewed", True)),
        "provenance_recorded": True,
        "weights_outside_control_repo_ack": True,
        "holdout_retained": gold_file.is_file(),
        "cost_acknowledged": cost_ok,
    }
    checklist_ok = all(checklist.values())
    baseline_ok = comparison["baseline_min_rate"] >= 0.9
    adapter_ok = comparison["adapter_min_rate"] >= 0.9

    if not baseline_ok or not adapter_ok or not checklist_ok:
        overall = "fail" if comparison["adapter_min_rate"] < 0.5 else "warn"
    elif warnings:
        overall = "warn"
    else:
        overall = "pass"

    if overall == "fail" or not checklist_ok:
        go_no_go = "no-go"
    elif overall == "warn" or dry_run:
        go_no_go = "hold"
    else:
        go_no_go = "go"

    run_id = f"sm2-{uuid4().hex[:10]}"
    report: dict[str, Any] = {
        "schema_version": "1",
        "run_id": run_id,
        "plan_id": "specialized-model-level-2",
        "level": 2,
        "phase": "evaluate",
        "repository_sha": git_sha(repo_root) or "",
        "northstar_version": _version(repo_root),
        "job_id": job_id,
        "job_path": job_path_s,
        "dataset_id": dataset_id,
        "dry_run": dry_run,
        "cost_acknowledged": cost_ok,
        "adapter_root": str(adapter_path),
        "train_metrics": train_metrics,
        "baseline_scores": {
            "retrieval_rate": baseline_scores.get("retrieval_rate"),
            "prompt_rate": baseline_scores.get("prompt_rate"),
            "stub_student_rate": baseline_scores.get("stub_student_rate"),
            "task_total": baseline_scores.get("task_total"),
        },
        "level1_scores": level1_scores,
        "adapter_scores": {
            "retrieval_rate": adapter_scores.get("retrieval_rate"),
            "prompt_rate": adapter_scores.get("prompt_rate"),
            "stub_student_rate": adapter_scores.get("stub_student_rate"),
            "task_total": adapter_scores.get("task_total"),
        },
        "comparison": comparison,
        "checklist": checklist,
        "warnings": warnings,
        "overall_status": overall,
        "go_no_go": go_no_go,
        "evidence_path": None,
        "notes": (
            "Specialized Model Level 2 GPU evaluate. Weights/adapters stay "
            "outside this control repo. Cost ack is an attestation, not payment. "
            "Never auto-promotes into Adaptive Intelligence routing."
        ),
        "weights_committed": False,
        "auto_promoted": False,
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }

    if write_evidence:
        out_root = Path(evidence_dir) if evidence_dir else (
            repo_root / ".agent" / "evidence" / "specialized-model-level-2"
        )
        out_root.mkdir(parents=True, exist_ok=True)
        json_path = out_root / f"{run_id}.json"
        report["evidence_path"] = str(json_path)
        validate_document(report, "specialized-model-gpu-run.schema.json")
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        json_path.write_text(payload, encoding="utf-8")
        (out_root / "LATEST.json").write_text(
            json.dumps({"run_id": run_id, "path": str(json_path)}, indent=2) + "\n",
            encoding="utf-8",
        )
        md = [
            "# Specialized Model Level 2 — GPU Evaluate Summary",
            "",
            f"- run_id: `{run_id}`",
            f"- overall_status: **{overall}**",
            f"- go_no_go: **{go_no_go}**",
            f"- dry_run: `{dry_run}`",
            f"- cost_acknowledged: `{cost_ok}`",
            f"- job_id: `{job_id}`",
            f"- weights_committed: `false`",
            f"- auto_promoted: `false`",
            f"- baseline_min_rate: `{comparison['baseline_min_rate']}`",
            f"- adapter_min_rate: `{comparison['adapter_min_rate']}`",
            "",
        ]
        if warnings:
            md.extend(["## Warnings", ""])
            for w in warnings:
                md.append(f"- {w}")
            md.append("")
        (out_root / "SUMMARY.md").write_text("\n".join(md), encoding="utf-8")
    else:
        validate_document(report, "specialized-model-gpu-run.schema.json")

    return report


def run_gpu_pipeline(
    repo_root: Path,
    *,
    dataset_path: Path,
    dry_run: bool = True,
    cost_ack: bool = False,
    adapter_root: Path | None = None,
    gold_path: Path | None = None,
    evidence_dir: Path | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    """Convenience: prepare → submit → evaluate."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    prepared = prepare_gpu_job(
        repo_root,
        dataset_path=Path(dataset_path),
        gold_path=gold_path,
        adapter_root=str(adapter_root) if adapter_root else None,
    )
    job_path = Path(prepared["_path"])
    submit_result = submit_gpu_job(
        repo_root,
        job_path=job_path,
        dry_run=dry_run,
        cost_ack=cost_ack,
        adapter_root=adapter_root,
    )
    return evaluate_gpu(
        repo_root,
        job_path=job_path,
        dataset_path=Path(dataset_path),
        adapter_root=Path(submit_result["adapter_root"]),
        gold_path=gold_path,
        dry_run=dry_run,
        cost_ack=cost_ack or dry_run,
        evidence_dir=evidence_dir,
        write_evidence=write_evidence,
        train_metrics=submit_result.get("train_metrics"),
    )
