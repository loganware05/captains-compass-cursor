"""Slack adapter — intake + transition notifications (not an approval authority)."""

from __future__ import annotations

from typing import Any

from orchestrator.integrations.adapters.base import FixtureAdapterBase
from orchestrator.integrations.contracts import SLACK_TRANSITIONS
from orchestrator.integrations.events import normalize_event, redact_secrets


class SlackAdapter(FixtureAdapterBase):
    provider = "slack"

    def __init__(
        self,
        *,
        channel_allowlist: set[str] | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("captain_ids", {"captain-slack"})
        super().__init__(**kwargs)
        self.channel_allowlist = channel_allowlist or {"northstar", "C-NORTHSTAR"}

    def normalize_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        if not self.connected:
            raise ConnectionError("slack adapter disconnected")
        channel = raw_event.get("channel") or ""
        if channel and channel not in self.channel_allowlist:
            raise ValueError(f"slack channel not allowlisted: {channel!r}")

        text = raw_event.get("text") or ""
        mentions = raw_event.get("mentions") or []
        mention_ok = (
            "@NorthStar" in text
            or "NorthStar" in mentions
            or "@CaptainCompass" in text
            or "CaptainCompass" in mentions
        )
        if raw_event.get("event_type", "objective") == "objective" and not mention_ok:
            raise ValueError("slack objective requires @NorthStar mention (or legacy @CaptainCompass)")

        product_name = "Captain's Compass" if (
            "@CaptainCompass" in text or "CaptainCompass" in mentions
        ) and "@NorthStar" not in text else raw_event.get("product_name")

        actor = self.verify_identity(
            {
                "provider_id": raw_event.get("user_id") or raw_event.get("actor_id"),
                "verified_role": raw_event.get("role"),
            }
        )
        return normalize_event(
            provider="slack",
            event_type=raw_event.get("event_type") or "objective",
            event_id=raw_event.get("event_id") or raw_event.get("ts"),
            occurred_at=raw_event.get("occurred_at"),
            actor=actor,
            product_name_received=product_name,
            references={"slack_thread": raw_event.get("thread_ts") or raw_event.get("ts")},
            payload=redact_secrets(
                {
                    "text": text,
                    "channel": channel,
                    "mentions": mentions,
                }
            ),
        )

    def publish_transition(self, run: dict[str, Any], transition: str) -> dict[str, Any]:
        if transition not in SLACK_TRANSITIONS:
            raise ValueError(f"slack transition not allowlisted: {transition!r}")
        if not self.connected:
            return {
                "ok": False,
                "suppressed": True,
                "reason": "slack_unavailable",
                "transition": transition,
            }
        thread = (run.get("references") or {}).get("slack_thread")
        msg = {
            "provider": "slack",
            "run_id": run.get("run_id"),
            "transition": transition,
            "state": run.get("state"),
            "thread_ts": thread,
            "text": f"NorthStar: {transition.replace('_', ' ')} ({run.get('state')})",
        }
        self.published.append(msg)
        self._write_json(f"slack-{run.get('run_id')}-{transition}.json", msg)
        return msg

    def record_approval_intent(
        self,
        run: dict[str, Any],
        *,
        actor_id: str,
    ) -> dict[str, Any]:
        """Record Slack approval intent — never authorizes Cursor by itself."""
        actor = self.verify_identity({"provider_id": actor_id, "verified_role": "captain"})
        return {
            "kind": "approval_intent",
            "authoritative": False,
            "requires_github_approval": True,
            "run_id": run.get("run_id"),
            "actor": actor,
            "accepted": actor.get("verified_role") == "captain",
        }
