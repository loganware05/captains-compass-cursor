"""Dual-format behavior evaluation ledger (per-record JSON + ledger.jsonl)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.behavior.signals import SCHEMA_VERSION, normalize_signals
from orchestrator.schemas.validate import ValidationError, validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class BehaviorLedgerError(ValueError):
    """Raised when ledger persistence is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def behavior_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evaluations" / "behavior"


def ledger_path(repo_root: Path) -> Path:
    return behavior_dir(repo_root) / "ledger.jsonl"


def record_path(repo_root: Path, evaluation_id: str) -> Path:
    return behavior_dir(repo_root) / f"{evaluation_id}.json"


def ensure_layout(repo_root: Path) -> None:
    out = behavior_dir(repo_root)
    out.mkdir(parents=True, exist_ok=True)
    keep = out / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise BehaviorLedgerError(f"unsafe {label}: {value!r}")
    return value


def build_behavior_evaluation(
    packet: dict[str, Any],
    *,
    signals: dict[str, float],
    provider: str,
    model_id: str | None,
    evidence: list[Any] | None = None,
    prompt_bundle_hash: str = "",
    evaluation_id: str | None = None,
    abstain: bool = False,
    abstain_reason: str = "",
    crossings: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    eid = evaluation_id or f"beval-{uuid4().hex[:12]}"
    _safe_id(eid, label="evaluation_id")
    record = {
        "evaluation_id": eid,
        "execution_id": str(packet.get("execution_id") or ""),
        "task_id": str(packet.get("task_id") or ""),
        "plan_id": str(packet.get("plan_id") or ""),
        "agent": str(packet.get("agent") or ""),
        "model": str(packet.get("model") or model_id or ""),
        "skill_ids": list(packet.get("skill_ids") or []),
        "repository_sha": str(packet.get("repository_sha") or ""),
        "northstar_version": str(packet.get("northstar_version") or ""),
        "outcome": str(packet.get("outcome") or ""),
        "objective": str(packet.get("objective") or ""),
        "signals": normalize_signals(signals),
        "evidence": list(evidence if evidence is not None else packet.get("evidence") or []),
        "diff_meta": dict(packet.get("diff_meta") or {}),
        "content_hash": str(packet.get("content_hash") or ""),
        "crossings": list(crossings or []),
        "abstain": bool(abstain),
        "abstain_reason": abstain_reason,
        "evaluator": {
            "provider": provider,
            "model": model_id,
            "schema_version": SCHEMA_VERSION,
            "prompt_bundle_hash": prompt_bundle_hash,
        },
        "schema_version": SCHEMA_VERSION,
        "created_at": _utc_now(),
        "authority_mutation": False,
    }
    return record


def load_record(repo_root: Path, evaluation_id: str) -> dict[str, Any]:
    eid = _safe_id(evaluation_id, label="evaluation_id")
    path = record_path(repo_root, eid)
    if not path.is_file():
        raise BehaviorLedgerError(f"evaluation not found: {eid}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "behavior-evaluation.schema.json")
    return doc


def find_by_execution(
    repo_root: Path,
    execution_id: str,
    *,
    content_hash: str = "",
) -> dict[str, Any] | None:
    """Return matching finalized record if present (idempotency helper)."""
    ensure_layout(repo_root)
    for path in sorted(behavior_dir(repo_root).glob("beval-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        if doc.get("execution_id") != execution_id:
            continue
        if content_hash and doc.get("content_hash") == content_hash:
            return doc
        if not content_hash:
            return doc
    return None


def execution_ids_in_ledger(repo_root: Path) -> set[str]:
    ids: set[str] = set()
    root = behavior_dir(repo_root)
    if not root.is_dir():
        return ids
    for path in root.glob("beval-*.json"):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict) and doc.get("execution_id"):
            ids.add(str(doc["execution_id"]))
    return ids


def write_behavior_evaluation(repo_root: Path, record: dict[str, Any]) -> Path:
    """Validate and persist dual formats; return per-record JSON path."""
    try:
        validate_document(record, "behavior-evaluation.schema.json")
    except ValidationError as exc:
        raise BehaviorLedgerError(str(exc)) from exc
    eid = _safe_id(str(record["evaluation_id"]), label="evaluation_id")
    ensure_layout(repo_root)
    path = record_path(repo_root, eid)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # Append JSONL (one line)
    with ledger_path(repo_root).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
        handle.write("\n")
    return path


def list_records(repo_root: Path) -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    records: list[dict[str, Any]] = []
    for path in sorted(behavior_dir(repo_root).glob("beval-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict):
            records.append(doc)
    return records
