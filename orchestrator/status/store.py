"""Persist Project Overseer snapshots and reconcile proposals (M51)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.providers.decision.state import redact_text
from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA_VERSION = "1"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class StatusStoreError(ValueError):
    """Raised when status persistence is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def status_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "status"


def snapshots_dir(repo_root: Path) -> Path:
    return status_root(repo_root) / "snapshots"


def proposals_dir(repo_root: Path) -> Path:
    return status_root(repo_root) / "reconcile-proposals"


def evidence_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "m51-project-overseer"


def ensure_layout(repo_root: Path) -> None:
    for path in (snapshots_dir(repo_root), proposals_dir(repo_root), evidence_root(repo_root)):
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise StatusStoreError(f"unsafe {label}: {value!r}")
    return value


def _write_json(path: Path, doc: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    return path


def write_snapshot(repo_root: Path, snapshot: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(snapshot)
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = SCHEMA_VERSION
    payload.setdefault("created_at", _utc_now())
    if payload.get("explanation"):
        payload["explanation"] = redact_text(str(payload["explanation"]))
    findings = []
    for finding in payload.get("findings") or []:
        if not isinstance(finding, dict):
            continue
        item = dict(finding)
        item["summary"] = redact_text(str(item.get("summary") or ""))
        item["evidence"] = [redact_text(str(x)) for x in (item.get("evidence") or [])]
        findings.append(item)
    payload["findings"] = findings
    try:
        validate_document(payload, "project-status-snapshot.schema.json")
    except ValidationError as exc:
        raise StatusStoreError(str(exc)) from exc
    sid = _safe_id(str(payload["snapshot_id"]), label="snapshot_id")
    path = snapshots_dir(repo_root) / f"{sid}.json"
    _write_json(path, payload)
    summary = {
        "snapshot_id": sid,
        "finding_count": len(findings),
        "northstar_version": payload.get("northstar_version") or "",
        "repository_sha": payload.get("repository_sha") or "",
        "approved_for_execution": False,
        "authority_mutation": False,
        "created_at": payload["created_at"],
    }
    _write_json(evidence_root(repo_root) / f"{sid}-summary.json", summary)
    # Sync persisted fields back so callers hold a schema-complete document.
    snapshot.clear()
    snapshot.update(payload)
    return path


def load_snapshot(repo_root: Path, snapshot_id: str) -> dict[str, Any]:
    path = snapshots_dir(repo_root) / f"{_safe_id(snapshot_id, label='snapshot_id')}.json"
    if not path.is_file():
        raise StatusStoreError(f"snapshot not found: {snapshot_id}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "project-status-snapshot.schema.json")
    return doc


def list_snapshots(repo_root: Path) -> list[dict[str, Any]]:
    root = snapshots_dir(repo_root)
    if not root.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(root.glob("psnap-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict):
            out.append(doc)
    return out


def write_proposal(repo_root: Path, proposal: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(proposal)
    payload["applied"] = False
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = SCHEMA_VERSION
    payload.setdefault("created_at", _utc_now())
    if payload.get("notes"):
        payload["notes"] = redact_text(str(payload["notes"]))
    actions = []
    for action in payload.get("actions") or []:
        if not isinstance(action, dict):
            continue
        item = dict(action)
        item["summary"] = redact_text(str(item.get("summary") or ""))
        if item.get("suggested_patch"):
            item["suggested_patch"] = redact_text(str(item["suggested_patch"]))
        actions.append(item)
    payload["actions"] = actions
    try:
        validate_document(payload, "status-reconcile-proposal.schema.json")
    except ValidationError as exc:
        raise StatusStoreError(str(exc)) from exc
    pid = _safe_id(str(payload["proposal_id"]), label="proposal_id")
    out_dir = proposals_dir(repo_root) / pid
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "proposal.json"
    _write_json(path, payload)
    (out_dir / "README.md").write_text(
        "# Reconcile proposal (M51)\n\n"
        "Proposal-only. NorthStar will not apply these edits to project memory "
        "automatically. Open a Captain-reviewed PR if adopting suggestions.\n",
        encoding="utf-8",
    )
    proposal.clear()
    proposal.update(payload)
    return path


def snapshot_id_for(payload: dict[str, Any]) -> str:
    material = {
        "repository_sha": payload.get("repository_sha"),
        "northstar_version": payload.get("northstar_version"),
        "findings": payload.get("findings"),
        "skill_count_fs": payload.get("skill_count_fs"),
    }
    digest = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:12]
    return f"psnap-{digest}"
