"""Cursor Cloud wakeability probe for ``northstar.agent_router.v1``.

Builds a live (or snapshot-backed) ``WakeabilityProbe`` from Cursor Cloud Agent
list payloads (MCP ``list-cloud-agents`` / equivalent JSON dumps).

Does not call the network itself — callers supply agent snapshots so CI and
MCP-backed First Mate runs share one mapper.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, MutableMapping

from orchestrator.routing.agent_router import WakeabilityProbe, normalize_wakeability

# Cursor Cloud lifecycle statuses observed via MCP list-cloud-agents.
_WAKEABLE_LIFECYCLES = {
    "RUNNING",
    "IDLE",
    "NOT_YET_STARTED",
    "WAITING_FOR_BACKGROUND_WORK",
}
_EXPIRED_LIFECYCLES = {
    "EXPIRED",
    "ARCHIVED",
}
_UNREACHABLE_LIFECYCLES = {
    "ERROR",
    "UNSPECIFIED",
}


def map_cloud_lifecycle_to_wakeability(
    status: str | None,
    *,
    is_archived: bool = False,
    is_killed: bool = False,
) -> str:
    """Map a Cursor Cloud agent lifecycle status to router wakeability."""

    if is_archived or is_killed:
        return "expired"
    if not status:
        return "unknown"
    key = str(status).strip().upper()
    if key in _WAKEABLE_LIFECYCLES:
        return "wakeable"
    if key in _EXPIRED_LIFECYCLES:
        return "expired"
    if key in _UNREACHABLE_LIFECYCLES:
        return "unreachable"
    # Unknown vendor statuses stay fail-soft (unknown cap).
    return "unknown"


def index_cloud_agents(agents: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Index cloud agent records by ``bcId`` / ``id`` / ``agent_id``."""

    out: dict[str, dict[str, Any]] = {}
    for raw in agents:
        if not isinstance(raw, Mapping):
            continue
        record = dict(raw)
        for key in ("bcId", "id", "agent_id", "agentId"):
            value = record.get(key)
            if value:
                out[str(value)] = record
        # Also index without dashes confusion: keep exact ids only.
    return out


def load_cloud_agents_payload(payload: Mapping[str, Any] | list[Any]) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    if isinstance(payload, Mapping):
        agents = payload.get("agents")
        if isinstance(agents, list):
            return [dict(item) for item in agents if isinstance(item, Mapping)]
    raise ValueError("cloud agents payload must be a list or object with agents[]")


def build_cloud_wakeability_probe(
    agents: Iterable[Mapping[str, Any]],
    *,
    missing: str = "unknown",
) -> WakeabilityProbe:
    """Return a probe that resolves wakeability from a cloud-agent snapshot.

    ``missing`` controls agents present in the registry but absent from the
    snapshot (default ``unknown`` → availability capped, not hard-expired).
    """

    missing_status = normalize_wakeability(missing)
    index = index_cloud_agents(agents)

    def probe(agent: Mapping[str, Any]) -> str:
        agent_id = str(agent.get("id") or agent.get("agent_id") or "")
        if not agent_id:
            return missing_status
        record = index.get(agent_id)
        if record is None:
            return missing_status
        return map_cloud_lifecycle_to_wakeability(
            record.get("status") or record.get("lifecycle_status"),
            is_archived=bool(record.get("isArchived") or record.get("archived")),
            is_killed=bool(record.get("isKilled") or record.get("killed")),
        )

    return probe


def annotate_registry_with_cloud_snapshot(
    registry_agents: Iterable[Mapping[str, Any]],
    cloud_agents: Iterable[Mapping[str, Any]],
    *,
    missing: str = "unknown",
) -> list[dict[str, Any]]:
    """Return registry agents with ``cloud_status`` filled from the snapshot.

    Useful when persisting probe results back into a registry copy without
    mutating the live probe path.
    """

    probe = build_cloud_wakeability_probe(cloud_agents, missing=missing)
    annotated: list[dict[str, Any]] = []
    for agent in registry_agents:
        row: MutableMapping[str, Any] = dict(agent)
        status = probe(row)
        row["cloud_status"] = status
        # Do not overwrite an explicit wakeability_status unless absent.
        if not row.get("wakeability_status"):
            row["wakeability_status"] = status
        annotated.append(dict(row))
    return annotated
