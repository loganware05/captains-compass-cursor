"""Adaptive model routing enable gate (default off)."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def route_enabled() -> bool:
    return _truthy("COMPASS_ROUTE_ENABLED")


def require_route_enabled() -> None:
    if not route_enabled():
        raise PermissionError(
            "model routing disabled — set COMPASS_ROUTE_ENABLED=1 "
            "and invoke northstar model route|evaluate explicitly"
        )
