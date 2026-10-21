"""Enable gates for Specialized Model Level 0 (local baseline)."""

from __future__ import annotations

import os

GATE = "COMPASS_SPECIALIZED_MODEL_ENABLED"


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def specialized_model_enabled() -> bool:
    return _truthy(GATE)


def require_specialized_model_gate() -> None:
    if not specialized_model_enabled():
        raise PermissionError(
            "specialized-model Level 0 disabled — set "
            f"{GATE}=1 (or pass --enable-gates) and invoke "
            "northstar specialized baseline"
        )
