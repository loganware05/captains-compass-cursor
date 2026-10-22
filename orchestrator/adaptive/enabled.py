"""Enable gate for Adaptive Intelligence Validation (N3)."""

from __future__ import annotations

import os

GATE = "COMPASS_ADAPTIVE_INTEL_ENABLED"


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def adaptive_intel_enabled() -> bool:
    return _truthy(GATE)


def require_adaptive_intel_gate() -> None:
    if not adaptive_intel_enabled():
        raise PermissionError(
            "adaptive intelligence disabled — set "
            f"{GATE}=1 (or pass --enable-gates) and invoke "
            "northstar adaptive scorecard"
        )
