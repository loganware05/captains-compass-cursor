"""Open UI enable gate (fail-closed)."""

from __future__ import annotations

import os


def openui_enabled() -> bool:
    raw = (os.environ.get("COMPASS_OPENUI_ENABLED") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def require_openui_gate() -> None:
    if not openui_enabled():
        raise PermissionError(
            "Open UI disabled — set COMPASS_OPENUI_ENABLED=1 "
            "(or pass --enable-gates / --ui with gate enable)"
        )
