"""Enable gates for read-only persistent oversight."""

from __future__ import annotations

import os

from orchestrator.cognitive.enabled import brain_enabled
from orchestrator.status.enabled import status_enabled


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def require_oversight_status_gate() -> None:
    if not status_enabled():
        raise PermissionError(
            "oversight disabled — set COMPASS_STATUS_ENABLED=1 "
            "(or pass --enable-gates) and invoke northstar oversight run"
        )


def brain_sync_requested() -> bool:
    """Brain sync is included when the brain gate is on."""
    return brain_enabled()
