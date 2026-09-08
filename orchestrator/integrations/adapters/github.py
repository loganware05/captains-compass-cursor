"""GitHub adapter — engineering and approval source of truth."""

from __future__ import annotations

from typing import Any

from orchestrator.integrations.adapters.base import FixtureAdapterBase
from orchestrator.integrations.events import normalize_event
from orchestrator.integrations.state_machine import StateTransitionError, mark_plan_approved


class GitHubAdapter(FixtureAdapterBase):
    provider = "github"

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("captain_ids", {"captain-github"})
        super().__init__(**kwargs)
        self.approvals: list[dict[str, Any]] = []

    def normalize_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        if not self.connected:
            raise ConnectionError("github adapter disconnected")
        label = (raw_event.get("label") or "").casefold()
        intake_ok = label in {"northstar", "northstar-intake"} or raw_event.get(
            "intake", False
        )
        if raw_event.get("event_type") == "objective" and not intake_ok:
            raise ValueError("github objective requires northstar intake label")

        actor = self.verify_identity(
            {
                "provider_id": raw_event.get("actor_id") or raw_event.get("sender"),
                "verified_role": raw_event.get("role"),
            }
        )
        return normalize_event(
            provider="github",
            event_type=raw_event.get("event_type") or "objective",
            event_id=raw_event.get("event_id") or raw_event.get("delivery_id"),
            occurred_at=raw_event.get("occurred_at"),
            actor=actor,
            product_name_received=raw_event.get("product_name"),
            repository=raw_event.get("repository") or "loganware05/captains-compass-cursor",
            references={
                "github_issue": raw_event.get("issue"),
                "github_pull_request": raw_event.get("pull_request"),
            },
            payload={
                "title": raw_event.get("title"),
                "body": raw_event.get("body"),
                "label": raw_event.get("label"),
            },
        )

    def record_canonical_approval(
        self,
        run: dict[str, Any],
        *,
        plan_id: str,
        plan_digest: str,
        actor_id: str,
        approval_ref: str,
    ) -> dict[str, Any]:
        actor = self.verify_identity({"provider_id": actor_id, "verified_role": "captain"})
        if actor["verified_role"] != "captain":
            raise StateTransitionError("github approval actor is not a verified Captain")
        updated = mark_plan_approved(
            run,
            plan_id=plan_id,
            plan_digest=plan_digest,
            captain_actor=actor,
            github_approval_ref=approval_ref,
        )
        record = {
            "run_id": run.get("run_id"),
            "plan_id": plan_id,
            "plan_digest": plan_digest,
            "approval_ref": approval_ref,
            "actor": actor,
        }
        self.approvals.append(record)
        self._write_json(f"approval-{run.get('run_id')}.json", record)
        return updated

    def verify_plan_digest(self, run: dict[str, Any], expected_digest: str) -> bool:
        return bool(run.get("plan_approved")) and run.get("plan_digest") == expected_digest
