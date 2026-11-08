"""Fail-closed gates for Apify CLI / live TI (I3)."""

from __future__ import annotations

import os

GATE = "COMPASS_APIFY_ENABLED"
LIVE_GATE = "COMPASS_APIFY_LIVE"


def _truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def apify_enabled() -> bool:
    return _truthy(GATE)


def apify_live_enabled() -> bool:
    return _truthy(LIVE_GATE)


def require_apify_enabled() -> None:
    if not apify_enabled():
        raise PermissionError(
            f"apify surface disabled — set {GATE}=1 "
            "(fixture-first; never auto-runs Actors)"
        )


def require_apify_live_enabled() -> None:
    require_apify_enabled()
    if not apify_live_enabled():
        raise PermissionError(
            f"apify live mode disabled — set {LIVE_GATE}=1 "
            "(fixture mode remains default; call-actor deferred)"
        )


def apify_token() -> str:
    return (
        (os.environ.get("COMPASS_APIFY_TOKEN") or "").strip()
        or (os.environ.get("APIFY_TOKEN") or "").strip()
    )
