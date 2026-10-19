"""REA deep-analysis enable gate (default off)."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def rea_enabled() -> bool:
    return _truthy("COMPASS_REA_ENABLED")


def require_rea_enabled() -> None:
    if not rea_enabled():
        raise PermissionError(
            "REA investigate disabled — set COMPASS_REA_ENABLED=1 "
            "and invoke northstar rea investigate explicitly"
        )
