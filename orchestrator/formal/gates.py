"""Fail-closed gate for the opt-in Bend proof experiment."""

from __future__ import annotations

import os


def require_bend_proof_enabled() -> None:
    raw = (os.environ.get("COMPASS_BEND_PROOF_ENABLED") or "").strip().lower()
    if raw not in {"1", "true", "yes", "on"}:
        raise PermissionError(
            "Bend proof experiment disabled — set COMPASS_BEND_PROOF_ENABLED=1"
        )
