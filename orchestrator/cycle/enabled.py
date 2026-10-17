"""Adaptive Development Loop enable gate (default off)."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def cycle_enabled() -> bool:
    return _truthy("COMPASS_CYCLE_ENABLED")


def require_cycle_enabled() -> None:
    if not cycle_enabled():
        raise PermissionError(
            "adaptive cycle disabled — set COMPASS_CYCLE_ENABLED=1 "
            "and invoke northstar cycle explicitly"
        )
