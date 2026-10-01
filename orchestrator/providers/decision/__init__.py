"""DecisionProvider boundary — skills, review triage, agent routing, behavior eval.

Authority: suggestions never mutate matcher rankings, review findings, agent
selection, prompts, Skills, or instructions; never set ``approved_for_execution``;
never bypass Captain gates. Behavior evaluation (M46) is observe-only.
"""

from __future__ import annotations

from typing import Protocol

from orchestrator.providers.decision.types import (
    PINNED_JEV_MODEL_ID,
    AgentRoutingRequest,
    AgentRoutingResult,
    BehaviorEvalRequest,
    BehaviorEvalResult,
    ReviewTriageRequest,
    ReviewTriageResult,
    SkillSuggestionRequest,
    SkillSuggestionResult,
)


class DecisionProvider(Protocol):
    """Suggestion-only DecisionProvider surface."""

    name: str

    def suggest_skills(self, request: SkillSuggestionRequest) -> SkillSuggestionResult:
        """Return ranked skill suggestions or an explicit abstain."""

    def triage_review(self, request: ReviewTriageRequest) -> ReviewTriageResult:
        """Return review investigation priority signals or abstain."""

    def suggest_agents(self, request: AgentRoutingRequest) -> AgentRoutingResult:
        """Return ranked agent suggestions over an eligible roster or abstain."""

    def evaluate_behavior(self, request: BehaviorEvalRequest) -> BehaviorEvalResult:
        """Return behavior signal probabilities or abstain (observe-only)."""


class StubDecisionProvider:
    """Default hermetic provider — no suggestions, no network."""

    name = "stub"

    def suggest_skills(self, request: SkillSuggestionRequest) -> SkillSuggestionResult:
        del request
        return SkillSuggestionResult(
            provider=self.name,
            model_id=None,
            abstain=True,
            abstain_reason="stub provider (decision service disabled)",
        )

    def triage_review(self, request: ReviewTriageRequest) -> ReviewTriageResult:
        del request
        return ReviewTriageResult(
            provider=self.name,
            model_id=None,
            abstain=True,
            abstain_reason="stub provider (decision service disabled)",
        )

    def suggest_agents(self, request: AgentRoutingRequest) -> AgentRoutingResult:
        del request
        return AgentRoutingResult(
            provider=self.name,
            model_id=None,
            abstain=True,
            abstain_reason="stub provider (decision service disabled)",
        )

    def evaluate_behavior(self, request: BehaviorEvalRequest) -> BehaviorEvalResult:
        del request
        return BehaviorEvalResult(
            provider=self.name,
            model_id=None,
            abstain=True,
            abstain_reason="stub provider (decision service disabled)",
        )


__all__ = [
    "DecisionProvider",
    "StubDecisionProvider",
    "PINNED_JEV_MODEL_ID",
    "SkillSuggestionRequest",
    "SkillSuggestionResult",
    "ReviewTriageRequest",
    "ReviewTriageResult",
    "AgentRoutingRequest",
    "AgentRoutingResult",
    "BehaviorEvalRequest",
    "BehaviorEvalResult",
]
