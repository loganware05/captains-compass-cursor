"""Persist execution provenance records (M53)."""

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


class ProvenanceStoreError(ValueError):
    """Raised when provenance persistence is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def provenance_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evaluations" / "behavior" / "provenance"


def evidence_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "m53-prompt-policy-provenance"


def ensure_layout(repo_root: Path) -> None:
    for path in (provenance_dir(repo_root), evidence_root(repo_root)):
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise ProvenanceStoreError(f"unsafe {label}: {value!r}")
    return value


def provenance_id_for(payload: dict[str, Any]) -> str:
    material = {
        "execution_id": payload.get("execution_id"),
        "prompt_bundle_hash": payload.get("prompt_bundle_hash"),
        "evaluation_id": payload.get("evaluation_id"),
        "repository_sha": payload.get("repository_sha"),
    }
    digest = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:12]
    return f"prov-{digest}"


def write_provenance(repo_root: Path, doc: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(doc)
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = SCHEMA_VERSION
    payload.setdefault("created_at", _utc_now())
    if payload.get("notes"):
        payload["notes"] = redact_text(str(payload["notes"]))
    for key in ("prompt_bundle_hash", "model", "model_provider", "context_route", "agent"):
        if payload.get(key):
            payload[key] = redact_text(str(payload[key]))
    try:
        validate_document(payload, "execution-provenance.schema.json")
    except ValidationError as exc:
        raise ProvenanceStoreError(str(exc)) from exc
    pid = _safe_id(str(payload["provenance_id"]), label="provenance_id")
    path = provenance_dir(repo_root) / f"{pid}.json"
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    summary = {
        "provenance_id": pid,
        "execution_id": payload.get("execution_id"),
        "evaluation_id": payload.get("evaluation_id"),
        "prompt_bundle_hash": payload.get("prompt_bundle_hash"),
        "approved_for_execution": False,
        "authority_mutation": False,
        "created_at": payload["created_at"],
    }
    with (evidence_root(repo_root) / f"{pid}-summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    doc.clear()
    doc.update(payload)
    return path


def load_provenance(repo_root: Path, provenance_id: str) -> dict[str, Any]:
    path = provenance_dir(repo_root) / f"{_safe_id(provenance_id, label='provenance_id')}.json"
    if not path.is_file():
        raise ProvenanceStoreError(f"provenance not found: {provenance_id}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "execution-provenance.schema.json")
    return doc


def list_provenance(repo_root: Path) -> list[dict[str, Any]]:
    root = provenance_dir(repo_root)
    if not root.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(root.glob("prov-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict):
            out.append(doc)
    return out
