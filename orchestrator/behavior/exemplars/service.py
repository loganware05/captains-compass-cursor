"""Operator service for behavior exemplars (M53)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from orchestrator.behavior.enabled import require_provenance_enabled
from orchestrator.behavior.exemplars.store import (
    ExemplarStoreError,
    exemplar_id_for,
    list_exemplars as store_list,
    load_exemplar as store_load,
    write_exemplar,
)
from orchestrator.behavior.ledger import BehaviorLedgerError, load_record


class ExemplarServiceError(ValueError):
    """Operator-facing exemplar errors."""


def draft_exemplar(
    repo_root: Path,
    *,
    polarity: str,
    evaluation_id: str = "",
    provenance_id: str = "",
    execution_id: str = "",
    summary: str = "",
    notes: str = "",
) -> dict[str, Any]:
    require_provenance_enabled()
    if polarity not in {"positive", "negative"}:
        raise ExemplarServiceError("polarity must be positive or negative")
    evidence: list[str] = []
    eval_doc: dict[str, Any] = {}
    if evaluation_id:
        try:
            eval_doc = load_record(repo_root, evaluation_id)
        except BehaviorLedgerError as exc:
            raise ExemplarServiceError(str(exc)) from exc
        execution_id = execution_id or str(eval_doc.get("execution_id") or "")
        evidence.append(f"evaluation:{evaluation_id}")
        outcome = str(eval_doc.get("outcome") or "")
        if not summary:
            summary = (
                f"{polarity} exemplar from evaluation {evaluation_id}"
                + (f" (outcome={outcome})" if outcome else "")
            )
    if provenance_id:
        evidence.append(f"provenance:{provenance_id}")
    if execution_id:
        evidence.append(f"execution:{execution_id}")
    if not summary:
        summary = f"{polarity} behavior exemplar draft"
    doc: dict[str, Any] = {
        "polarity": polarity,
        "summary": summary,
        "evaluation_id": evaluation_id,
        "provenance_id": provenance_id,
        "execution_id": execution_id,
        "evidence": evidence,
        "notes": notes
        or "Proposal-only exemplar. Captain must review before any learning use.",
        "auto_promoted": False,
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    doc["exemplar_id"] = exemplar_id_for(doc)
    try:
        path = write_exemplar(repo_root, doc)
    except ExemplarStoreError as exc:
        raise ExemplarServiceError(str(exc)) from exc
    return {
        "status": "drafted",
        "exemplar": doc,
        "path": str(path),
        "auto_promoted": False,
    }


def list_exemplars(repo_root: Path, *, polarity: str = "") -> dict[str, Any]:
    require_provenance_enabled()
    items = store_list(repo_root, polarity=polarity)
    return {
        "status": "ok",
        "count": len(items),
        "exemplars": items,
        "auto_promoted": False,
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def load_exemplar(repo_root: Path, exemplar_id: str) -> dict[str, Any]:
    require_provenance_enabled()
    try:
        doc = store_load(repo_root, exemplar_id)
    except ExemplarStoreError as exc:
        raise ExemplarServiceError(str(exc)) from exc
    return {"status": "ok", "exemplar": doc}


def export_exemplars_csv(repo_root: Path, dest: Path) -> Path:
    require_provenance_enabled()
    items = store_list(repo_root)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "exemplar_id",
        "polarity",
        "summary",
        "evaluation_id",
        "provenance_id",
        "execution_id",
        "auto_promoted",
        "approved_for_execution",
    ]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow({k: item.get(k, "") for k in fieldnames})
    return dest
