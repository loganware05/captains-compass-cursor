"""Behavior eval / learn enable gates (default off)."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def behavior_eval_enabled() -> bool:
    return _truthy("COMPASS_BEHAVIOR_EVAL_ENABLED")


def require_behavior_eval_enabled() -> None:
    if not behavior_eval_enabled():
        raise PermissionError(
            "behavior evaluation disabled — set COMPASS_BEHAVIOR_EVAL_ENABLED=1 "
            "and invoke northstar evaluate explicitly"
        )


def behavior_learn_enabled() -> bool:
    return _truthy("COMPASS_BEHAVIOR_LEARN_ENABLED")


def require_behavior_learn_enabled() -> None:
    if not behavior_learn_enabled():
        raise PermissionError(
            "behavior learning disabled — set COMPASS_BEHAVIOR_LEARN_ENABLED=1 "
            "and invoke northstar learn explicitly"
        )


def instructions_enabled() -> bool:
    return _truthy("COMPASS_INSTRUCTIONS_ENABLED")


def require_instructions_enabled() -> None:
    if not instructions_enabled():
        raise PermissionError(
            "behavior instructions disabled — set COMPASS_INSTRUCTIONS_ENABLED=1 "
            "and invoke northstar instructions explicitly"
        )
