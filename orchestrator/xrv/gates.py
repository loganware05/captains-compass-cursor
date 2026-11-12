"""Fail-closed gate for XRV Experience Evidence Record validation."""

from __future__ import annotations

import os


def require_xrv_eer_enabled() -> None:
    raw = (os.environ.get("COMPASS_XRV_EER_ENABLED") or "").strip().lower()
    if raw not in {"1", "true", "yes", "on"}:
        raise PermissionError(
            "XRV EER validation disabled — set COMPASS_XRV_EER_ENABLED=1"
        )
