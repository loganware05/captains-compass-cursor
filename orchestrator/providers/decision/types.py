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

    def to_dict(self, *, applied: bool = False) -> dict[str, Any]:
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
            "applied": bool(applied),
        }


QUESTION_REVISION_REVIEW_TRIAGE = "review_triage_v1"
PRIORITY_CHOICES = frozenset({"high", "medium", "low", "none"})
WARRANT_CHOICES = frozenset({"yes", "no", "uncertain"})


@dataclass(frozen=True)
class ReviewChangeSummary:
    """Compact change metadata for review triage (no diffs / secrets)."""

    changed_paths: tuple[str, ...]
    domains: tuple[str, ...]
    path_flags: dict[str, bool]
    specialist_skill_ids: tuple[str, ...] = ()
    candidate_count: int = 0
    objective: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "changed_paths": list(self.changed_paths),
            "domains": list(self.domains),
            "path_flags": dict(self.path_flags),
            "specialist_skill_ids": list(self.specialist_skill_ids),
            "candidate_count": int(self.candidate_count),
            "objective": self.objective,
        }


@dataclass
class ReviewTriageRequest:
    change: ReviewChangeSummary
    change_hash: str
    question_revision: str = QUESTION_REVISION_REVIEW_TRIAGE

    def to_dict(self) -> dict[str, Any]:
        return {
            "change": self.change.to_dict(),
            "change_hash": self.change_hash,
            "question_revision": self.question_revision,
        }


@dataclass
class ReviewTriageResult:
    """Suggestion-only — never mutates review findings or grants merge authority."""

    provider: str
    model_id: str | None
    investigation_priority: str | None = None
    specialist_security_warranted: str | None = None
    touches_authz: float | None = None
    touches_sensitive: float | None = None
    abstain: bool = False
    abstain_reason: str = ""
    question_revision: str = QUESTION_REVISION_REVIEW_TRIAGE
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw_answers: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self, *, applied: bool = False) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "investigation_priority": self.investigation_priority,
            "specialist_security_warranted": self.specialist_security_warranted,
            "touches_authz": self.touches_authz,
            "touches_sensitive": self.touches_sensitive,
            "abstain": self.abstain,
            "abstain_reason": self.abstain_reason,
            "question_revision": self.question_revision,
            "latency_ms": self.latency_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "raw_answers": dict(self.raw_answers),
            "error": self.error,
            "applied": bool(applied),
        }
