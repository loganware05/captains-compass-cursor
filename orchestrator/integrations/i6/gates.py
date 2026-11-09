"""Fail-closed gate for I6 cross-provider validation."""

from __future__ import annotations

import os

GATE = "COMPASS_I6_VALIDATE_ENABLED"


def _truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def i6_enabled() -> bool:
    return _truthy(GATE)


def require_i6_enabled() -> None:
    if not i6_enabled():
        raise PermissionError(
            f"i6 validation disabled — set {GATE}=1 "
            "(hermetic I1–I5 fixture harness; never grants authority)"
        )
