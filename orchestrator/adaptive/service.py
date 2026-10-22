"""N3 Adaptive Intelligence scorecard service (proposal-only)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.adaptive.enabled import require_adaptive_intel_gate
from orchestrator.adaptive.metrics import collect_metrics, level3_recommendation
from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA = "adaptive-intelligence-scorecard.schema.json"
SCHEMA_VERSION = "1"


class AdaptiveServiceError(ValueError):
    """Operator-facing adaptive intelligence errors."""


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _version(repo_root: Path) -> str:
    path = Path(repo_root) / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _git_sha(repo_root: Path) -> str:
    head = Path(repo_root) / ".git" / "HEAD"
    if not head.is_file():
        return ""
    try:
        raw = head.read_text(encoding="utf-8").strip()
        if raw.startswith("ref:"):
            ref = raw.split(" ", 1)[1].strip()
            ref_path = Path(repo_root) / ".git" / ref
            if ref_path.is_file():
                return ref_path.read_text(encoding="utf-8").strip()[:40]
        return raw[:40]
    except OSError:
        return ""


def _evidence_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "n3-adaptive-intelligence-validation"


def _report_id(phase: str) -> str:
    digest = hashlib.sha256(f"{phase}|{_utc_now()}|{uuid4().hex}".encode()).hexdigest()[
        :12
    ]
    return f"adaptive-{phase}-{digest}"


def _build_phase_report(
    repo_root: Path,
    *,
    phase: str,
    with_evidence: bool,
) -> dict[str, Any]:
    metrics = collect_metrics(repo_root, with_evidence=with_evidence)
    recommendation, rationale = level3_recommendation(metrics)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "report_id": _report_id(phase),
        "plan_id": "n3-adaptive-intelligence-validation",
        "created_at": _utc_now(),
        "phase": phase,
        "repository_sha": _git_sha(repo_root),
        "northstar_version": _version(repo_root),
        "metrics": metrics,
        "deltas": None,
        "baseline_report_id": None,
        "evidence_report_id": None,
        "level3_recommendation": recommendation,
        "level3_rationale": rationale,
        "warnings": [],
        "evidence_path": None,
        "notes": (
            "N3 Adaptive Intelligence Validation scorecard. Hermetic metrics only. "
            "Does not apply routing weights, promote Skills/policies, or authorize "
            "Level 3 GPU spend."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_applied": False,
    }
    # schema forbids null deltas on some drafts — omit until compare
    report.pop("deltas")
    try:
        validate_document(report, SCHEMA)
    except ValidationError as exc:
        raise AdaptiveServiceError(f"scorecard schema validation failed: {exc}") from exc
    return report


def _persist(repo_root: Path, report: dict[str, Any]) -> dict[str, Any]:
    out_dir = _evidence_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{report['report_id']}.json"
    latest = out_dir / f"LATEST_{report['phase']}.json"
    payload = dict(report)
    payload["evidence_path"] = str(path)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    latest.write_text(text, encoding="utf-8")
    validate_document(payload, SCHEMA)
    return payload


def run_scorecard(
    repo_root: Path,
    *,
    phase: str = "compare",
    persist: bool = True,
) -> dict[str, Any]:
    """Run baseline, with_evidence, or compare scorecard phases."""
    require_adaptive_intel_gate()
    repo_root = Path(repo_root).resolve()
    phase = (phase or "compare").strip().lower()
    if phase not in {"baseline", "with_evidence", "compare"}:
        raise AdaptiveServiceError("--phase must be baseline|with_evidence|compare")

    if phase == "baseline":
        report = _build_phase_report(repo_root, phase="baseline", with_evidence=False)
        return _persist(repo_root, report) if persist else report

    if phase == "with_evidence":
        report = _build_phase_report(
            repo_root, phase="with_evidence", with_evidence=True
        )
        return _persist(repo_root, report) if persist else report

    # compare
    baseline = _build_phase_report(repo_root, phase="baseline", with_evidence=False)
    evidence = _build_phase_report(
        repo_root, phase="with_evidence", with_evidence=True
    )
    if persist:
        baseline = _persist(repo_root, baseline)
        evidence = _persist(repo_root, evidence)

    deltas: dict[str, float | None] = {}
    for key in baseline["metrics"]:
        b = baseline["metrics"][key].get("value")
        e = evidence["metrics"][key].get("value")
        if b is None or e is None:
            deltas[key] = None
        else:
            deltas[key] = round(float(e) - float(b), 4)

    recommendation, rationale = level3_recommendation(evidence["metrics"])
    compare: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "report_id": _report_id("compare"),
        "plan_id": "n3-adaptive-intelligence-validation",
        "created_at": _utc_now(),
        "phase": "compare",
        "repository_sha": _git_sha(repo_root),
        "northstar_version": _version(repo_root),
        "metrics": evidence["metrics"],
        "deltas": deltas,
        "baseline_report_id": baseline.get("report_id"),
        "evidence_report_id": evidence.get("report_id"),
        "level3_recommendation": recommendation,
        "level3_rationale": rationale,
        "warnings": [],
        "evidence_path": None,
        "notes": (
            "Compare phase: deltas = with_evidence − baseline. "
            "Positive skill_reuse delta indicates Experiences improved Skill hit-rate. "
            "auto_applied remains false."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_applied": False,
    }
    try:
        validate_document(compare, SCHEMA)
    except ValidationError as exc:
        raise AdaptiveServiceError(f"compare schema validation failed: {exc}") from exc
    return _persist(repo_root, compare) if persist else compare
