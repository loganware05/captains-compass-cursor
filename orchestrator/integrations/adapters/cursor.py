"""Cursor adapter — execution runtime with M21 agent identity enforcement."""

from __future__ import annotations

from typing import Any

from orchestrator.integrations.adapters.base import FixtureAdapterBase
from orchestrator.integrations.contracts import M21_INTEGRATION_AGENT_ID
from orchestrator.integrations.events import normalize_event, sha256_hex, utc_now
from orchestrator.integrations.state_machine import StateTransitionError


class CursorAdapter(FixtureAdapterBase):
    provider = "cursor"

    def __init__(self, *, allowed_agent_id: str = M21_INTEGRATION_AGENT_ID, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.allowed_agent_id = allowed_agent_id
        self.dispatched: list[dict[str, Any]] = []
        self.checkpoints: list[dict[str, Any]] = []

    def normalize_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        if not self.connected:
            raise ConnectionError("cursor adapter disconnected")
        agent_id = raw_event.get("agent_id") or raw_event.get("cursor_agent")
        actor = self.verify_identity(
            {
                "provider_id": raw_event.get("actor_id") or agent_id,
                "verified_role": raw_event.get("role") or "agent",
            }
        )
        return normalize_event(
            provider="cursor",
            event_type=raw_event.get("event_type") or "checkpoint",
            event_id=raw_event.get("event_id"),
            occurred_at=raw_event.get("occurred_at"),
            actor=actor,
            product_name_received=raw_event.get("product_name"),
            references={"cursor_agent": agent_id},
            payload={
                "checkpoint": raw_event.get("checkpoint"),
                "evidence_path": raw_event.get("evidence_path"),
                "state_hint": raw_event.get("state_hint"),
            },
            cursor_agent=agent_id,
        )

    def build_work_packet(self, run: dict[str, Any]) -> dict[str, Any]:
        if not run.get("plan_approved"):
            raise StateTransitionError("cannot build work packet before canonical approval")
        packet = {
            "kind": "northstar-work-packet",
            "run_id": run.get("run_id"),
            "plan_id": run.get("plan_id"),
            "plan_digest": run.get("plan_digest"),
            "repository": (run.get("origin_event") or {}).get("project", {}).get(
                "repository"
            ),
            "allowed_agent_id": self.allowed_agent_id,
            "github_approval_ref": run.get("github_approval_ref"),
            "objective": ((run.get("origin_event") or {}).get("payload") or {}).get("title")
            or ((run.get("origin_event") or {}).get("payload") or {}).get("text"),
            "created_at": utc_now(),
        }
        packet["packet_digest"] = sha256_hex(packet)
        return packet

    def dispatch(self, run: dict[str, Any], work_packet: dict[str, Any]) -> dict[str, Any]:
        if not run.get("plan_approved"):
            raise StateTransitionError("cannot dispatch before canonical approval")
        if not str(run.get("github_approval_ref") or "").startswith("github:"):
            raise StateTransitionError("dispatch requires github_approval_ref")
        if work_packet.get("plan_digest") != run.get("plan_digest"):
            raise StateTransitionError("work packet plan_digest mismatch")
        if not self.connected:
            # Missing Cursor: leave launch-ready packet and stop.
            return {
                "ok": False,
                "reason": "cursor_unavailable",
                "work_packet": work_packet,
            }
        record = {
            "run_id": run.get("run_id"),
            "agent_id": self.allowed_agent_id,
            "packet_digest": work_packet.get("packet_digest"),
            "at": utc_now(),
        }
        self.dispatched.append(record)
        self._write_json(f"dispatch-{run.get('run_id')}.json", record)
        return {"ok": True, "dispatch": record, "work_packet": work_packet}

    def accept_checkpoint(
        self,
        raw_checkpoint: dict[str, Any],
        *,
        run: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        agent_id = raw_checkpoint.get("agent_id")
        if agent_id != self.allowed_agent_id:
            raise StateTransitionError(
                f"BLOCKED_AGENT_IDENTITY: expected {self.allowed_agent_id}, got {agent_id!r}"
            )
        if run is not None:
            state = run.get("state")
            if state not in {"DISPATCHED", "IN_PROGRESS", "VALIDATING"}:
                raise StateTransitionError(
                    f"checkpoint rejected for run state {state!r}"
                )
            if raw_checkpoint.get("run_id") != run.get("run_id"):
                raise StateTransitionError("checkpoint requires matching run_id")
            packet = run.get("work_packet") or {}
            expected_digest = packet.get("packet_digest")
            if not expected_digest or raw_checkpoint.get("packet_digest") != expected_digest:
                raise StateTransitionError("checkpoint packet_digest mismatch")
        event = self.normalize_event(
            {
                **raw_checkpoint,
                "event_type": "checkpoint",
                "agent_id": agent_id,
            }
        )
        self.checkpoints.append(event)
        self._write_json(
            f"checkpoint-{event['event_id']}.json",
            event,
        )
        return event
