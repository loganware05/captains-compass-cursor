"""Typed request/result shapes for the DecisionProvider skill-suggestion call."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


QUESTION_REVISION_RANK = "skill_suggest_v1"
QUESTION_REVISION_RECHECK = "skill_recheck_v1"
PINNED_JEV_MODEL_ID = "jev-1.13.0"
FORBIDDEN_MODEL_ALIASES = frozenset({"jev-latest", "jev-preview"})


@dataclass(frozen=True)
class EligibleSkillSummary:
    """Compact metadata safe to send to a decision provider (no secrets / diffs)."""

    skill_id: str
    name: str
    description: str
    lifecycle_stage: str = ""
    maturity: str = ""
    categories: tuple[str, ...] = ()
    evidence_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "lifecycle_stage": self.lifecycle_stage,
            "maturity": self.maturity,
            "categories": list(self.categories),
            "evidence_notes": self.evidence_notes,
        }


@dataclass
class SkillSuggestionRequest:
    objective: str
    eligible_skills: list[EligibleSkillSummary]
    roster_hash: str
    question_revision_rank: str = QUESTION_REVISION_RANK
    question_revision_recheck: str = QUESTION_REVISION_RECHECK
    shortlist_n: int = 3

    def to_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "eligible_skills": [s.to_dict() for s in self.eligible_skills],
            "roster_hash": self.roster_hash,
            "question_revision_rank": self.question_revision_rank,
            "question_revision_recheck": self.question_revision_recheck,
            "shortlist_n": self.shortlist_n,
        }


@dataclass
class RankedSuggestion:
    skill_id: str
    score: float
    confidence: float | None = None
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "score": self.score,
            "confidence": self.confidence,
            "rationale": self.rationale,
        }


@dataclass
class SkillSuggestionResult:
    """Suggestion-only — never mutates matcher rankings or grants authority."""

    provider: str
    model_id: str | None
    ranked: list[RankedSuggestion] = field(default_factory=list)
    suggested_skill_id: str | None = None
    abstain: bool = False
    abstain_reason: str = ""
    question_revision_rank: str = QUESTION_REVISION_RANK
    question_revision_recheck: str = QUESTION_REVISION_RECHECK
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw_answers: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "ranked": [item.to_dict() for item in self.ranked],
            "suggested_skill_id": self.suggested_skill_id,
            "abstain": self.abstain,
            "abstain_reason": self.abstain_reason,
            "question_revision_rank": self.question_revision_rank,
            "question_revision_recheck": self.question_revision_recheck,
            "latency_ms": self.latency_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "raw_answers": dict(self.raw_answers),
            "error": self.error,
            "applied": False,
        }
