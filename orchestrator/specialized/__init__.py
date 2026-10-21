"""Specialized Model Level 0 — local baseline (no fine-tuning)."""

from orchestrator.specialized.service import (
    SpecializedModelServiceError,
    run_baseline,
)

__all__ = ["SpecializedModelServiceError", "run_baseline"]
