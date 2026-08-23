"""Candidate promotion package."""

from orchestrator.promotion.advance import (
    PromotionError,
    advance_to_analyzed,
    draft_skill_sidecar_proposal,
    load_candidate_json,
    write_skill_sidecar_draft,
    write_staging_candidate,
)

__all__ = [
    "PromotionError",
    "advance_to_analyzed",
    "draft_skill_sidecar_proposal",
    "load_candidate_json",
    "write_skill_sidecar_draft",
    "write_staging_candidate",
]
