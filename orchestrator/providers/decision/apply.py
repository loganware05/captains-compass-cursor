"""Opt-in DecisionProvider ranking apply policy (M43).

Fail-closed to matcher rankings unless APPLY is on, provider is non-stub,
suggestion is non-abstaining, gates pass, and IDs stay within the eligible roster.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Sequence

from orchestrator.providers.decision.types import SkillSuggestionResult

DEFAULT_NOUL_MIN = 0.70
DEFAULT_CONF_MIN = 0.60


def _truthy_env(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def decision_apply_enabled() -> bool:
    """COMPASS_DECISION_APPLY — default off."""
    return _truthy_env("COMPASS_DECISION_APPLY")


def decision_noul_min() -> float:
    raw = os.environ.get("COMPASS_DECISION_NOUL_MIN", "").strip()
    if not raw:
        return DEFAULT_NOUL_MIN
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_NOUL_MIN


def decision_conf_min() -> float:
    raw = os.environ.get("COMPASS_DECISION_CONF_MIN", "").strip()
    if not raw:
        return DEFAULT_CONF_MIN
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_CONF_MIN


def extract_apply_gates(
    result: SkillSuggestionResult,
) -> tuple[float | None, float | None]:
    """Return (needs_skill noul, choice confidence) from result / raw_answers."""
    raw = result.raw_answers or {}
    noul: float | None = None
    needs = raw.get("needs_skill")
    if isinstance(needs, dict) and needs.get("noul") is not None:
        try:
            noul = float(needs["noul"])
        except (TypeError, ValueError):
            noul = None
    if noul is None:
        fits = raw.get("top_fits")
        if isinstance(fits, dict) and fits.get("noul") is not None:
            try:
                noul = float(fits["noul"])
            except (TypeError, ValueError):
                noul = None

    confidence: float | None = None
    which = raw.get("which_skill")
    if isinstance(which, dict) and which.get("confidence") is not None:
        try:
            confidence = float(which["confidence"])
        except (TypeError, ValueError):
            confidence = None
    if confidence is None:
        which2 = raw.get("which_of_shortlist")
        if isinstance(which2, dict) and which2.get("confidence") is not None:
            try:
                confidence = float(which2["confidence"])
            except (TypeError, ValueError):
                confidence = None
    if confidence is None and result.suggested_skill_id:
        for item in result.ranked:
            if item.skill_id == result.suggested_skill_id and item.confidence is not None:
                confidence = float(item.confidence)
                break
    if confidence is None and result.ranked:
        top = result.ranked[0]
        if top.confidence is not None:
            confidence = float(top.confidence)
    return noul, confidence


def provider_ordered_ids(result: SkillSuggestionResult, *, top_n: int) -> list[str]:
    """Ordered skill ids from a non-abstaining suggestion (suggested first)."""
    if result.abstain:
        return []
    out: list[str] = []
    seen: set[str] = set()
    if result.suggested_skill_id:
        sid = str(result.suggested_skill_id)
        out.append(sid)
        seen.add(sid)
    for item in result.ranked:
        sid = str(item.skill_id)
        if not sid or sid in seen:
            continue
        out.append(sid)
        seen.add(sid)
        if len(out) >= top_n:
            break
    return out[:top_n]


def pad_with_matcher(
    provider_ids: Sequence[str],
    matcher_ids: Sequence[str],
    *,
    eligible_ids: set[str],
    top_n: int,
) -> list[str]:
    """Provider head (eligible only) + matcher pad; never introduce OOR ids."""
    out: list[str] = []
    seen: set[str] = set()
    for sid in provider_ids:
        if sid not in eligible_ids or sid in seen:
            continue
        out.append(sid)
        seen.add(sid)
        if len(out) >= top_n:
            return out
    for sid in matcher_ids:
        if sid not in eligible_ids or sid in seen:
            continue
        out.append(sid)
        seen.add(sid)
        if len(out) >= top_n:
            break
    return out


@dataclass(frozen=True)
class ApplyDecision:
    applied: bool
    recommended_skill_ids: list[str]
    reason: str
    noul: float | None = None
    confidence: float | None = None
    provider_head: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "applied": self.applied,
            "recommended_skill_ids": list(self.recommended_skill_ids),
            "reason": self.reason,
            "noul": self.noul,
            "confidence": self.confidence,
            "provider_head": list(self.provider_head),
        }


def apply_skill_rankings(
    matcher_ids: Sequence[str],
    result: SkillSuggestionResult,
    *,
    eligible_ids: set[str],
    top_n: int,
    noul_min: float | None = None,
    conf_min: float | None = None,
) -> ApplyDecision:
    """Decide whether to replace matcher rankings with a padded provider order.

    Fail-closed: any uncertainty returns matcher_ids with applied=False.
    ``applied`` is True only when the final list differs from matcher.
    """
    matcher = [str(x) for x in matcher_ids][:top_n]
    floor_noul = DEFAULT_NOUL_MIN if noul_min is None else noul_min
    floor_conf = DEFAULT_CONF_MIN if conf_min is None else conf_min

    if result.provider in {"stub", "off", "none", ""}:
        return ApplyDecision(False, matcher, "stub_provider")
    if result.abstain:
        return ApplyDecision(
            False, matcher, f"abstain:{result.abstain_reason or 'unspecified'}"
        )
    if result.error:
        return ApplyDecision(False, matcher, f"error:{result.error}")

    noul, confidence = extract_apply_gates(result)
    if noul is None:
        return ApplyDecision(False, matcher, "missing_noul", noul=noul, confidence=confidence)
    if noul < floor_noul:
        return ApplyDecision(
            False,
            matcher,
            f"noul_below_floor:{noul:.4f}<{floor_noul:.4f}",
            noul=noul,
            confidence=confidence,
        )
    if confidence is None:
        return ApplyDecision(
            False, matcher, "missing_confidence", noul=noul, confidence=confidence
        )
    if confidence < floor_conf:
        return ApplyDecision(
            False,
            matcher,
            f"confidence_below_floor:{confidence:.4f}<{floor_conf:.4f}",
            noul=noul,
            confidence=confidence,
        )

    head = provider_ordered_ids(result, top_n=top_n)
    # Drop anything outside eligible roster (OOR).
    head = [sid for sid in head if sid in eligible_ids]
    if not head:
        return ApplyDecision(
            False,
            matcher,
            "no_eligible_provider_ids",
            noul=noul,
            confidence=confidence,
        )

    merged = pad_with_matcher(head, matcher, eligible_ids=eligible_ids, top_n=top_n)
    if not merged:
        return ApplyDecision(
            False,
            matcher,
            "empty_after_pad",
            noul=noul,
            confidence=confidence,
            provider_head=tuple(head),
        )
    # Invariant: every applied id must be eligible.
    if any(sid not in eligible_ids for sid in merged):
        return ApplyDecision(
            False,
            matcher,
            "eligibility_invariant_failed",
            noul=noul,
            confidence=confidence,
            provider_head=tuple(head),
        )
    if merged == matcher:
        return ApplyDecision(
            False,
            matcher,
            "identical_to_matcher",
            noul=noul,
            confidence=confidence,
            provider_head=tuple(head),
        )
    return ApplyDecision(
        True,
        merged,
        "thresholds_passed",
        noul=noul,
        confidence=confidence,
        provider_head=tuple(head),
    )
