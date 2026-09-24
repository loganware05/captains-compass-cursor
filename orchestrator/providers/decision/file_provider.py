"""File-backed DecisionProvider + selector (hermetic fixtures; default stub)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from orchestrator.providers.decision import StubDecisionProvider
from orchestrator.providers.decision.types import (
    PINNED_JEV_MODEL_ID,
    PRIORITY_CHOICES,
    WARRANT_CHOICES,
    RankedSuggestion,
    ReviewTriageRequest,
    ReviewTriageResult,
    SkillSuggestionRequest,
    SkillSuggestionResult,
)

DEFAULT_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _fixtures_dir() -> Path:
    override = os.environ.get("COMPASS_DECISION_FIXTURES_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_FIXTURES_DIR


class FileDecisionProvider:
    """Load offline skill-suggestion fixtures keyed by objective substring."""

    name = "file"

    def __init__(self, fixtures_dir: Path | None = None) -> None:
        self.fixtures_dir = fixtures_dir or _fixtures_dir()

    def _load_fixtures(self) -> list[dict]:
        if not self.fixtures_dir.is_dir():
            return []
        out: list[dict] = []
        for path in sorted(self.fixtures_dir.glob("*.json")):
            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, dict):
                out.append(payload)
        return out

    def suggest_skills(self, request: SkillSuggestionRequest) -> SkillSuggestionResult:
        objective = (request.objective or "").lower()
        eligible_ids = {s.skill_id for s in request.eligible_skills}
        for fixture in self._load_fixtures():
            needle = str(fixture.get("objective_contains") or "").lower().strip()
            if not needle:
                # Skip non-suggestion JSON accidentally placed in fixtures/.
                continue
            if needle not in objective:
                continue
            ranked_raw = fixture.get("ranked") or []
            ranked: list[RankedSuggestion] = []
            for item in ranked_raw:
                if not isinstance(item, dict):
                    continue
                skill_id = str(item.get("skill_id") or "")
                if skill_id and skill_id not in eligible_ids:
                    continue
                ranked.append(
                    RankedSuggestion(
                        skill_id=skill_id,
                        score=float(item.get("score") or 0.0),
                        confidence=(
                            float(item["confidence"])
                            if item.get("confidence") is not None
                            else None
                        ),
                        rationale=str(item.get("rationale") or "file-fixture"),
                    )
                )
            abstain = bool(fixture.get("abstain"))
            suggested = fixture.get("suggested_skill_id")
            if suggested is not None:
                suggested = str(suggested)
                if suggested and suggested not in eligible_ids:
                    suggested = None
                    abstain = True
            return SkillSuggestionResult(
                provider=self.name,
                model_id=str(fixture.get("model_id") or PINNED_JEV_MODEL_ID),
                ranked=ranked,
                suggested_skill_id=None if abstain else suggested,
                abstain=abstain,
                abstain_reason=str(fixture.get("abstain_reason") or ""),
                question_revision_rank=str(
                    fixture.get("question_revision_rank") or request.question_revision_rank
                ),
                question_revision_recheck=str(
                    fixture.get("question_revision_recheck")
                    or request.question_revision_recheck
                ),
                latency_ms=float(fixture.get("latency_ms") or 0.0),
                input_tokens=int(fixture.get("input_tokens") or 0),
                output_tokens=int(fixture.get("output_tokens") or 0),
                raw_answers=dict(fixture.get("raw_answers") or {}),
            )
        return SkillSuggestionResult(
            provider=self.name,
            model_id=PINNED_JEV_MODEL_ID,
            abstain=True,
            abstain_reason="no matching file fixture for objective",
        )

    def triage_review(self, request: ReviewTriageRequest) -> ReviewTriageResult:
        paths_blob = " ".join(request.change.changed_paths).lower()
        domains_blob = " ".join(request.change.domains).lower()
        haystack = f"{paths_blob} {domains_blob} {request.change.objective.lower()}"
        for fixture in self._load_fixtures():
            needle = str(fixture.get("path_contains") or "").lower().strip()
            if not needle:
                continue
            if needle not in haystack:
                continue
            priority = fixture.get("investigation_priority")
            if priority is not None:
                priority = str(priority).lower()
                if priority not in PRIORITY_CHOICES:
                    priority = None
            warrant = fixture.get("specialist_security_warranted")
            if warrant is not None:
                warrant = str(warrant).lower()
                if warrant not in WARRANT_CHOICES:
                    warrant = None
            abstain = bool(fixture.get("abstain"))
            return ReviewTriageResult(
                provider=self.name,
                model_id=str(fixture.get("model_id") or PINNED_JEV_MODEL_ID),
                investigation_priority=None if abstain else priority,
                specialist_security_warranted=None if abstain else warrant,
                touches_authz=(
                    float(fixture["touches_authz"])
                    if fixture.get("touches_authz") is not None
                    else None
                ),
                touches_sensitive=(
                    float(fixture["touches_sensitive"])
                    if fixture.get("touches_sensitive") is not None
                    else None
                ),
                abstain=abstain,
                abstain_reason=str(fixture.get("abstain_reason") or ""),
                question_revision=str(
                    fixture.get("question_revision") or request.question_revision
                ),
                latency_ms=float(fixture.get("latency_ms") or 0.0),
                input_tokens=int(fixture.get("input_tokens") or 0),
                output_tokens=int(fixture.get("output_tokens") or 0),
                raw_answers=dict(fixture.get("raw_answers") or {}),
            )
        return ReviewTriageResult(
            provider=self.name,
            model_id=PINNED_JEV_MODEL_ID,
            abstain=True,
            abstain_reason="no matching file fixture for review paths",
        )


def select_decision_provider(repo_root: Path | None = None):
    """Return DecisionProvider from COMPASS_DECISION_PROVIDER (default stub)."""
    del repo_root  # reserved for future repo-local config
    name = os.environ.get("COMPASS_DECISION_PROVIDER", "stub").strip().lower() or "stub"
    if name in {"stub", "off", "none", ""}:
        return StubDecisionProvider()
    if name == "file":
        return FileDecisionProvider()
    if name == "jev":
        from orchestrator.providers.decision.jev_provider import JevDecisionProvider

        return JevDecisionProvider()
    # Unknown → fail closed to stub (no surprise network)
    return StubDecisionProvider()


def decision_shadow_enabled() -> bool:
    raw = os.environ.get("COMPASS_DECISION_SHADOW", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def decision_review_shadow_enabled() -> bool:
    raw = os.environ.get("COMPASS_DECISION_REVIEW_SHADOW", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}
