"""N3 Adaptive Intelligence Validation — scorecard compose (proposal-only)."""

from orchestrator.adaptive.enabled import (
    adaptive_intel_enabled,
    require_adaptive_intel_gate,
)
from orchestrator.adaptive.service import AdaptiveServiceError, run_scorecard

__all__ = [
    "AdaptiveServiceError",
    "adaptive_intel_enabled",
    "require_adaptive_intel_gate",
    "run_scorecard",
]
