"""Persist Policy objects, promotion events, and shadow reports (M50)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.behavior.policy.states import SCHEMA_VERSION
from orchestrator.providers.decision.state import redact_text
from orchestrator.schemas.validate import ValidationError, validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class PolicyStoreError(ValueError):
    """Raised when Policy persistence is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def policies_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evaluations" / "behavior" / "policies"


def shadow_dir(repo_root: Path) -> Path:
    return policies_root(repo_root) / "shadow"


def events_dir(repo_root: Path) -> Path:
    return policies_root(repo_root) / "events"


def materialize_dir(repo_root: Path) -> Path:
    return policies_root(repo_root) / "materialize-proposals"


def evidence_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "m50-policy-promotion-lifecycle"


def ensure_layout(repo_root: Path) -> None:
    for path in (
        policies_root(repo_root),
        shadow_dir(repo_root),
        events_dir(repo_root),
        materialize_dir(repo_root),
        evidence_root(repo_root),
    ):
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise PolicyStoreError(f"unsafe {label}: {value!r}")
    return value


def _write_json(path: Path, doc: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    return path


def policy_id_for_instruction(instruction_id: str) -> str:
    digest = hashlib.sha256(instruction_id.encode("utf-8")).hexdigest()[:12]
    return f"pol-{digest}"


def policy_path(repo_root: Path, policy_id: str) -> Path:
    pid = _safe_id(policy_id, label="policy_id")
    return policies_root(repo_root) / f"{pid}.json"


def write_policy(repo_root: Path, policy: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(policy)
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = SCHEMA_VERSION
    if payload.get("title"):
        payload["title"] = redact_text(str(payload["title"]))
    path = policy_path(repo_root, str(payload["policy_id"]))
    if path.is_file():
        try:
            with path.open(encoding="utf-8") as handle:
                existing = json.load(handle)
        except (OSError, json.JSONDecodeError):
            existing = None
        if isinstance(existing, dict) and existing.get("created_at"):
            payload["created_at"] = str(existing["created_at"])
            payload["updated_at"] = _utc_now()
    else:
        payload.setdefault("created_at", _utc_now())
    try:
        validate_document(payload, "behavior-policy.schema.json")
    except ValidationError as exc:
        raise PolicyStoreError(str(exc)) from exc
    return _write_json(path, payload)


def load_policy(repo_root: Path, policy_id: str) -> dict[str, Any]:
    path = policy_path(repo_root, policy_id)
    if not path.is_file():
        raise PolicyStoreError(f"policy not found: {policy_id}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "behavior-policy.schema.json")
    return doc


def list_policies(repo_root: Path) -> list[dict[str, Any]]:
    root = policies_root(repo_root)
    if not root.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(root.glob("pol-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        try:
            validate_document(doc, "behavior-policy.schema.json")
        except ValidationError:
            continue
        out.append(doc)
    return out


def write_event(repo_root: Path, event: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(event)
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = SCHEMA_VERSION
    payload.setdefault("created_at", _utc_now())
    if payload.get("notes"):
        payload["notes"] = redact_text(str(payload["notes"]))
    try:
        validate_document(payload, "policy-promotion-event.schema.json")
    except ValidationError as exc:
        raise PolicyStoreError(str(exc)) from exc
    eid = _safe_id(str(payload["event_id"]), label="event_id")
    return _write_json(events_dir(repo_root) / f"{eid}.json", payload)


def write_shadow(repo_root: Path, report: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(report)
    payload["applied"] = False
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = SCHEMA_VERSION
    payload.setdefault("created_at", _utc_now())
    if payload.get("diff_summary"):
        payload["diff_summary"] = redact_text(str(payload["diff_summary"]))
    try:
        validate_document(payload, "shadow-report.schema.json")
    except ValidationError as exc:
        raise PolicyStoreError(str(exc)) from exc
    sid = _safe_id(str(payload["shadow_id"]), label="shadow_id")
    return _write_json(shadow_dir(repo_root) / f"{sid}.json", payload)


def load_shadow(repo_root: Path, shadow_id: str) -> dict[str, Any]:
    path = shadow_dir(repo_root) / f"{_safe_id(shadow_id, label='shadow_id')}.json"
    if not path.is_file():
        raise PolicyStoreError(f"shadow report not found: {shadow_id}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "shadow-report.schema.json")
    return doc


def write_evidence_summary(repo_root: Path, summary: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(summary)
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    pid = _safe_id(str(payload.get("policy_id") or "unknown"), label="policy_id")
    return _write_json(evidence_root(repo_root) / f"{pid}-summary.json", payload)
