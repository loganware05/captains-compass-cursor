"""Specialized Model Level 0 — gated local baseline (no fine-tuning)."""

from __future__ import annotations

import json
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
from orchestrator.train_bridge.store import (
    TrainBridgeStoreError,
    load_export,
    load_export_file,
)


class SpecializedModelServiceError(ValueError):
    """Operator-facing Specialized Model Level 0 errors."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _attach_export(
    repo_root: Path,
    *,
    export_id: str | None,
    export_path: Path | None,
) -> dict[str, Any]:
    empty = {
        "attached": False,
        "export_id": None,
        "export_path": None,
        "trajectory_count": None,
        "checklist_complete": False,
        "auto_uploaded": False,
    }
    if not export_id and not export_path:
        return empty
    try:
        if export_path is not None:
            manifest = load_export_file(Path(export_path))
        else:
            manifest = load_export(repo_root, str(export_id))
    except (TrainBridgeStoreError, FileNotFoundError, OSError, ValueError) as exc:
        raise SpecializedModelServiceError(f"export attach failed: {exc}") from exc

    checklist = manifest.get("permission_checklist") or {}
    required = (
        "export_authorized",
        "secrets_redacted_ack",
        "license_reviewed",
        "pii_reviewed",
        "specialized_model_handoff_ack",
    )
    complete = all(bool(checklist.get(k)) for k in required)
    if manifest.get("auto_uploaded") is not False:
        raise SpecializedModelServiceError(
            "export auto_uploaded must be false (C7 authority lock)"
        )
    return {
        "attached": True,
        "export_id": str(manifest.get("export_id") or "") or None,
        "export_path": str(manifest.get("export_path") or export_path or "") or None,
        "trajectory_count": int(manifest.get("trajectory_count") or 0),
        "checklist_complete": complete,
        "auto_uploaded": False,
    }


def _checklist_from_export(export_attach: dict[str, Any], *, gold_ok: bool) -> dict[str, bool]:
    # Level 0 always attests weights stay outside the control repo.
    attached = bool(export_attach.get("attached"))
    complete = bool(export_attach.get("checklist_complete"))
    return {
        "license_reviewed": complete if attached else True,
        "secrets_redacted_ack": complete if attached else True,
        "pii_reviewed": complete if attached else True,
        "provenance_recorded": gold_ok and (complete if attached else True),
        "weights_outside_control_repo_ack": True,
    }


def run_baseline(
    repo_root: Path,
    *,
    gold_path: Path | None = None,
    export_id: str | None = None,
    export_path: Path | None = None,
    evidence_dir: Path | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    """Run gated Level 0 baseline and return a schema-validated report."""
    require_specialized_model_gate()
    repo_root = Path(repo_root).resolve()
    warnings: list[str] = []

    gold_file = Path(gold_path) if gold_path else default_gold_path(repo_root)
    try:
        gold = load_gold_set(gold_file)
    except (OSError, ValueError) as exc:
        raise SpecializedModelServiceError(str(exc)) from exc

    scores = score_gold_set(gold)
    if scores.get("misses"):
        warnings.append(
            "gold misses: " + ", ".join(scores["misses"][:8])
        )

    export_attach = _attach_export(
        repo_root, export_id=export_id, export_path=export_path
    )
    if export_attach["attached"] and not export_attach["checklist_complete"]:
        warnings.append("C7 export permission checklist incomplete")

    total = int(scores["task_total"] or 0)
    rates = [
        scores.get("retrieval_rate"),
        scores.get("prompt_rate"),
        scores.get("stub_student_rate"),
    ]
    rates_ok = [r for r in rates if isinstance(r, (int, float))]
    min_rate = min(rates_ok) if rates_ok else 0.0
    gold_ok = total > 0 and min_rate >= 0.9

    checklist = _checklist_from_export(export_attach, gold_ok=gold_ok)
    checklist_ok = all(checklist.values())

    if not gold_ok:
        overall = "fail" if min_rate < 0.5 else "warn"
    elif warnings:
        overall = "warn"
    else:
        overall = "pass"

    if overall == "fail" or not checklist_ok:
        go_no_go = "no-go"
    elif overall == "warn":
        go_no_go = "hold"
    else:
        go_no_go = "go"

    report_id = f"sm0-{uuid4().hex[:10]}"
    head = git_sha(repo_root) or ""
    version = _version(repo_root)

    report: dict[str, Any] = {
        "schema_version": "1",
        "report_id": report_id,
        "plan_id": "specialized-model-level-0",
        "level": 0,
        "repository_sha": head,
        "northstar_version": version,
        "gold_set_path": str(gold_file),
        "gold_task_count": total,
        "scores": {
            "retrieval_rate": scores.get("retrieval_rate"),
            "prompt_rate": scores.get("prompt_rate"),
            "stub_student_rate": scores.get("stub_student_rate"),
            "retrieval_passed": scores.get("retrieval_passed"),
            "prompt_passed": scores.get("prompt_passed"),
            "stub_student_passed": scores.get("stub_student_passed"),
            "task_total": total,
        },
        "export_attach": export_attach,
        "checklist": checklist,
        "warnings": warnings,
        "overall_status": overall,
        "go_no_go": go_no_go,
        "evidence_path": None,
        "notes": (
            "Specialized Model Level 0 local baseline. No fine-tuning, no weight "
            "training, no auto-upload. Weights/adapters stay outside this control "
            "repo. Promote to Level 1 only after Captain review of go/no-go."
        ),
        "weights_trained": False,
        "auto_uploaded": False,
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }

    if write_evidence:
        out_root = Path(evidence_dir) if evidence_dir else (
            repo_root / ".agent" / "evidence" / "specialized-model-level-0"
        )
        out_root.mkdir(parents=True, exist_ok=True)
        json_path = out_root / f"{report_id}.json"
        report["evidence_path"] = str(json_path)
        validate_document(report, "specialized-model-baseline-report.schema.json")
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        json_path.write_text(payload, encoding="utf-8")
        (out_root / "LATEST.json").write_text(
            json.dumps({"report_id": report_id, "path": str(json_path)}, indent=2)
            + "\n",
            encoding="utf-8",
        )
        md_lines = [
            "# Specialized Model Level 0 — Baseline Summary",
            "",
            f"- report_id: `{report_id}`",
            f"- overall_status: **{overall}**",
            f"- go_no_go: **{go_no_go}**",
            f"- gold_task_count: `{total}`",
            f"- retrieval_rate: `{scores.get('retrieval_rate')}`",
            f"- prompt_rate: `{scores.get('prompt_rate')}`",
            f"- stub_student_rate: `{scores.get('stub_student_rate')}`",
            f"- weights_trained: `false`",
            f"- auto_uploaded: `false`",
            f"- export_attached: `{export_attach.get('attached')}`",
            "",
        ]
        if warnings:
            md_lines.extend(["## Warnings", ""])
            for w in warnings:
                md_lines.append(f"- {w}")
            md_lines.append("")
        (out_root / "SUMMARY.md").write_text("\n".join(md_lines), encoding="utf-8")
    else:
        validate_document(report, "specialized-model-baseline-report.schema.json")

    return report
