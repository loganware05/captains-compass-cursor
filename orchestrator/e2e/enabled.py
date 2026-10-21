"""Gate checks for Cognitive Core e2e evaluation."""

from __future__ import annotations

import os

REQUIRED_GATES = (
    ("COMPASS_BRAIN_ENABLED", "brain (C1/C2)"),
    ("COMPASS_ASSESS_ENABLED", "assess (C3)"),
    ("COMPASS_CYCLE_ENABLED", "cycle (C4)"),
    ("COMPASS_ROUTE_ENABLED", "model route (C5)"),
    ("COMPASS_REA_ENABLED", "rea (C6)"),
    ("COMPASS_TRAIN_BRIDGE_ENABLED", "train (C7)"),
)


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def missing_gates() -> list[str]:
    return [name for name, _label in REQUIRED_GATES if not _truthy(name)]


def require_e2e_gates() -> None:
    missing = missing_gates()
    if missing:
        joined = ", ".join(missing)
        raise PermissionError(
            "Cognitive Core e2e requires feature gates to be set "
            f"(missing: {joined}). Export COMPASS_BRAIN_ENABLED=1 "
            "COMPASS_ASSESS_ENABLED=1 COMPASS_CYCLE_ENABLED=1 "
            "COMPASS_ROUTE_ENABLED=1 COMPASS_REA_ENABLED=1 "
            "COMPASS_TRAIN_BRIDGE_ENABLED=1, or pass --enable-gates."
        )
