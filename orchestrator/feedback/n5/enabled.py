"""Enable gate for N5 Skill-fit / routing feedback."""

from __future__ import annotations

import os

GATE = "COMPASS_N5_FEEDBACK_ENABLED"


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def n5_enabled() -> bool:
    return _truthy(GATE)


def require_n5_gate() -> None:
    if not n5_enabled():
        raise PermissionError(
            "N5 feedback disabled — set "
            f"{GATE}=1 (or pass --enable-gates) and invoke "
            "northstar feedback n5"
        )
