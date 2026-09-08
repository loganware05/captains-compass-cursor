"""Shared contracts for NorthStar connected-system adapters."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

# Only this Cursor cloud agent may be accepted for M21 integration checkpoints.
M21_INTEGRATION_AGENT_ID = "bc-05d4594d-fac7-4378-b595-c20e3c006044"

DEFAULT_REPOSITORY = "loganware05/captains-compass-cursor"

NORMAL_STATES = (
    "RECEIVED",
    "RECONCILING",
    "PLAN_PROPOSED",
    "AWAITING_CAPTAIN_APPROVAL",
    "DISPATCHED",
    "IN_PROGRESS",
    "VALIDATING",
    "REVIEW_READY",
    "AWAITING_MERGE",
    "COMPLETED",
)

EXCEPTION_STATES = (
    "BLOCKED_CONNECTION",
    "BLOCKED_APPROVAL",
    "BLOCKED_AGENT_IDENTITY",
    "BLOCKED_SCOPE",
    "BUDGET_STOPPED",
    "VALIDATION_FAILED",
    "CANCELLED",
    "SUPERSEDED",
)

ALL_STATES = NORMAL_STATES + EXCEPTION_STATES

SLACK_TRANSITIONS = (
    "work_received",
    "plan_awaiting_approval",
    "execution_started",
    "blocked_or_budget_stopped",
    "review_ready",
    "completed",
)

PROVIDERS = ("slack", "linear", "github", "cursor")


@runtime_checkable
class ConnectorAdapter(Protocol):
    """Provider adapter interface required by M21."""

    provider: str

    def healthcheck(self) -> dict[str, Any]:
        ...

    def normalize_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        ...

    def read_context(self, reference: dict[str, Any]) -> dict[str, Any]:
        ...

    def verify_identity(self, actor: dict[str, Any]) -> dict[str, Any]:
        ...

    def deduplicate(self, event_id: str, idempotency_key: str) -> bool:
        ...

    def create_or_update_work_item(self, run: dict[str, Any]) -> dict[str, Any]:
        ...

    def publish_transition(self, run: dict[str, Any], transition: str) -> dict[str, Any]:
        ...

    def link_artifacts(self, run: dict[str, Any]) -> dict[str, Any]:
        ...

    def reconcile(self, run: dict[str, Any]) -> dict[str, Any]:
        ...
