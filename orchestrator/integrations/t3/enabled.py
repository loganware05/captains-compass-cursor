"""Fail-closed gates for T3 execution adapter."""

from __future__ import annotations

import os

GATE = "COMPASS_T3_EXEC_ENABLED"
LIVE_GATE = "COMPASS_T3_EXEC_LIVE"


def _truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def t3_exec_enabled() -> bool:
    return _truthy(GATE)


def t3_exec_live_enabled() -> bool:
    return _truthy(LIVE_GATE)


def require_t3_exec_enabled() -> None:
    if not t3_exec_enabled():
        raise PermissionError(
            f"t3 execution adapter disabled — set {GATE}=1 "
            "(plan-bound; never bypasses approval gates)"
        )


def require_t3_exec_live_enabled() -> None:
    require_t3_exec_enabled()
    if not t3_exec_live_enabled():
        raise PermissionError(
            f"t3 live mode disabled — set {LIVE_GATE}=1 "
            "(fixture mode remains default)"
        )
