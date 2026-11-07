"""Persist Sentry incident packets under .agent/incidents/sentry/."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,160}$")


class SentryStoreError(ValueError):
    """Raised when incident store IO fails."""


def incidents_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "incidents" / "sentry"


def ensure_layout(repo_root: Path) -> None:
    incidents_root(repo_root).mkdir(parents=True, exist_ok=True)


def assert_safe_id(value: str, label: str = "packet_id") -> None:
    if not value or not _SAFE_ID.match(value):
        raise SentryStoreError(f"unsafe {label}: {value!r}")


def write_packet(repo_root: Path, doc: dict[str, Any]) -> Path:
    validate_document(doc, "sentry-incident-packet.schema.json")
    packet_id = str(doc["packet_id"])
    assert_safe_id(packet_id)
    ensure_layout(repo_root)
    path = incidents_root(repo_root) / f"{packet_id}.json"
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_packet(repo_root: Path, packet_id: str) -> dict[str, Any]:
    assert_safe_id(packet_id)
    path = incidents_root(repo_root) / f"{packet_id}.json"
    if not path.is_file():
        raise SentryStoreError(f"packet not found: {packet_id}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SentryStoreError(str(exc)) from exc
    validate_document(doc, "sentry-incident-packet.schema.json")
    return doc


def list_packets(repo_root: Path) -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    out: list[dict[str, Any]] = []
    for path in sorted(incidents_root(repo_root).glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            validate_document(doc, "sentry-incident-packet.schema.json")
            out.append(doc)
        except Exception:
            continue
    return out
