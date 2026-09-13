"""NorthStar Code Reviewer pipeline (M27 + M28 specialists).

Stages: detect → investigate → specialist composition → verify → report.
Default posture is hermetic and evidence-only (no GitHub review posts).
Default candidates mode is specialists (M28); fixtures remain the CI golden path.
"""

from __future__ import annotations

from orchestrator.review.pipeline import ReviewError, run_code_review

__all__ = ["ReviewError", "run_code_review"]
