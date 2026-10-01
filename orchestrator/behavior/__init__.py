"""M46 Behavior Intelligence — observe-only evaluation package.

Import submodules directly (e.g. ``orchestrator.behavior.service``) to avoid
circular imports with DecisionProvider adapters.
"""

from orchestrator.behavior.enabled import behavior_eval_enabled, require_behavior_eval_enabled
from orchestrator.behavior.signals import BEHAVIOR_SIGNALS, SCHEMA_VERSION, normalize_signals

__all__ = [
    "BEHAVIOR_SIGNALS",
    "SCHEMA_VERSION",
    "behavior_eval_enabled",
    "normalize_signals",
    "require_behavior_eval_enabled",
]
