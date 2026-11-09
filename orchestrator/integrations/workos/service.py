"""WorkOS identity service — fixture sync/show/list; no live API."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.integrations.workos import store
from orchestrator.integrations.workos.gates import (
    require_identity_enabled,
    require_identity_live_enabled,
    workos_api_key,
)

DEFAULT_FIXTURES = (
    Path(__file__).resolve().parent / "fixtures" / "memberships.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _packet_id(org_id: str) -> str:
    digest = hashlib.sha256(org_id.encode("utf-8")).hexdigest()[:12]
    return f"workos-identity-{digest}"


def _fixtures_path() -> Path:
    override = os.environ.get("COMPASS_WORKOS_FIXTURES", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_FIXTURES


def _load_schema(repo_root: Path) -> dict[str, Any]:
    path = (
        Path(repo_root)
        / "orchestrator"
        / "schemas"
        / "workos-identity-packet.schema.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_packet(repo_root: Path, packet: dict[str, Any]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        for key in (
            "approved_for_execution",
            "authority_mutation",
            "grants_captain_approval",
            "live_synced",
        ):
            if packet.get(key) is not False:
                raise ValueError(f"{key} must be false")
        return
    jsonschema.validate(instance=packet, schema=_load_schema(repo_root))


def _load_fixture() -> dict[str, Any]:
    path = _fixtures_path()
    if not path.is_file():
        raise FileNotFoundError(f"workos fixtures missing: {path}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("workos fixtures must be a JSON object")
    return doc


def sync(
    repo_root: Path,
    *,
    live: bool = False,
) -> dict[str, Any]:
    """Sync fixture WorkOS membership catalog into an identity packet."""
    require_identity_enabled()
    if live:
        require_identity_live_enabled()
        if not workos_api_key():
            raise PermissionError(
                "identity live requires COMPASS_WORKOS_API_KEY or WORKOS_API_KEY"
            )
        raise RuntimeError(
            "Live WorkOS API sync deferred in v1.82.0; "
            "use fixture mode (omit --live). "
            "WorkOS roles never grant Captain approval."
        )
    raw = _load_fixture()
    org = raw.get("organization") if isinstance(raw.get("organization"), dict) else {}
    org_id = str(org.get("id") or "org_unknown")
    packet = {
        "schema_version": "1",
        "packet_id": _packet_id(org_id),
        "provider": "workos",
        "mode": "fixture",
        "created_at": _utc_now(),
        "organization": {
            "id": org_id,
            "name": str(org.get("name") or "Unknown Org"),
        },
        "users": list(raw.get("users") or []),
        "memberships": list(raw.get("memberships") or []),
        "approved_for_execution": False,
        "authority_mutation": False,
        "grants_captain_approval": False,
        "live_synced": False,
        "notes": (
            "Fixture WorkOS AuthKit identity packet — NOT LIVE SYNCED. "
            "Roles are advisory evidence only; never replace GitHub Captain approval."
        ),
    }
    _validate_packet(repo_root, packet)
    path = store.write_packet(repo_root, packet)
    return {"status": "ok", "path": str(path), "packet": packet}


def show(repo_root: Path, packet_id: str) -> dict[str, Any]:
    require_identity_enabled()
    packet = store.read_packet(repo_root, packet_id)
    if not packet:
        raise FileNotFoundError(f"workos identity packet not found: {packet_id}")
    return {"status": "ok", "packet": packet}


def list_packets(repo_root: Path) -> dict[str, Any]:
    require_identity_enabled()
    packets = store.list_packets(repo_root)
    return {
        "status": "ok",
        "count": len(packets),
        "packets": [
            {
                "packet_id": p.get("packet_id"),
                "organization_id": (p.get("organization") or {}).get("id")
                if isinstance(p.get("organization"), dict)
                else "",
                "mode": p.get("mode"),
                "created_at": p.get("created_at"),
                "membership_count": len(p.get("memberships") or []),
                "grants_captain_approval": False,
            }
            for p in packets
        ],
    }
