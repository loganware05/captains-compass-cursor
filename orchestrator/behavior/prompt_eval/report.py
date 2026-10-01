"""Persist prompt-eval reports under behavior/prompt-eval + evidence (M49)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.providers.decision.state import redact_text
from orchestrator.schemas.validate import ValidationError, validate_document

REPORT_SCHEMA_VERSION = "1"


class PromptEvalReportError(ValueError):
    """Raised when report persistence is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def prompt_eval_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evaluations" / "behavior" / "prompt-eval"


def evidence_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "m49-prompt-evaluation-harness"


def ensure_layout(repo_root: Path) -> None:
    for path in (prompt_eval_root(repo_root), evidence_root(repo_root)):
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def report_id_for_payload(payload: dict[str, Any]) -> str:
    material = {
        "cases": payload.get("cases"),
        "baseline_mode": payload.get("baseline_mode"),
        "candidate_mode": payload.get("candidate_mode"),
        "non_regression": payload.get("non_regression"),
    }
    digest = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:12]
    return f"peval-{digest}"


def _write_json(path: Path, doc: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    return path


def _redact_report(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    for key in ("cases_path", "evidence_path", "northstar_version"):
        if key in out and isinstance(out[key], str):
            out[key] = redact_text(out[key])
    cases = []
    for case in out.get("cases") or []:
        if not isinstance(case, dict):
            continue
        item = dict(case)
        metrics = {}
        for name, metric in (item.get("metrics") or {}).items():
            if isinstance(metric, dict):
                m = dict(metric)
                if "detail" in m:
                    m["detail"] = redact_text(str(m["detail"]))
                metrics[name] = m
        item["metrics"] = metrics
        item["failures"] = [redact_text(str(x)) for x in (item.get("failures") or [])]
        cases.append(item)
    out["cases"] = cases
    return out


def write_report(repo_root: Path, report: dict[str, Any]) -> dict[str, Any]:
    ensure_layout(repo_root)
    payload = _redact_report(dict(report))
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = REPORT_SCHEMA_VERSION
    payload.setdefault("created_at", _utc_now())
    payload["baseline_mode"] = "include_proposals=false"
    payload["candidate_mode"] = "include_proposals=true"
    if not payload.get("report_id"):
        payload["report_id"] = report_id_for_payload(payload)
    try:
        validate_document(payload, "prompt-eval-report.schema.json")
    except ValidationError as exc:
        raise PromptEvalReportError(str(exc)) from exc

    dest = prompt_eval_root(repo_root) / f"{payload['report_id']}.json"
    _write_json(dest, payload)

    summary = {
        "report_id": payload["report_id"],
        "non_regression": payload["non_regression"],
        "case_count": payload["case_count"],
        "passed_count": payload["passed_count"],
        "failed_count": payload["failed_count"],
        "canonical_path": str(dest.relative_to(Path(repo_root)))
        if dest.is_relative_to(Path(repo_root))
        else str(dest),
        "approved_for_execution": False,
        "authority_mutation": False,
        "created_at": payload["created_at"],
    }
    evidence_path = evidence_root(repo_root) / f"{payload['report_id']}-summary.json"
    _write_json(evidence_path, summary)
    payload["evidence_path"] = str(
        evidence_path.relative_to(Path(repo_root))
        if evidence_path.is_relative_to(Path(repo_root))
        else evidence_path
    )
    # Re-write canonical with evidence_path filled (still schema-valid)
    try:
        validate_document(payload, "prompt-eval-report.schema.json")
    except ValidationError as exc:
        raise PromptEvalReportError(str(exc)) from exc
    _write_json(dest, payload)
    return payload


def list_reports(repo_root: Path) -> list[dict[str, Any]]:
    root = prompt_eval_root(repo_root)
    if not root.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(root.glob("peval-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict):
            out.append(doc)
    return out


def load_report(repo_root: Path, report_id: str) -> dict[str, Any]:
    path = prompt_eval_root(repo_root) / f"{report_id}.json"
    if not path.is_file():
        raise PromptEvalReportError(f"report not found: {report_id}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise PromptEvalReportError(f"invalid report: {report_id}")
    validate_document(doc, "prompt-eval-report.schema.json")
    return doc
