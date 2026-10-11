"""Status / Project Overseer enable gate (default off)."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def status_enabled() -> bool:
    return _truthy("COMPASS_STATUS_ENABLED")


def require_status_enabled() -> None:
    if not status_enabled():
        raise PermissionError(
            "project status/overseer disabled — set COMPASS_STATUS_ENABLED=1 "
            "and invoke northstar status explicitly"
        )
