"""Cognitive Core / brain enable gate (default off)."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def brain_enabled() -> bool:
    return _truthy("COMPASS_BRAIN_ENABLED")


def require_brain_enabled() -> None:
    if not brain_enabled():
        raise PermissionError(
            "cognitive core / brain disabled — set COMPASS_BRAIN_ENABLED=1 "
            "and invoke northstar brain explicitly"
        )
