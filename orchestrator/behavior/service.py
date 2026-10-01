"""Orchestrate observe-only behavior evaluation runs (M46)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.behavior.enabled import require_behavior_eval_enabled
from orchestrator.behavior.export import export_csv
from orchestrator.behavior.instructions.composer import prompt_bundle_hash_for_packet
from orchestrator.behavior.ledger import (
    BehaviorLedgerError,
    build_behavior_evaluation,
    execution_ids_in_ledger,
    find_by_execution,
    list_records,
    load_record,
    write_behavior_evaluation,
)
from orchestrator.behavior.packet import (
    BehaviorPacketError,
    build_evaluation_packet,
    list_pending_execution_ids,
)
from orchestrator.behavior.thresholds import load_thresholds, signals_crossing_threshold
from orchestrator.providers.decision.file_provider import select_decision_provider
from orchestrator.providers.decision.types import BehaviorEvalRequest


class BehaviorEvalServiceError(ValueError):
    """Operator-facing evaluation errors."""


def _result_to_signals(result) -> tuple[dict[str, float], bool, str]:
    if result.abstain or result.error:
        return {}, True, result.abstain_reason or result.error or "abstain"
    return dict(result.signals or {}), False, ""


def evaluate_execution(
    repo_root: Path,
    execution_id: str,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Build packet, call DecisionProvider.evaluate_behavior, persist dual ledger."""
    require_behavior_eval_enabled()
    root = Path(repo_root).resolve()
    try:
        packet = build_evaluation_packet(root, execution_id)
    except BehaviorPacketError as exc:
        raise BehaviorEvalServiceError(str(exc)) from exc
    except Exception as exc:  # telemetry store errors
        raise BehaviorEvalServiceError(str(exc)) from exc

    existing = find_by_execution(
        root, packet["execution_id"], content_hash=str(packet.get("content_hash") or "")
    )
    if existing and not force:
        return {
            "status": "idempotent",
            "record": existing,
            "path": str(
                root
                / ".agent"
                / "evaluations"
                / "behavior"
                / f"{existing['evaluation_id']}.json"
            ),
        }

    provider = select_decision_provider(root)
    request = BehaviorEvalRequest(packet=packet)
    result = provider.evaluate_behavior(request)
    signals, abstain, reason = _result_to_signals(result)
    thresholds = load_thresholds()
    crossings = [] if abstain else signals_crossing_threshold(signals, thresholds)
    # M48: record composed PICCO hash when available (never injects into live prompts).
    composed_hash = prompt_bundle_hash_for_packet(root, packet)
    provider_hash = str((result.raw_answers or {}).get("prompt_bundle_hash") or "")
    record = build_behavior_evaluation(
        packet,
        signals=signals,
        provider=result.provider,
        model_id=result.model_id,
        abstain=abstain,
        abstain_reason=reason,
        crossings=crossings,
        prompt_bundle_hash=composed_hash or provider_hash,
    )
    # Never mutate authority — hard constant on every write
    record["authority_mutation"] = False
    try:
        path = write_behavior_evaluation(root, record)
    except BehaviorLedgerError as exc:
        raise BehaviorEvalServiceError(str(exc)) from exc
    return {"status": "written", "record": record, "path": str(path)}


def evaluate_pending(repo_root: Path) -> dict[str, Any]:
    require_behavior_eval_enabled()
    root = Path(repo_root).resolve()
    known = execution_ids_in_ledger(root)
    pending = list_pending_execution_ids(root, ledger_execution_ids=known)
    results = []
    for execution_id in pending:
        results.append(evaluate_execution(root, execution_id))
    return {"pending": pending, "results": results}


def review_ledger(repo_root: Path) -> dict[str, Any]:
    require_behavior_eval_enabled()
    records = list_records(repo_root)
    crossings = []
    for record in records:
        for item in record.get("crossings") or []:
            crossings.append(
                {
                    "evaluation_id": record.get("evaluation_id"),
                    "execution_id": record.get("execution_id"),
                    **item,
                }
            )
    return {"count": len(records), "records": records, "crossings": crossings}


def retry_evaluation(repo_root: Path, evaluation_id: str) -> dict[str, Any]:
    require_behavior_eval_enabled()
    root = Path(repo_root).resolve()
    prior = load_record(root, evaluation_id)
    execution_id = str(prior.get("execution_id") or "")
    if not execution_id:
        raise BehaviorEvalServiceError("prior evaluation missing execution_id")
    return evaluate_execution(root, execution_id, force=True)


def export_ledger_csv(repo_root: Path, dest: Path) -> Path:
    require_behavior_eval_enabled()
    return export_csv(repo_root, dest)
