"""Scrimba Explain service — fixture create/show/list; no live MCP stream."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.integrations.scrimba import store
from orchestrator.integrations.scrimba.gates import (
    require_explain_enabled,
    require_explain_live_enabled,
)

DEFAULT_MCP = "https://scrimba.com/explain/mcp"
PR_MCP = "https://scrimba.com/explain/pr/mcp"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _packet_id(topic: str) -> str:
    digest = hashlib.sha256(topic.encode("utf-8")).hexdigest()[:12]
    return f"scrimba-explain-{digest}"


def _load_schema(repo_root: Path) -> dict[str, Any]:
    path = (
        Path(repo_root)
        / "orchestrator"
        / "schemas"
        / "scrimba-explainer-packet.schema.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_packet(repo_root: Path, packet: dict[str, Any]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        for key in (
            "approved_for_execution",
            "authority_mutation",
            "auto_published",
            "streamed_live",
        ):
            if packet.get(key) is not False:
                raise ValueError(f"{key} must be false")
        return
    jsonschema.validate(instance=packet, schema=_load_schema(repo_root))


def _fixture_slides(topic: str) -> list[dict[str, str]]:
    return [
        {
            "title": "Overview",
            "narration": f"Fixture overview for: {topic}",
            "code": "",
        },
        {
            "title": "Key points",
            "narration": (
                "This is a NorthStar fixture explainer packet. "
                "Live Scrimba MCP streaming is deferred; "
                "auto_published remains false."
            ),
            "code": "# fixture — not streamed to Scrimba",
        },
        {
            "title": "Next steps",
            "narration": (
                "Captain may approve a follow-on to enable live MCP streaming "
                "under COMPASS_EXPLAIN_LIVE. Claiming Scrimba drafts stays manual."
            ),
            "code": "",
        },
    ]


def create(
    repo_root: Path,
    topic: str,
    *,
    live: bool = False,
    mcp: str = "main",
) -> dict[str, Any]:
    """Create a fixture explainer packet (or refuse live stream)."""
    require_explain_enabled()
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("topic is required")
    if live:
        require_explain_live_enabled()
        raise RuntimeError(
            "Live Scrimba MCP streaming deferred in v1.81.0; "
            "use fixture mode (omit --live). "
            f"Documented endpoints: {DEFAULT_MCP} and {PR_MCP}"
        )
    endpoint = PR_MCP if mcp.strip().lower() in {"pr", "pull", "pull-request"} else DEFAULT_MCP
    packet = {
        "schema_version": "1",
        "packet_id": _packet_id(topic),
        "provider": "fixture",
        "mode": "fixture",
        "topic": topic,
        "created_at": _utc_now(),
        "slides": _fixture_slides(topic),
        "explainer_url": f"https://scrimba.com/explain/fixture/{_packet_id(topic)}",
        "mcp_endpoint": endpoint,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_published": False,
        "streamed_live": False,
        "notes": (
            "Fixture Scrimba explainer packet — NOT STREAMED / NOT AUTO-PUBLISHED. "
            "Distinct from northstar status explain."
        ),
    }
    _validate_packet(repo_root, packet)
    path = store.write_packet(repo_root, packet)
    return {"status": "ok", "path": str(path), "packet": packet}


def show(repo_root: Path, packet_id: str) -> dict[str, Any]:
    require_explain_enabled()
    packet = store.read_packet(repo_root, packet_id)
    if not packet:
        raise FileNotFoundError(f"scrimba explainer packet not found: {packet_id}")
    return {"status": "ok", "packet": packet}


def list_packets(repo_root: Path) -> dict[str, Any]:
    require_explain_enabled()
    packets = store.list_packets(repo_root)
    return {
        "status": "ok",
        "count": len(packets),
        "packets": [
            {
                "packet_id": p.get("packet_id"),
                "topic": p.get("topic"),
                "mode": p.get("mode"),
                "created_at": p.get("created_at"),
                "slide_count": len(p.get("slides") or []),
                "explainer_url": p.get("explainer_url") or "",
            }
            for p in packets
        ],
    }
