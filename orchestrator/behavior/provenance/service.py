"""Operator service for execution provenance (M53)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from orchestrator.behavior.enabled import provenance_enabled, require_provenance_enabled
from orchestrator.behavior.instructions.composer import prompt_bundle_hash_for_packet
from orchestrator.behavior.ledger import find_by_execution
from orchestrator.behavior.packet import BehaviorPacketError, build_evaluation_packet
from orchestrator.behavior.policy.store import list_policies
from orchestrator.behavior.provenance.store import (
    ProvenanceStoreError,
    list_provenance as store_list,
    load_provenance as store_load,
    provenance_id_for,
    write_provenance,
)


class ProvenanceServiceError(ValueError):
    """Operator-facing provenance errors."""


def build_provenance_record(
    repo_root: Path,
    *,
    execution_id: str = "",
    evaluation: dict[str, Any] | None = None,
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Best-effort provenance from packet and/or evaluation fields."""
    root = Path(repo_root)
    pkt = dict(packet or {})
    ev = dict(evaluation or {})
    eid = (
        execution_id
        or str(ev.get("execution_id") or "")
        or str(pkt.get("execution_id") or "")
    )
    if not eid:
        raise ProvenanceServiceError("execution_id is required")
    if not pkt:
        try:
            pkt = build_evaluation_packet(root, eid)
        except (BehaviorPacketError, Exception):
            pkt = {"execution_id": eid}
    if not ev:
        found = find_by_execution(root, eid)
        if found:
            ev = found
    prompt_hash = str(
        (ev.get("evaluator") or {}).get("prompt_bundle_hash")
        or pkt.get("prompt_bundle_hash")
        or ""
    )
    if not prompt_hash:
        try:
            prompt_hash = prompt_bundle_hash_for_packet(root, pkt) or ""
        except Exception:
            prompt_hash = ""
    policy_ids = [
        str(p.get("policy_id"))
        for p in list_policies(root)
        if p.get("lifecycle_state") in {"active", "proven", "approved"}
        and p.get("policy_id")
    ]
    instruction_ids: list[str] = []
    for pol in list_policies(root):
        if str(pol.get("policy_id")) in policy_ids:
            instruction_ids.extend(str(x) for x in (pol.get("instruction_ids") or []))
    # Deduplicate preserving order
    seen: set[str] = set()
    instruction_ids = [x for x in instruction_ids if not (x in seen or seen.add(x))]
    skill_ids = list(ev.get("skill_ids") or pkt.get("skill_ids") or [])
    record: dict[str, Any] = {
        "execution_id": eid,
        "evaluation_id": str(ev.get("evaluation_id") or ""),
        "prompt_bundle_hash": prompt_hash,
        "instruction_ids": instruction_ids,
        "policy_ids": policy_ids,
        "skill_ids": [str(s) for s in skill_ids],
        "skill_versions": {},
        "model": str(ev.get("model") or pkt.get("model") or ""),
        "model_provider": str(
            (ev.get("evaluator") or {}).get("provider") or pkt.get("model_provider") or ""
        ),
        "context_route": str(pkt.get("context_route") or ""),
        "repository_sha": str(
            ev.get("repository_sha") or pkt.get("repository_sha") or ""
        ),
        "northstar_version": str(
            ev.get("northstar_version") or pkt.get("northstar_version") or ""
        ),
        "agent": str(ev.get("agent") or pkt.get("agent") or ""),
        "notes": "Best-effort provenance capture (M53). Missing fields allowed.",
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    record["provenance_id"] = provenance_id_for(record)
    return record


def capture_from_execution(repo_root: Path, execution_id: str) -> dict[str, Any]:
    require_provenance_enabled()
    try:
        record = build_provenance_record(repo_root, execution_id=execution_id)
        path = write_provenance(repo_root, record)
    except (ProvenanceStoreError, BehaviorPacketError) as exc:
        raise ProvenanceServiceError(str(exc)) from exc
    return {"status": "captured", "provenance": record, "path": str(path)}


def capture_from_evaluation(
    repo_root: Path, evaluation: dict[str, Any]
) -> dict[str, Any] | None:
    """Emit provenance when gate on; return None when disabled (best-effort)."""
    if not provenance_enabled():
        return None
    try:
        record = build_provenance_record(
            repo_root,
            execution_id=str(evaluation.get("execution_id") or ""),
            evaluation=evaluation,
        )
        path = write_provenance(repo_root, record)
    except (ProvenanceStoreError, ProvenanceServiceError):
        return None
    return {"provenance": record, "path": str(path)}


def list_provenance(repo_root: Path) -> dict[str, Any]:
    require_provenance_enabled()
    items = store_list(repo_root)
    return {
        "status": "ok",
        "count": len(items),
        "provenance": items,
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def load_provenance(repo_root: Path, provenance_id: str) -> dict[str, Any]:
    require_provenance_enabled()
    try:
        doc = store_load(repo_root, provenance_id)
    except ProvenanceStoreError as exc:
        raise ProvenanceServiceError(str(exc)) from exc
    return {"status": "ok", "provenance": doc}


def export_provenance_csv(repo_root: Path, dest: Path) -> Path:
    require_provenance_enabled()
    items = store_list(repo_root)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "provenance_id",
        "execution_id",
        "evaluation_id",
        "prompt_bundle_hash",
        "model",
        "model_provider",
        "repository_sha",
        "northstar_version",
        "approved_for_execution",
    ]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow({k: item.get(k, "") for k in fieldnames})
    return dest
