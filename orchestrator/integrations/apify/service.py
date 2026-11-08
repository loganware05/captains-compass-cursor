"""Apify research service — fixture search/show/list; no Actor runs."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.providers.technology_intelligence.apify_file_provider import (
    ApifyFileTechnologyIntelligenceProvider,
    load_apify_fixture_records,
)
from orchestrator.providers.technology_intelligence.apify_gates import (
    require_apify_enabled,
    require_apify_live_enabled,
)
from orchestrator.providers.technology_intelligence.mapper import (
    candidate_from_apify_shaped,
)
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates
from orchestrator.integrations.apify import store


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _packet_id(query: str) -> str:
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()[:12]
    return f"apify-research-{digest}"


def _load_schema(repo_root: Path) -> dict[str, Any]:
    path = (
        Path(repo_root)
        / "orchestrator"
        / "schemas"
        / "apify-research-packet.schema.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_packet(repo_root: Path, packet: dict[str, Any]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        # Soft validate required locks when jsonschema unavailable.
        for key in (
            "approved_for_execution",
            "authority_mutation",
            "auto_promoted",
            "called_actor",
        ):
            if packet.get(key) is not False:
                raise ValueError(f"{key} must be false")
        return
    jsonschema.validate(instance=packet, schema=_load_schema(repo_root))


def search(
    repo_root: Path,
    query: str,
    *,
    live: bool = False,
) -> dict[str, Any]:
    """Search Apify Actor fixtures (or refuse live) and persist a research packet."""
    require_apify_enabled()
    if live:
        require_apify_live_enabled()
        raise RuntimeError(
            "Live Apify search/call-actor deferred in v1.80.0; "
            "use fixture mode (omit --live)"
        )
    provider = ApifyFileTechnologyIntelligenceProvider()
    candidates = provider.discover_candidates(query, {})
    packet = {
        "schema_version": "1",
        "packet_id": _packet_id(query or "apify"),
        "provider": "apify",
        "mode": "fixture",
        "query": query,
        "created_at": _utc_now(),
        "candidates": [c.to_dict() for c in candidates],
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "called_actor": False,
        "notes": "Fixture Apify research packet — NOT APPROVED FOR EXECUTION",
    }
    _validate_packet(repo_root, packet)
    path = store.write_packet(repo_root, packet)
    return {"status": "ok", "path": str(path), "packet": packet}


def show(repo_root: Path, packet_id: str) -> dict[str, Any]:
    require_apify_enabled()
    packet = store.read_packet(repo_root, packet_id)
    if not packet:
        raise FileNotFoundError(f"apify research packet not found: {packet_id}")
    return {"status": "ok", "packet": packet}


def list_packets(repo_root: Path) -> dict[str, Any]:
    require_apify_enabled()
    packets = store.list_packets(repo_root)
    return {
        "status": "ok",
        "count": len(packets),
        "packets": [
            {
                "packet_id": p.get("packet_id"),
                "query": p.get("query"),
                "mode": p.get("mode"),
                "created_at": p.get("created_at"),
                "candidate_count": len(p.get("candidates") or []),
            }
            for p in packets
        ],
    }


def fixture_catalog() -> list[dict[str, Any]]:
    records = load_apify_fixture_records()
    candidates = [candidate_from_apify_shaped(r) for r in records]
    docs = [c.to_dict() for c in candidates]
    validate_ti_candidates(docs)
    return docs
