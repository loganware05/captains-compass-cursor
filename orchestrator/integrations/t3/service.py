"""Operator service for northstar t3 capabilities|start|status|collect|cancel|list|show."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.integrations.events import utc_now
from orchestrator.integrations.t3.adapter import (
    FixtureT3ExecutionAdapter,
    LiveT3ExecutionAdapter,
)
from orchestrator.integrations.t3.enabled import (
    require_t3_exec_enabled,
    require_t3_exec_live_enabled,
    t3_exec_live_enabled,
)
from orchestrator.integrations.t3.plan_gate import PlanGateError, require_plan_binding
from orchestrator.integrations.t3.store import (
    T3StoreError,
    list_executions as store_list,
    load_execution,
    write_execution,
)

# Process-local fixture adapter so status/collect share state within a CLI process.
_FIXTURE = FixtureT3ExecutionAdapter()


class T3ServiceError(ValueError):
    """Operator-facing T3 adapter errors."""


def _timeline_append(doc: dict[str, Any], status: str, note: str = "") -> None:
    entry: dict[str, str] = {"at": utc_now(), "status": status}
    if note:
        entry["note"] = note
    timeline = list(doc.get("timeline") or [])
    timeline.append(entry)
    doc["timeline"] = timeline
    doc["status"] = status
    doc["updated_at"] = entry["at"]


def list_capabilities(*, force_live: bool = False) -> dict[str, Any]:
    require_t3_exec_enabled()
    if force_live or t3_exec_live_enabled():
        require_t3_exec_live_enabled()
        return LiveT3ExecutionAdapter().capabilities()
    return _FIXTURE.capabilities()


def start_execution(
    repo_root: Path,
    *,
    plan_id: str,
    objective: str,
    provider: str = "fixture",
    model: str = "",
    allow_fixture_plan: bool = False,
    force_live: bool = False,
) -> dict[str, Any]:
    require_t3_exec_enabled()
    if not plan_id.strip():
        raise T3ServiceError("--plan-id is required")
    if not objective.strip():
        raise T3ServiceError("--objective is required")
    try:
        binding = require_plan_binding(
            repo_root,
            plan_id=plan_id.strip(),
            allow_fixture_plan=allow_fixture_plan,
        )
    except PlanGateError as exc:
        raise T3ServiceError(str(exc)) from exc

    use_live = force_live or t3_exec_live_enabled()
    if use_live:
        require_t3_exec_live_enabled()
        adapter = LiveT3ExecutionAdapter()
        mode = "live"
    else:
        adapter = _FIXTURE
        mode = "fixture"

    execution_id = f"t3-exec-{uuid4().hex[:12]}"
    try:
        started = adapter.start(
            {
                "execution_id": execution_id,
                "plan_id": plan_id.strip(),
                "objective": objective.strip(),
                "provider": provider,
                "model": model,
            }
        )
    except RuntimeError as exc:
        raise T3ServiceError(str(exc)) from exc

    now = utc_now()
    doc: dict[str, Any] = {
        "schema_version": "1",
        "execution_id": str(started.get("execution_id") or execution_id),
        "plan_id": plan_id.strip(),
        "mode": mode,
        "provider": str(started.get("provider") or provider),
        "model": str(started.get("model") or model or ""),
        "objective": objective.strip(),
        "status": "started",
        "thread_ref": str(started.get("thread_ref") or ""),
        "timeline": [{"at": now, "status": "started", "note": f"binding={binding['binding']}"}],
        "artifacts": [],
        "collected_summary": "",
        "created_at": now,
        "updated_at": now,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "bypassed_plan_gate": False,
    }
    try:
        write_execution(repo_root, doc)
    except T3StoreError as exc:
        raise T3ServiceError(str(exc)) from exc
    return {
        "status": "started",
        "execution": doc,
        "plan_binding": binding,
        "approved_for_execution": False,
        "authority_mutation": False,
        "bypassed_plan_gate": False,
    }


def status_execution(repo_root: Path, execution_id: str) -> dict[str, Any]:
    require_t3_exec_enabled()
    try:
        doc = load_execution(repo_root, execution_id)
    except T3StoreError as exc:
        raise T3ServiceError(str(exc)) from exc
    if doc.get("mode") == "fixture":
        try:
            live = _FIXTURE.status(execution_id)
            _timeline_append(doc, str(live.get("status") or doc["status"]), "fixture-status")
        except KeyError:
            # Persist-only status if process-local fixture state was lost.
            if doc["status"] == "started":
                _timeline_append(doc, "running", "persisted-status-advance")
    try:
        write_execution(repo_root, doc)
    except T3StoreError as exc:
        raise T3ServiceError(str(exc)) from exc
    return {"status": "ok", "execution": doc}


def collect_execution(repo_root: Path, execution_id: str) -> dict[str, Any]:
    require_t3_exec_enabled()
    try:
        doc = load_execution(repo_root, execution_id)
    except T3StoreError as exc:
        raise T3ServiceError(str(exc)) from exc
    if doc.get("mode") == "fixture":
        try:
            collected = _FIXTURE.collect(execution_id)
        except KeyError:
            collected = {
                "status": "completed",
                "collected_summary": f"Persisted fixture collect for {execution_id}",
                "artifacts": [f"fixture://{execution_id}/summary.txt"],
            }
        doc["artifacts"] = list(collected.get("artifacts") or [])
        doc["collected_summary"] = str(collected.get("collected_summary") or "")
        _timeline_append(doc, "completed", "fixture-collect")
    else:
        raise T3ServiceError("live collect unavailable in v1.79.0 skeleton")
    try:
        write_execution(repo_root, doc)
    except T3StoreError as exc:
        raise T3ServiceError(str(exc)) from exc
    return {"status": "collected", "execution": doc, "bypassed_plan_gate": False}


def cancel_execution(repo_root: Path, execution_id: str) -> dict[str, Any]:
    require_t3_exec_enabled()
    try:
        doc = load_execution(repo_root, execution_id)
    except T3StoreError as exc:
        raise T3ServiceError(str(exc)) from exc
    if doc.get("mode") == "fixture":
        try:
            _FIXTURE.cancel(execution_id)
        except KeyError:
            pass
        _timeline_append(doc, "cancelled", "fixture-cancel")
    else:
        raise T3ServiceError("live cancel unavailable in v1.79.0 skeleton")
    try:
        write_execution(repo_root, doc)
    except T3StoreError as exc:
        raise T3ServiceError(str(exc)) from exc
    return {"status": "cancelled", "execution": doc, "bypassed_plan_gate": False}


def show_execution(repo_root: Path, execution_id: str) -> dict[str, Any]:
    require_t3_exec_enabled()
    try:
        return load_execution(repo_root, execution_id)
    except T3StoreError as exc:
        raise T3ServiceError(str(exc)) from exc


def list_executions(repo_root: Path) -> dict[str, Any]:
    require_t3_exec_enabled()
    docs = store_list(repo_root)
    return {
        "count": len(docs),
        "executions": [
            {
                "execution_id": d["execution_id"],
                "plan_id": d["plan_id"],
                "status": d["status"],
                "mode": d["mode"],
                "provider": d["provider"],
                "updated_at": d["updated_at"],
            }
            for d in docs
        ],
        "approved_for_execution": False,
        "bypassed_plan_gate": False,
    }
