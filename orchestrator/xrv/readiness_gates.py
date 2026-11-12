"""Fail-closed gate for XRV eight-pillar readiness assessor."""

from __future__ import annotations

import os


def require_xrv_readiness_enabled() -> None:
    raw = (os.environ.get("COMPASS_XRV_READINESS_ENABLED") or "").strip().lower()
    if raw not in {"1", "true", "yes", "on"}:
        raise PermissionError(
            "XRV readiness assessor disabled — set COMPASS_XRV_READINESS_ENABLED=1"
        )
