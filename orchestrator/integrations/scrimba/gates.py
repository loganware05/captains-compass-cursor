"""Fail-closed gates for Scrimba Explain (I4)."""

from __future__ import annotations

import os

GATE = "COMPASS_EXPLAIN_ENABLED"
LIVE_GATE = "COMPASS_EXPLAIN_LIVE"


def _truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def explain_enabled() -> bool:
    return _truthy(GATE)


def explain_live_enabled() -> bool:
    return _truthy(LIVE_GATE)


def require_explain_enabled() -> None:
    if not explain_enabled():
        raise PermissionError(
            f"scrimba explain disabled — set {GATE}=1 "
            "(fixture-first; never auto-publishes; distinct from status explain)"
        )


def require_explain_live_enabled() -> None:
    require_explain_enabled()
    if not explain_live_enabled():
        raise PermissionError(
            f"scrimba explain live mode disabled — set {LIVE_GATE}=1 "
            "(fixture mode remains default; MCP streaming deferred)"
        )
