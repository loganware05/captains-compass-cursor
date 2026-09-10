"""Shared fixture-backed adapter helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.integrations.events import IdempotencyStore, redact_secrets, utc_now
from orchestrator.integrations.transport import HttpTransport


class FixtureAdapterBase:
    """Common storage + dedupe for recorded-fixture adapters (no live credentials)."""

    provider: str = "base"

    def __init__(
        self,
        *,
        store_dir: Path | None = None,
        allowlist: set[str] | None = None,
        captain_ids: set[str] | None = None,
        connected: bool = True,
        mode: str = "fixtures",
        transport: HttpTransport | None = None,
        product_repository: str | None = None,
    ) -> None:
        mode_n = (mode or "fixtures").strip().lower()
        if mode_n in {"fixture", "fixtures"}:
            mode_n = "fixtures"
        elif mode_n != "live":
            raise ValueError(f"unknown adapter mode: {mode!r}")
        self.mode = mode_n
        self.transport = transport
        self.product_repository = product_repository
        self.store_dir = Path(store_dir) if store_dir else None
        self.allowlist = allowlist or set()
        self.captain_ids = captain_ids or set()
        self.connected = connected
        self._idem = IdempotencyStore(
            (self.store_dir / "idempotency.json") if self.store_dir else None
        )
        self.published: list[dict[str, Any]] = []
        self.work_items: list[dict[str, Any]] = []
        if self.store_dir:
            self.store_dir.mkdir(parents=True, exist_ok=True)
        if self.mode == "live" and self.transport is None:
            raise RuntimeError(
                f"BLOCKED_CONNECTION: {self.provider} live mode requires transport"
            )

    def healthcheck(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "ok": bool(self.connected),
            "mode": self.mode,
            "checked_at": utc_now(),
        }

    def deduplicate(self, event_id: str, idempotency_key: str) -> bool:
        """Return True when the event is NEW (should be processed)."""
        return self._idem.remember(event_id, idempotency_key)

    def verify_identity(self, actor: dict[str, Any]) -> dict[str, Any]:
        provider_id = str((actor or {}).get("provider_id") or "")
        claimed = (actor or {}).get("verified_role") or "collaborator"
        if provider_id and provider_id in self.captain_ids:
            role = "captain"
        elif claimed in {"first_mate", "agent", "collaborator", "captain"}:
            # Captain role requires allowlisted identity — never trust claim alone.
            role = "collaborator" if claimed == "captain" else claimed
        else:
            role = "collaborator"
        return {
            "provider_id": provider_id or "unknown",
            "verified_role": role,
            "verified": True,
        }

    def _write_json(self, name: str, payload: dict[str, Any]) -> Path | None:
        if not self.store_dir:
            return None
        path = self.store_dir / name
        path.write_text(
            json.dumps(redact_secrets(payload), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path

    def create_or_update_work_item(self, run: dict[str, Any]) -> dict[str, Any]:
        item = {
            "provider": self.provider,
            "run_id": run.get("run_id"),
            "state": run.get("state"),
            "updated_at": utc_now(),
        }
        self.work_items.append(item)
        self._write_json(f"work-item-{run.get('run_id')}.json", item)
        return item

    def publish_transition(self, run: dict[str, Any], transition: str) -> dict[str, Any]:
        msg = {
            "provider": self.provider,
            "run_id": run.get("run_id"),
            "transition": transition,
            "state": run.get("state"),
            "at": utc_now(),
        }
        self.published.append(msg)
        self._write_json(f"transition-{run.get('run_id')}-{transition}.json", msg)
        return msg

    def link_artifacts(self, run: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "provider": self.provider,
            "run_id": run.get("run_id"),
            "references": run.get("references") or {},
            "at": utc_now(),
        }
        self._write_json(f"links-{run.get('run_id')}.json", payload)
        return payload

    def reconcile(self, run: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "run_id": run.get("run_id"),
            "state": run.get("state"),
            "ok": True,
        }

    def read_context(self, reference: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "reference": reference,
            "mode": self.mode,
        }

    def normalize_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
