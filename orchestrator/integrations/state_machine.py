"""NorthStar run state machine with append-only transition log."""

from __future__ import annotations

from typing import Any

from orchestrator.integrations.contracts import ALL_STATES, EXCEPTION_STATES, NORMAL_STATES
from orchestrator.integrations.events import sha256_hex, utc_now

# Allowed normal-path edges.
_NORMAL_EDGES: dict[str, frozenset[str]] = {
    "RECEIVED": frozenset({"RECONCILING", "CANCELLED", "SUPERSEDED"}),
    "RECONCILING": frozenset({"PLAN_PROPOSED", "BLOCKED_CONNECTION", "CANCELLED", "SUPERSEDED"}),
    "PLAN_PROPOSED": frozenset(
        {"AWAITING_CAPTAIN_APPROVAL", "BLOCKED_SCOPE", "CANCELLED", "SUPERSEDED"}
    ),
    "AWAITING_CAPTAIN_APPROVAL": frozenset(
        {"DISPATCHED", "BLOCKED_APPROVAL", "CANCELLED", "SUPERSEDED"}
    ),
    "DISPATCHED": frozenset(
        {"IN_PROGRESS", "BLOCKED_AGENT_IDENTITY", "BLOCKED_CONNECTION", "CANCELLED"}
    ),
    "IN_PROGRESS": frozenset(
        {
            "VALIDATING",
            "BLOCKED_SCOPE",
            "BUDGET_STOPPED",
            "VALIDATION_FAILED",
            "CANCELLED",
        }
    ),
    "VALIDATING": frozenset(
        {"REVIEW_READY", "VALIDATION_FAILED", "BUDGET_STOPPED", "CANCELLED"}
    ),
    "REVIEW_READY": frozenset({"AWAITING_MERGE", "VALIDATION_FAILED", "CANCELLED"}),
    "AWAITING_MERGE": frozenset({"COMPLETED", "CANCELLED", "SUPERSEDED"}),
    "COMPLETED": frozenset(),
}

# Exception states may recover to a subset of normal states or stay terminal.
_EXCEPTION_EDGES: dict[str, frozenset[str]] = {
    "BLOCKED_CONNECTION": frozenset({"RECONCILING", "CANCELLED", "SUPERSEDED"}),
    "BLOCKED_APPROVAL": frozenset({"AWAITING_CAPTAIN_APPROVAL", "CANCELLED", "SUPERSEDED"}),
    "BLOCKED_AGENT_IDENTITY": frozenset({"DISPATCHED", "CANCELLED", "SUPERSEDED"}),
    "BLOCKED_SCOPE": frozenset({"PLAN_PROPOSED", "AWAITING_CAPTAIN_APPROVAL", "CANCELLED"}),
    "BUDGET_STOPPED": frozenset({"CANCELLED", "SUPERSEDED"}),
    "VALIDATION_FAILED": frozenset({"IN_PROGRESS", "CANCELLED", "SUPERSEDED"}),
    "CANCELLED": frozenset(),
    "SUPERSEDED": frozenset(),
}


class StateTransitionError(ValueError):
    """Raised when a transition is illegal or a run is malformed."""


def allowed_next_states(current: str) -> frozenset[str]:
    if current in _NORMAL_EDGES:
        return _NORMAL_EDGES[current]
    if current in _EXCEPTION_EDGES:
        return _EXCEPTION_EDGES[current]
    raise StateTransitionError(f"unknown state: {current}")


def new_run(
    *,
    run_id: str,
    origin_event: dict[str, Any],
    plan_id: str | None = None,
) -> dict[str, Any]:
    now = utc_now()
    plan_digest = sha256_hex({"plan_id": plan_id or "", "status": "proposed"})
    transition = {
        "at": now,
        "actor": origin_event.get("actor") or {"provider_id": "system", "verified_role": "first_mate"},
        "origin": origin_event.get("provider"),
        "previous_state": None,
        "next_state": "RECEIVED",
        "event_digest": origin_event.get("payload_digest"),
        "plan_digest": plan_digest,
        "correlation_ids": {
            "run_id": run_id,
            "event_id": origin_event.get("event_id"),
            "idempotency_key": origin_event.get("idempotency_key"),
        },
    }
    return {
        "run_id": run_id,
        "state": "RECEIVED",
        "plan_id": plan_id,
        "plan_digest": plan_digest,
        "plan_approved": False,
        "origin_event": origin_event,
        "references": dict(origin_event.get("references") or {}),
        "work_packet": None,
        "transitions": [transition],
        "created_at": now,
        "updated_at": now,
        "product": "NorthStar",
    }


def transition_run(
    run: dict[str, Any],
    next_state: str,
    *,
    actor: dict[str, Any] | None = None,
    origin: str | None = None,
    event_digest: str | None = None,
    plan_digest: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    current = run.get("state")
    if current not in ALL_STATES:
        raise StateTransitionError(f"run has unknown state: {current!r}")
    if next_state not in ALL_STATES:
        raise StateTransitionError(f"unknown next state: {next_state!r}")
    allowed = allowed_next_states(current)
    if next_state not in allowed:
        raise StateTransitionError(
            f"illegal transition {current} -> {next_state}; allowed={sorted(allowed)}"
        )

    now = utc_now()
    entry = {
        "at": now,
        "actor": actor
        or {"provider_id": "first-mate", "verified_role": "first_mate"},
        "origin": origin or "northstar",
        "previous_state": current,
        "next_state": next_state,
        "event_digest": event_digest or run.get("origin_event", {}).get("payload_digest"),
        "plan_digest": plan_digest or run.get("plan_digest"),
        "correlation_ids": {
            "run_id": run.get("run_id"),
            "event_id": (run.get("origin_event") or {}).get("event_id"),
            "idempotency_key": (run.get("origin_event") or {}).get("idempotency_key"),
        },
    }
    if reason:
        entry["reason"] = reason

    run = dict(run)
    run["state"] = next_state
    run["updated_at"] = now
    if plan_digest:
        run["plan_digest"] = plan_digest
    transitions = list(run.get("transitions") or [])
    transitions.append(entry)
    run["transitions"] = transitions

    if next_state in EXCEPTION_STATES:
        run["blocked"] = True
        run["block_reason"] = reason or next_state
    elif next_state in NORMAL_STATES:
        run["blocked"] = False
        run.pop("block_reason", None)
    return run


def mark_plan_approved(
    run: dict[str, Any],
    *,
    plan_id: str,
    plan_digest: str,
    captain_actor: dict[str, Any],
    github_approval_ref: str,
) -> dict[str, Any]:
    """Record canonical GitHub approval. Does not dispatch by itself."""
    if (captain_actor or {}).get("verified_role") != "captain":
        raise StateTransitionError("canonical approval requires verified_role=captain")
    if not github_approval_ref:
        raise StateTransitionError("canonical approval requires github_approval_ref")
    run = dict(run)
    run["plan_id"] = plan_id
    run["plan_digest"] = plan_digest
    run["plan_approved"] = True
    run["github_approval_ref"] = github_approval_ref
    run["approval_actor"] = captain_actor
    return run
