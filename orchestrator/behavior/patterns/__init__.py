"""M47 Behavior Pattern Learning — proposal-only patterns from the M46 ledger.

Import submodules directly (e.g. ``orchestrator.behavior.patterns.service``).
"""

from orchestrator.behavior.enabled import (
    behavior_learn_enabled,
    require_behavior_learn_enabled,
)

__all__ = [
    "behavior_learn_enabled",
    "require_behavior_learn_enabled",
]
