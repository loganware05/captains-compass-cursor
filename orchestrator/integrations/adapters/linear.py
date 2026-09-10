"""Linear adapter — work ledger with GitHub fallback (never an approval authority)."""

from __future__ import annotations

import os
from typing import Any

from orchestrator.integrations.adapters.base import FixtureAdapterBase
from orchestrator.integrations.events import normalize_event


class LinearAdapter(FixtureAdapterBase):
    provider = "linear"

    def __init__(self, *, project_allowlist: set[str] | None = None, **kwargs: Any) -> None:
        kwargs.setdefault("captain_ids", {"captain-linear"})
        super().__init__(**kwargs)
        self.project_allowlist = project_allowlist or {"NorthStar", "northstar"}
        self.children: list[dict[str, Any]] = []

    def normalize_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        if not self.connected:
            raise ConnectionError("linear adapter disconnected")
        project = raw_event.get("project") or ""
        if project and project not in self.project_allowlist:
            raise ValueError(f"linear project not allowlisted: {project!r}")
        actor = self.verify_identity(
            {
                "provider_id": raw_event.get("actor_id"),
                "verified_role": raw_event.get("role"),
            }
        )
        return normalize_event(
            provider="linear",
            event_type=raw_event.get("event_type") or "work_item_changed",
            event_id=raw_event.get("event_id"),
            occurred_at=raw_event.get("occurred_at"),
            actor=actor,
            product_name_received=raw_event.get("product_name"),
            repository=raw_event.get("repository") or self.product_repository
            or "loganware05/captains-compass-cursor",
            references={"linear_issue": raw_event.get("issue")},
            payload={
                "title": raw_event.get("title"),
                "status": raw_event.get("status"),
                "project": project,
                "parent": raw_event.get("parent"),
                "depends_on": raw_event.get("depends_on") or [],
            },
        )

    def create_or_update_work_item(self, run: dict[str, Any]) -> dict[str, Any]:
        # Linear never sets plan_approved / never calls mark_plan_approved.
        if not self.connected:
            return {
                "ok": False,
                "fallback": "github",
                "reason": "linear_unavailable",
                "run_id": run.get("run_id"),
            }
        parent = {
            "provider": "linear",
            "kind": "initiative",
            "run_id": run.get("run_id"),
            "label": "northstar",
            "state": run.get("state"),
            "title": f"NorthStar run {run.get('run_id')}",
            "mode": self.mode,
        }
        self.work_items.append(parent)
        for stream in run.get("workstreams") or []:
            child = {
                "provider": "linear",
                "kind": "workstream",
                "run_id": run.get("run_id"),
                "stream_id": stream.get("id"),
                "depends_on": stream.get("depends_on") or [],
                "owner": stream.get("owner"),
                "status": stream.get("status") or run.get("state"),
                "acceptance": stream.get("acceptance") or [],
                "pr": (run.get("references") or {}).get("github_pull_request"),
            }
            self.children.append(child)
        self._write_json(f"linear-parent-{run.get('run_id')}.json", parent)

        if self.mode == "live" and self.transport is not None:
            from orchestrator.integrations.adapters.live import linear_graphql

            api_key = (os.environ.get("NORTHSTAR_LINEAR_API_KEY") or "").strip()
            linear_graphql(
                self.transport,
                query=(
                    "mutation CreateIssue($title: String!) {"
                    " issueCreate(input: {title: $title}) { success } }"
                ),
                variables={"title": parent["title"]},
                api_key=api_key,
            )
        return parent

    def reconcile(self, run: dict[str, Any]) -> dict[str, Any]:
        if not self.connected:
            return {
                "provider": "linear",
                "ok": False,
                "fallback": "github",
                "run_id": run.get("run_id"),
            }
        for child in self.children:
            if child.get("run_id") == run.get("run_id"):
                child["status"] = run.get("state")
                child["pr"] = (run.get("references") or {}).get("github_pull_request")
        return {
            "provider": "linear",
            "ok": True,
            "run_id": run.get("run_id"),
            "state": run.get("state"),
            "mode": self.mode,
        }

    def record_approval_intent(self, run: dict[str, Any], *, actor_id: str) -> dict[str, Any]:
        """Linear may record intent only — never authorizes Cursor."""
        actor = self.verify_identity({"provider_id": actor_id, "verified_role": "captain"})
        return {
            "kind": "approval_intent",
            "authoritative": False,
            "requires_github_approval": True,
            "run_id": run.get("run_id"),
            "actor": actor,
            "accepted": False,
            "provider": "linear",
        }
