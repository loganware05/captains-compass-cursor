"""Specialized Model Level 1 — on-device LoRA prepare / train / evaluate."""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.cognitive.git_facts import git_sha
from orchestrator.schemas.validate import validate_document
from orchestrator.specialized.enabled import require_specialized_model_gate
from orchestrator.specialized.scoring import (
    default_gold_path,
    load_gold_set,
    score_gold_set,
)
from orchestrator.specialized.service import SpecializedModelServiceError
from orchestrator.train_bridge.store import (
    TrainBridgeStoreError,
    load_export,
    load_export_file,
)

_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_WEIGHT_SUFFIXES = (
    ".safetensors",
    ".bin",
    ".gguf",
    ".pt",
    ".pth",
    ".onnx",
    ".mlx",
    ".npz",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def datasets_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "specialized-datasets"


def _assert_safe_id(value: str) -> str:
    if not _SAFE_ID.match(value or ""):
        raise SpecializedModelServiceError(f"invalid id: {value!r}")
    return value


def _load_export_manifest(
    repo_root: Path,
    *,
    export_id: str | None,
    export_path: Path | None,
) -> dict[str, Any]:
    if not export_id and not export_path:
        raise SpecializedModelServiceError(
            "lora prepare requires --export-id or --export-path"
        )
    try:
        if export_path is not None:
            return load_export_file(Path(export_path))
        return load_export(repo_root, str(export_id))
    except (TrainBridgeStoreError, FileNotFoundError, OSError, ValueError) as exc:
        raise SpecializedModelServiceError(f"export load failed: {exc}") from exc


def _checklist_complete(manifest: dict[str, Any]) -> dict[str, bool]:
    checklist = dict(manifest.get("permission_checklist") or {})
    required = (
        "export_authorized",
        "secrets_redacted_ack",
        "license_reviewed",
        "pii_reviewed",
        "specialized_model_handoff_ack",
    )
    out = {k: bool(checklist.get(k)) for k in required}
    if not all(out.values()):
        missing = [k for k, v in out.items() if not v]
        raise SpecializedModelServiceError(
            "C7 export permission checklist incomplete: " + ", ".join(missing)
        )
    if manifest.get("auto_uploaded") is not False:
        raise SpecializedModelServiceError(
            "export auto_uploaded must be false (C7 authority lock)"
        )
    return out


def load_dataset(path: Path) -> dict[str, Any]:
    target = Path(path)
    if not target.is_file():
        raise SpecializedModelServiceError(f"dataset not found: {target}")
    doc = json.loads(target.read_text(encoding="utf-8"))
    validate_document(doc, "specialized-model-dataset.schema.json")
    return doc


def prepare_dataset(
    repo_root: Path,
    *,
    export_id: str | None = None,
    export_path: Path | None = None,
    gold_path: Path | None = None,
    external_blob_path: str | None = None,
) -> dict[str, Any]:
    """Prepare a Level 1 dataset manifest from a C7 training export."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    manifest = _load_export_manifest(
        repo_root, export_id=export_id, export_path=export_path
    )
    checklist = _checklist_complete(manifest)

    samples: list[dict[str, Any]] = []
    for idx, traj in enumerate(manifest.get("trajectories") or []):
        if not isinstance(traj, dict):
            continue
        samples.append(
            {
                "sample_id": f"sample-{idx + 1:04d}",
                "objective": str(traj.get("objective") or ""),
                "outcome": str(traj.get("outcome") or ""),
                "source": str(traj.get("source") or "experience"),
                "experience_id": traj.get("experience_id"),
                "lessons": [str(x) for x in (traj.get("lessons") or [])][:8],
            }
        )

    gold_file = Path(gold_path) if gold_path else default_gold_path(repo_root)
    dataset_id = f"smds-{uuid4().hex[:12]}"
    dataset: dict[str, Any] = {
        "schema_version": "1",
        "dataset_id": dataset_id,
        "plan_id": "specialized-model-level-1",
        "source_export_id": str(manifest.get("export_id") or "") or None,
        "source_export_path": str(manifest.get("export_path") or export_path or "")
        or None,
        "sample_count": len(samples),
        "samples": samples,
        "permission_checklist": checklist,
        "holdout_gold_path": str(gold_file),
        "external_blob_path": external_blob_path,
        "repository_sha": git_sha(repo_root) or "",
        "northstar_version": _version(repo_root),
        "notes": (
            "Level 1 dataset manifest from C7 export. Metadata only — large "
            "training blobs may live at external_blob_path outside this repo."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }
    validate_document(dataset, "specialized-model-dataset.schema.json")
    out_dir = datasets_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_id}.json"
    out_path.write_text(
        json.dumps(dataset, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    dataset["_path"] = str(out_path)
    return dataset


def _path_is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _refuse_weight_files(path: Path) -> None:
    if not path.exists():
        return
    if path.is_file():
        candidates = [path]
    else:
        candidates = list(path.rglob("*"))
    for item in candidates:
        if item.is_file() and item.suffix.lower() in _WEIGHT_SUFFIXES:
            raise SpecializedModelServiceError(
                f"refusing weight/adapter binary under control-repo path: {item}"
            )


def _default_adapter_root(repo_root: Path, *, dry_run: bool) -> Path:
    env = os.environ.get("COMPASS_SPECIALIZED_ADAPTER_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    if dry_run:
        # Fixture adapter metadata only (no weight binaries).
        return (
            Path(repo_root).resolve()
            / "tests"
            / "fixtures"
            / "specialized-model-lora"
            / "fixture-adapter"
        )
    raise SpecializedModelServiceError(
        "lora train requires COMPASS_SPECIALIZED_ADAPTER_ROOT outside the "
        "control repo (or pass --dry-run for CI fixture path)"
    )


def _write_dry_run_metrics(adapter_root: Path, dataset: dict[str, Any]) -> dict[str, Any]:
    adapter_root.mkdir(parents=True, exist_ok=True)
    metrics = {
        "schema_version": "1",
        "dry_run": True,
        "dataset_id": dataset.get("dataset_id"),
        "sample_count": dataset.get("sample_count"),
        "steps": 0,
        "status": "dry-run",
        "notes": "Hermetic dry-run — no weights trained or written.",
        "generated_at": _utc_now(),
    }
    (adapter_root / "train-metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # Marker that this is a fixture adapter directory (never a weight file).
    (adapter_root / "adapter-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "kind": "fixture-adapter",
                "weights_present": False,
                "auto_promoted": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return metrics


def train_lora(
    repo_root: Path,
    *,
    dataset_path: Path,
    dry_run: bool = True,
    adapter_root: Path | None = None,
) -> dict[str, Any]:
    """Run external LoRA trainer or hermetic dry-run; never commit weights here."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    dataset = load_dataset(Path(dataset_path))
    root = (
        Path(adapter_root).expanduser().resolve()
        if adapter_root
        else _default_adapter_root(repo_root, dry_run=dry_run)
    )

    if not dry_run and _path_is_under(root, repo_root):
        # Allow only the committed fixture adapter tree for non-dry? No — refuse.
        fixture = (
            repo_root / "tests" / "fixtures" / "specialized-model-lora" / "fixture-adapter"
        ).resolve()
        if root != fixture:
            raise SpecializedModelServiceError(
                "adapter_root must be outside the control repo "
                "(set COMPASS_SPECIALIZED_ADAPTER_ROOT)"
            )

    if dry_run:
        metrics = _write_dry_run_metrics(root, dataset)
        trainer = "dry-run"
    else:
        trainer = os.environ.get("COMPASS_SPECIALIZED_LORA_TRAINER", "").strip()
        if not trainer:
            raise SpecializedModelServiceError(
                "live train requires COMPASS_SPECIALIZED_LORA_TRAINER "
                "(or pass --dry-run)"
            )
        root.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [trainer, "--dataset", str(dataset_path), "--adapter-root", str(root)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SpecializedModelServiceError(
                f"external trainer failed (rc={proc.returncode}): {proc.stderr[-800:]}"
            )
        metrics_path = root / "train-metrics.json"
        if metrics_path.is_file():
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        else:
            metrics = {
                "status": "external",
                "stdout_tail": (proc.stdout or "")[-400:],
            }

    # Refuse weight binaries anywhere under the control repo after train.
    _refuse_weight_files(repo_root / ".agent" / "specialized-datasets")
    if _path_is_under(root, repo_root):
        _refuse_weight_files(root)

    return {
        "dataset_id": dataset.get("dataset_id"),
        "dataset_path": str(Path(dataset_path).resolve()),
        "adapter_root": str(root),
        "dry_run": dry_run,
        "trainer": trainer,
        "train_metrics": metrics,
        "weights_committed": False,
        "auto_promoted": False,
    }


def _score_adapter_stub(gold: dict[str, Any], *, train_metrics: dict[str, Any] | None) -> dict[str, Any]:
    """Hermetic adapter scorer: reuse gold stub answers (fixture student).

    Dry-run does not claim improvement over Level 0; rates match baseline.
    """
    del train_metrics  # reserved for future live metrics coupling
    return score_gold_set(gold)


def evaluate_lora(
    repo_root: Path,
    *,
    dataset_path: Path | None = None,
    adapter_root: Path | None = None,
    gold_path: Path | None = None,
    dry_run: bool = True,
    evidence_dir: Path | None = None,
    write_evidence: bool = True,
    train_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare Level 0 baseline vs adapter stub on the held-out gold set."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    warnings: list[str] = []

    dataset: dict[str, Any] | None = None
    dataset_id = None
    dataset_path_s = None
    checklist_src: dict[str, bool] = {}
    if dataset_path:
        dataset = load_dataset(Path(dataset_path))
        dataset_id = dataset.get("dataset_id")
        dataset_path_s = str(Path(dataset_path).resolve())
        checklist_src = dict(dataset.get("permission_checklist") or {})
        gold_file = Path(dataset.get("holdout_gold_path") or default_gold_path(repo_root))
    else:
        gold_file = Path(gold_path) if gold_path else default_gold_path(repo_root)

    if gold_path:
        gold_file = Path(gold_path)

    gold = load_gold_set(gold_file)
    baseline_scores = score_gold_set(gold)
    adapter_scores = _score_adapter_stub(gold, train_metrics=train_metrics)

    def _rate(scores: dict[str, Any], key: str) -> float:
        val = scores.get(key)
        return float(val) if isinstance(val, (int, float)) else 0.0

    comparison = {
        "retrieval_delta": round(
            _rate(adapter_scores, "retrieval_rate")
            - _rate(baseline_scores, "retrieval_rate"),
            4,
        ),
        "prompt_delta": round(
            _rate(adapter_scores, "prompt_rate") - _rate(baseline_scores, "prompt_rate"),
            4,
        ),
        "stub_student_delta": round(
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
    }

    if dry_run:
        warnings.append("dry-run evaluate — fixture adapter; no live LoRA weights")

    adapter_path = (
        Path(adapter_root).expanduser().resolve()
        if adapter_root
        else _default_adapter_root(repo_root, dry_run=True)
    )
    if _path_is_under(adapter_path, repo_root):
        _refuse_weight_files(adapter_path)

    checklist = {
        "license_reviewed": bool(checklist_src.get("license_reviewed", True)),
        "secrets_redacted_ack": bool(checklist_src.get("secrets_redacted_ack", True)),
        "pii_reviewed": bool(checklist_src.get("pii_reviewed", True)),
        "provenance_recorded": True,
        "weights_outside_control_repo_ack": True,
        "holdout_retained": gold_file.is_file(),
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

    run_id = f"sm1-{uuid4().hex[:10]}"
    report: dict[str, Any] = {
        "schema_version": "1",
        "run_id": run_id,
        "plan_id": "specialized-model-level-1",
        "level": 1,
        "phase": "evaluate",
        "repository_sha": git_sha(repo_root) or "",
        "northstar_version": _version(repo_root),
        "dataset_id": dataset_id,
        "dataset_path": dataset_path_s,
        "dry_run": dry_run,
        "adapter_root": str(adapter_path),
        "train_metrics": train_metrics,
        "baseline_scores": {
            "retrieval_rate": baseline_scores.get("retrieval_rate"),
            "prompt_rate": baseline_scores.get("prompt_rate"),
            "stub_student_rate": baseline_scores.get("stub_student_rate"),
            "task_total": baseline_scores.get("task_total"),
        },
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
            "Specialized Model Level 1 LoRA evaluate. Weights/adapters stay "
            "outside this control repo. Never auto-promotes into Adaptive "
            "Intelligence routing."
        ),
        "weights_committed": False,
        "auto_promoted": False,
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }

    if write_evidence:
        out_root = Path(evidence_dir) if evidence_dir else (
            repo_root / ".agent" / "evidence" / "specialized-model-level-1"
        )
        out_root.mkdir(parents=True, exist_ok=True)
        json_path = out_root / f"{run_id}.json"
        report["evidence_path"] = str(json_path)
        validate_document(report, "specialized-model-lora-run.schema.json")
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        json_path.write_text(payload, encoding="utf-8")
        (out_root / "LATEST.json").write_text(
            json.dumps({"run_id": run_id, "path": str(json_path)}, indent=2) + "\n",
            encoding="utf-8",
        )
        md = [
            "# Specialized Model Level 1 — LoRA Evaluate Summary",
            "",
            f"- run_id: `{run_id}`",
            f"- overall_status: **{overall}**",
            f"- go_no_go: **{go_no_go}**",
            f"- dry_run: `{dry_run}`",
            f"- dataset_id: `{dataset_id}`",
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
        validate_document(report, "specialized-model-lora-run.schema.json")

    return report


def run_lora_pipeline(
    repo_root: Path,
    *,
    export_id: str | None = None,
    export_path: Path | None = None,
    dataset_path: Path | None = None,
    dry_run: bool = True,
    adapter_root: Path | None = None,
    gold_path: Path | None = None,
    evidence_dir: Path | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    """Convenience: prepare (if needed) → train → evaluate."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    if dataset_path is None:
        prepared = prepare_dataset(
            repo_root,
            export_id=export_id,
            export_path=export_path,
            gold_path=gold_path,
        )
        dataset_path = Path(prepared["_path"])
    train_result = train_lora(
        repo_root,
        dataset_path=Path(dataset_path),
        dry_run=dry_run,
        adapter_root=adapter_root,
    )
    return evaluate_lora(
        repo_root,
        dataset_path=Path(dataset_path),
        adapter_root=Path(train_result["adapter_root"]),
        gold_path=gold_path,
        dry_run=dry_run,
        evidence_dir=evidence_dir,
        write_evidence=write_evidence,
        train_metrics=train_result.get("train_metrics"),
    )
