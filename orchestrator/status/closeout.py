"""Closeout-readiness assessment for Project Overseer (N1).

Read-only: composes drift findings + an optional ledger into a schema-validated
report. Never auto-closes GitHub issues or mutates authority.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.status.explain import explain_status
from orchestrator.status.store import StatusStoreError, ensure_layout, status_root

SCHEMA_NAME = "status-closeout-report.schema.json"
SCHEMA_VERSION = "1"
DEFAULT_LEDGER_REL = Path(".agent/evidence/n1-operational-reconciliation/CLOSEOUT_LEDGER.json")


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def closeout_reports_dir(repo_root: Path) -> Path:
    return status_root(repo_root) / "closeout-reports"


def closeout_evidence_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "n1-operational-reconciliation"


def _report_id(snapshot_id: str, item_count: int) -> str:
    material = f"{snapshot_id}|{item_count}|{_utc_now()}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
    return f"closeout-{digest}"


def load_ledger(repo_root: Path, ledger_path: Path | None = None) -> tuple[list[dict[str, Any]], Path | None]:
    """Load ledger JSON if present; otherwise return empty list."""
    path = Path(ledger_path) if ledger_path else Path(repo_root) / DEFAULT_LEDGER_REL
    if not path.is_file():
        return [], None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StatusStoreError(f"invalid closeout ledger at {path}: {exc}") from exc
    items = raw.get("items") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise StatusStoreError(f"closeout ledger must be a list or {{items: [...]}}: {path}")
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise StatusStoreError(f"ledger item {idx} must be an object")
        required = (
            "item_id",
            "kind",
            "title",
            "status",
            "recommended_disposition",
            "evidence",
        )
        missing = [k for k in required if k not in item]
        if missing:
            raise StatusStoreError(
                f"ledger item {idx} missing fields: {', '.join(missing)}"
            )
        evidence = item.get("evidence") or []
        if not isinstance(evidence, list):
            raise StatusStoreError(f"ledger item {idx} evidence must be a list")
        normalized.append(
            {
                "item_id": str(item["item_id"]),
                "kind": str(item["kind"]),
                "title": str(item["title"]),
                "status": str(item["status"]),
                "recommended_disposition": str(item["recommended_disposition"]),
                "evidence": [str(e) for e in evidence],
                "subsystem": str(item.get("subsystem") or ""),
                "notes": str(item.get("notes") or ""),
            }
        )
    return normalized, path


def _readiness(items: list[dict[str, Any]], finding_severities: list[str]) -> str:
    if any(s == "error" for s in finding_severities):
        return "blocked"
    actionable = {
        "still_actionable",
        "open_unverified",
    }
    if any(i.get("status") in actionable for i in items):
        return "needs_captain_action"
    # completed-but-open issues still need Captain close
    if any(
        i.get("kind") == "github_issue" and i.get("status") == "completed"
        for i in items
    ):
        return "needs_captain_action"
    if any(s == "warn" for s in finding_severities):
        return "needs_captain_action"
    return "ready"


def _recommended_actions(
    readiness: str,
    items: list[dict[str, Any]],
    findings: list[dict[str, Any]],
) -> list[str]:
    actions: list[str] = []
    for item in items:
        status = str(item.get("status") or "")
        if status == "completed" and item.get("kind") == "github_issue":
            actions.append(
                f"Captain: verify acceptance then close {item.get('item_id')} "
                f"— {item.get('recommended_disposition')}"
            )
        elif status in {"still_actionable", "open_unverified"}:
            actions.append(
                f"Track {item.get('item_id')}: {item.get('recommended_disposition')}"
            )
        elif status == "deferred":
            actions.append(
                f"Keep deferred {item.get('item_id')} until prerequisites met"
            )
    for finding in findings:
        if finding.get("severity") in {"warn", "error"}:
            actions.append(
                f"Resolve drift {finding.get('finding_id')}: {finding.get('summary')}"
            )
    if readiness == "ready" and not actions:
        actions.append("Closeout readiness: no blocking actions.")
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for action in actions:
        if action not in seen:
            seen.add(action)
            out.append(action)
    return out


def build_closeout_report(
    repo_root: Path,
    *,
    snapshot_id: str = "",
    ledger_path: Path | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    """Build and optionally persist a closeout-readiness report."""
    ensure_layout(repo_root)
    closeout_reports_dir(repo_root).mkdir(parents=True, exist_ok=True)
    evidence_dir = closeout_evidence_dir(repo_root)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    snapshot = explain_status(
        repo_root, snapshot_id=snapshot_id, persist=True, write_memory=False
    )
    findings = list(snapshot.get("findings") or [])
    items, loaded_ledger = load_ledger(repo_root, ledger_path)
    severities = [str(f.get("severity") or "info") for f in findings]
    readiness = _readiness(items, severities)
    actions = _recommended_actions(readiness, items, findings)
    sid = str(snapshot.get("snapshot_id") or "")
    report_id = _report_id(sid, len(items))

    completed = sum(1 for i in items if i.get("status") == "completed")
    deferred = sum(1 for i in items if i.get("status") == "deferred")
    actionable = sum(
        1 for i in items if i.get("status") in {"still_actionable", "open_unverified"}
    )
    summary = (
        f"Closeout readiness={readiness}; ledger_items={len(items)} "
        f"(completed={completed}, deferred={deferred}, actionable={actionable}); "
        f"drift_findings={len(findings)}. "
        "Issues are never auto-closed."
    )

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "report_id": report_id,
        "plan_id": "n1-operational-reconciliation",
        "created_at": _utc_now(),
        "repository_sha": str(snapshot.get("repository_sha") or ""),
        "northstar_version": str(snapshot.get("northstar_version") or ""),
        "snapshot_id": sid or None,
        "readiness": readiness,
        "summary": summary,
        "ledger_items": items,
        "drift_finding_ids": [str(f.get("finding_id") or "") for f in findings],
        "recommended_actions": actions,
        "ledger_path": str(loaded_ledger) if loaded_ledger else None,
        "evidence_path": None,
        "approved_for_execution": False,
        "authority_mutation": False,
        "issues_auto_closed": False,
    }

    try:
        validate_document(report, SCHEMA_NAME)
    except ValidationError as exc:
        raise StatusStoreError(f"closeout report failed schema validation: {exc}") from exc

    if persist:
        out = closeout_reports_dir(repo_root) / f"{report_id}.json"
        tmp = out.with_suffix(out.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
        tmp.replace(out)
        evidence_copy = evidence_dir / "CLOSEOUT_REPORT.json"
        with evidence_copy.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
        report["evidence_path"] = str(evidence_copy)
        # re-write report with evidence_path set
        with out.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
        validate_document(report, SCHEMA_NAME)

    return report
