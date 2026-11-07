"""Fail-closed gates for Sentry incident ingest."""

from __future__ import annotations

import os

GATE = "COMPASS_SENTRY_INGEST_ENABLED"
LIVE_GATE = "COMPASS_SENTRY_LIVE"


def _truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def sentry_ingest_enabled() -> bool:
    return _truthy(GATE)


def sentry_live_enabled() -> bool:
    return _truthy(LIVE_GATE)


def require_sentry_ingest_enabled() -> None:
    if not sentry_ingest_enabled():
        raise PermissionError(
            f"sentry ingest disabled — set {GATE}=1 "
            "(read-only evidence; never writes to Sentry or grants authority)"
        )


def require_sentry_live_enabled() -> None:
    require_sentry_ingest_enabled()
    if not sentry_live_enabled():
        raise PermissionError(
            f"sentry live mode disabled — set {LIVE_GATE}=1 "
            "and provide a read-only auth token (https only)"
        )
