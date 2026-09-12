"""NorthStar Code Reviewer pipeline (M27).

Stages: detect → investigate → verify → report.
Default posture is hermetic and evidence-only (no GitHub review posts).
"""

from __future__ import annotations

from orchestrator.review.pipeline import ReviewError, run_code_review

__all__ = ["ReviewError", "run_code_review"]
