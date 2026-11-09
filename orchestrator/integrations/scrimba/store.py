"""Persist Scrimba explainer packets under .agent/explainers/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def explainers_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "explainers"


def ensure_store(repo_root: Path) -> Path:
    path = explainers_dir(repo_root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def packet_path(repo_root: Path, packet_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in packet_id)
    return explainers_dir(repo_root) / f"{safe}.json"


def write_packet(repo_root: Path, packet: dict[str, Any]) -> Path:
    ensure_store(repo_root)
    path = packet_path(repo_root, str(packet["packet_id"]))
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def read_packet(repo_root: Path, packet_id: str) -> dict[str, Any] | None:
    path = packet_path(repo_root, packet_id)
    if not path.is_file():
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return doc if isinstance(doc, dict) else None


def list_packets(repo_root: Path) -> list[dict[str, Any]]:
    root = explainers_dir(repo_root)
    if not root.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict):
            out.append(doc)
    out.sort(key=lambda d: str(d.get("created_at") or ""), reverse=True)
    return out
