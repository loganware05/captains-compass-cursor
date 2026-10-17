"""Difficulty assessment enable gate (default off)."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def assess_enabled() -> bool:
    return _truthy("COMPASS_ASSESS_ENABLED")


def require_assess_enabled() -> None:
    if not assess_enabled():
        raise PermissionError(
            "project assess disabled — set COMPASS_ASSESS_ENABLED=1 "
            "and invoke northstar assess project explicitly"
        )
