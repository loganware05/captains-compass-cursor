"""GitHub adapter — engineering and approval source of truth."""

from __future__ import annotations

import os
import re
from typing import Any

from orchestrator.integrations.adapters.base import FixtureAdapterBase
from orchestrator.integrations.events import normalize_event
from orchestrator.integrations.product_allowlist import require_allowed_repository
from orchestrator.integrations.state_machine import StateTransitionError, mark_plan_approved

APPROVE_RE = re.compile(r"NORTHSTAR_APPROVE\s+plan_digest=([0-9a-fA-F]{64})\b")


class GitHubAdapter(FixtureAdapterBase):
    provider = "github"

    def __init__(self, **kwargs: Any) -> None:
        mode = str(kwargs.get("mode") or "fixtures").strip().lower()
        env_ids = {
            part.strip()
            for part in (os.environ.get("NORTHSTAR_CAPTAIN_GITHUB_IDS") or "").split(",")
            if part.strip()
        }
        if mode == "live":
            # Live mode: never implicitly trust the fixture captain id.
            # Use env allowlist and/or explicitly passed captain_ids only.
            if "captain_ids" not in kwargs:
                kwargs["captain_ids"] = set(env_ids)
            else:
                kwargs["captain_ids"] = set(kwargs["captain_ids"]) | set(env_ids)
        else:
            kwargs.setdefault("captain_ids", {"captain-github"})
            if env_ids:
                kwargs["captain_ids"] = set(kwargs["captain_ids"]) | set(env_ids)
        super().__init__(**kwargs)
        self.approvals: list[dict[str, Any]] = []

    def normalize_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        if not self.connected:
            raise ConnectionError("github adapter disconnected")
        repository = (
            raw_event.get("repository")
            or self.product_repository
            or "loganware05/captains-compass-cursor"
        )
        if self.mode == "live":
            require_allowed_repository(str(repository))

        label = (raw_event.get("label") or "").casefold()
        intake_ok = label in {"northstar", "northstar-intake"} or raw_event.get(
            "intake", False
        )
        event_type = raw_event.get("event_type") or "objective"
        if event_type == "objective" and not intake_ok:
            raise ValueError("github objective requires northstar intake label")

        actor = self.verify_identity(
            {
                "provider_id": raw_event.get("actor_id") or raw_event.get("sender"),
                "verified_role": raw_event.get("role"),
            }
        )
        payload = {
            "title": raw_event.get("title"),
            "body": raw_event.get("body"),
            "label": raw_event.get("label"),
        }
        if event_type == "approval":
            payload["plan_digest"] = raw_event.get("plan_digest")
            payload["approval_ref"] = raw_event.get("approval_ref")

        return normalize_event(
            provider="github",
            event_type=event_type,
            event_id=raw_event.get("event_id") or raw_event.get("delivery_id"),
            occurred_at=raw_event.get("occurred_at"),
            actor=actor,
            product_name_received=raw_event.get("product_name"),
            repository=str(repository),
            references={
                "github_issue": raw_event.get("issue"),
                "github_pull_request": raw_event.get("pull_request"),
            },
            payload=payload,
        )

    def parse_approval_comment(self, body: str) -> str | None:
        match = APPROVE_RE.search(body or "")
        return match.group(1).lower() if match else None

    def record_canonical_approval(
        self,
        run: dict[str, Any],
        *,
        plan_id: str,
        plan_digest: str,
        actor_id: str,
        approval_ref: str,
        issue_number: Any | None = None,
    ) -> dict[str, Any]:
        actor = self.verify_identity({"provider_id": actor_id, "verified_role": "captain"})
        if actor["verified_role"] != "captain":
            raise StateTransitionError("github approval actor is not a verified Captain")
        if run.get("plan_digest") and run.get("plan_digest") != plan_digest:
            raise StateTransitionError("BLOCKED_APPROVAL: plan digest mismatch")
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
            "mode": self.mode,
            "issue_number": issue_number,
        }
        self.approvals.append(record)
        self._write_json(f"approval-{run.get('run_id')}.json", record)

        if self.mode == "live" and self.transport is not None:
            from orchestrator.integrations.adapters.live import github_api

            token = (os.environ.get("NORTHSTAR_GITHUB_TOKEN") or "").strip()
            repo = (
                self.product_repository
                or (run.get("origin_event") or {}).get("project", {}).get("repository")
            )
            issue = issue_number or (run.get("origin_event") or {}).get("references", {}).get(
                "github_issue"
            )
            if not repo:
                raise StateTransitionError(
                    "BLOCKED_CONNECTION: live approval ack requires repository"
                )
            if not issue:
                raise StateTransitionError(
                    "BLOCKED_CONNECTION: live approval ack requires issue number"
                )
            require_allowed_repository(str(repo))
            github_api(
                self.transport,
                method="POST",
                path=f"/repos/{repo}/issues/{issue}/comments",
                token=token,
                body={
                    "body": (
                        f"NorthStar recorded Captain approval for plan_digest={plan_digest}"
                    )
                },
            )
        return updated

    def create_or_update_work_item(self, run: dict[str, Any]) -> dict[str, Any]:
        item = super().create_or_update_work_item(run)
        if self.mode == "live" and self.transport is not None and self.connected:
            from orchestrator.integrations.adapters.live import github_api

            token = (os.environ.get("NORTHSTAR_GITHUB_TOKEN") or "").strip()
            repo = self.product_repository or (
                (run.get("origin_event") or {}).get("project", {}).get("repository")
            )
            if repo:
                require_allowed_repository(str(repo))
                try:
                    remote = github_api(
                        self.transport,
                        method="POST",
                        path=f"/repos/{repo}/issues",
                        token=token,
                        body={
                            "title": f"NorthStar run {run.get('run_id')}",
                            "body": f"state={run.get('state')} plan={run.get('plan_id')}",
                            "labels": ["northstar"],
                        },
                    )
                    item["remote"] = {"number": (remote or {}).get("number")}
                    self._write_json(f"work-item-{run.get('run_id')}.json", item)
                except RuntimeError:
                    # Missing token / transport failure: fail closed for live ledger write.
                    raise
        return item

    def verify_plan_digest(self, run: dict[str, Any], expected_digest: str) -> bool:
        return (
            bool(run.get("plan_approved"))
            and run.get("plan_digest") == expected_digest
            and str(run.get("github_approval_ref") or "").startswith("github:")
        )
