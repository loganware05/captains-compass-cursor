"""COMPASS_BEHAVIOR_EVAL_ENABLED gate (default off)."""

from __future__ import annotations

import os


def behavior_eval_enabled() -> bool:
    raw = os.environ.get("COMPASS_BEHAVIOR_EVAL_ENABLED", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def require_behavior_eval_enabled() -> None:
    if not behavior_eval_enabled():
        raise PermissionError(
            "behavior evaluation disabled — set COMPASS_BEHAVIOR_EVAL_ENABLED=1 "
            "and invoke northstar evaluate explicitly"
        )
