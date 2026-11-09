"""Fail-closed gates for WorkOS identity / RBAC (I5)."""

from __future__ import annotations

import os

GATE = "COMPASS_IDENTITY_ENABLED"
LIVE_GATE = "COMPASS_IDENTITY_LIVE"
# Optional alias accepted for operator familiarity
ALIAS_GATE = "COMPASS_WORKOS_ENABLED"
ALIAS_LIVE = "COMPASS_WORKOS_LIVE"


def _truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def identity_enabled() -> bool:
    return _truthy(GATE) or _truthy(ALIAS_GATE)


def identity_live_enabled() -> bool:
    return _truthy(LIVE_GATE) or _truthy(ALIAS_LIVE)


def require_identity_enabled() -> None:
    if not identity_enabled():
        raise PermissionError(
            f"identity surface disabled — set {GATE}=1 "
            f"(alias {ALIAS_GATE}=1 also accepted; fixture-first; "
            "never grants Captain approval)"
        )


def require_identity_live_enabled() -> None:
    require_identity_enabled()
    if not identity_live_enabled():
        raise PermissionError(
            f"identity live mode disabled — set {LIVE_GATE}=1 "
            f"(alias {ALIAS_LIVE}=1; fixture mode remains default; "
            "WorkOS API deferred)"
        )


def workos_api_key() -> str:
    return (
        (os.environ.get("COMPASS_WORKOS_API_KEY") or "").strip()
        or (os.environ.get("WORKOS_API_KEY") or "").strip()
    )
