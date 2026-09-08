"""Normalized event helpers: digests, idempotency, and product identity."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from orchestrator.branding import (
    display_name,
    legacy_alias_received,
    normalize_product_name,
)
from orchestrator.integrations.contracts import DEFAULT_REPOSITORY, M21_INTEGRATION_AGENT_ID


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_hex(payload: Any) -> str:
    if isinstance(payload, (bytes, bytearray)):
        data = bytes(payload)
    elif isinstance(payload, str):
        data = payload.encode("utf-8")
    else:
        data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_idempotency_key(
    *,
    provider: str,
    event_id: str,
    event_type: str,
    repository: str,
    payload_digest: str,
) -> str:
    return sha256_hex(
        {
            "provider": provider,
            "event_id": event_id,
            "event_type": event_type,
            "repository": repository,
            "payload_digest": payload_digest,
        }
    )


def normalize_event(
    *,
    provider: str,
    event_type: str,
    event_id: str | None = None,
    occurred_at: str | None = None,
    actor: dict[str, Any] | None = None,
    product_name_received: str | None = None,
    repository: str = DEFAULT_REPOSITORY,
    references: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    cursor_agent: str | None = M21_INTEGRATION_AGENT_ID,
) -> dict[str, Any]:
    """Build the M21 normalized event contract."""
    payload = payload or {}
    refs = {
        "slack_thread": None,
        "linear_issue": None,
        "github_issue": None,
        "github_pull_request": None,
        "cursor_agent": cursor_agent,
    }
    if references:
        refs.update(references)

    actor_obj = {
        "provider_id": (actor or {}).get("provider_id") or "unknown",
        "verified_role": (actor or {}).get("verified_role") or "collaborator",
    }
    payload_digest = sha256_hex(payload)
    eid = event_id or f"{provider}-{uuid4().hex[:12]}"
    repo = repository or DEFAULT_REPOSITORY
    idem = build_idempotency_key(
        provider=provider,
        event_id=eid,
        event_type=event_type,
        repository=repo,
        payload_digest=payload_digest,
    )
    return {
        "event_id": eid,
        "provider": provider,
        "event_type": event_type,
        "occurred_at": occurred_at or utc_now(),
        "actor": actor_obj,
        "product": {
            "name": display_name(),
            "legacy_alias_received": legacy_alias_received(product_name_received),
            "normalized_from": normalize_product_name(product_name_received)
            if product_name_received
            else display_name(),
        },
        "project": {"repository": repo},
        "references": refs,
        "payload": payload,
        "payload_digest": payload_digest,
        "idempotency_key": idem,
    }


class IdempotencyStore:
    """Append-only in-memory / JSON-file dedupe store."""

    def __init__(self, path: Any | None = None) -> None:
        self.path = path
        self._seen: set[str] = set()
        if path is not None:
            from pathlib import Path

            p = Path(path)
            if p.is_file():
                data = json.loads(p.read_text(encoding="utf-8"))
                self._seen = set(data.get("keys") or [])

    def seen(self, event_id: str, idempotency_key: str) -> bool:
        token = f"{event_id}:{idempotency_key}"
        return token in self._seen

    def remember(self, event_id: str, idempotency_key: str) -> bool:
        """Return True if this is the first observation; False if duplicate."""
        token = f"{event_id}:{idempotency_key}"
        if token in self._seen:
            return False
        self._seen.add(token)
        self._persist()
        return True

    def _persist(self) -> None:
        if self.path is None:
            return
        from pathlib import Path

        p = Path(self.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps({"keys": sorted(self._seen)}, indent=2) + "\n",
            encoding="utf-8",
        )


def redact_secrets(value: Any) -> Any:
    """Redact common secret-shaped fields from structures copied to logs/Slack."""
    secret_keys = {
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "api_key",
        "apikey",
        "secret",
        "password",
        "webhook_secret",
        "private_key",
    }
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if key.casefold() in secret_keys or key.casefold().endswith("_token"):
                out[key] = "[REDACTED]"
            else:
                out[key] = redact_secrets(item)
        return out
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value
