"""Enable gate for N4 cross-stack benchmark."""

from __future__ import annotations

import os

GATE = "COMPASS_N4_BENCHMARK_ENABLED"


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def n4_enabled() -> bool:
    return _truthy(GATE)


def n4_live_implement_enabled() -> bool:
    return _truthy("COMPASS_N4_LIVE_IMPLEMENT")


def require_n4_gate() -> None:
    if not n4_enabled():
        raise PermissionError(
            "N4 benchmark disabled — set "
            f"{GATE}=1 (or pass --enable-gates) and invoke "
            "northstar benchmark n4"
        )
