"""Training bridge enable gate (default off)."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def train_bridge_enabled() -> bool:
    return _truthy("COMPASS_TRAIN_BRIDGE_ENABLED")


def require_train_bridge_enabled() -> None:
    if not train_bridge_enabled():
        raise PermissionError(
            "training bridge disabled — set COMPASS_TRAIN_BRIDGE_ENABLED=1 "
            "and invoke northstar train export|review explicitly"
        )
