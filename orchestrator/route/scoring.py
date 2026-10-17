"""Deterministic adapter-class selection for Cognitive Core C5."""

from __future__ import annotations

from typing import Any

# Notion adapter classes → existing model-profile catalog ids.
ADAPTER_TO_PROFILE: dict[str, str] = {
    "local": "fast-iter",
    "hosted": "coding-strong",
    "premium": "reasoning-strong",
}

CLASS_ORDER = ("local", "hosted", "premium")

BUDGET_BY_CLASS: dict[str, dict[str, Any]] = {
    "local": {
        "token_budget_hint": "small",
        "latency_hint": "low",
        "cost_cap_hint": "minimal",
        "autonomy_budget_hint": "tight",
    },
    "hosted": {
        "token_budget_hint": "standard",
        "latency_hint": "medium",
        "cost_cap_hint": "standard",
        "autonomy_budget_hint": "standard",
    },
    "premium": {
        "token_budget_hint": "large",
        "latency_hint": "high",
        "cost_cap_hint": "elevated",
        "autonomy_budget_hint": "minimal",
    },
}


def _bump(adapter_class: str, steps: int = 1) -> str:
    idx = CLASS_ORDER.index(adapter_class)
    return CLASS_ORDER[min(len(CLASS_ORDER) - 1, idx + steps)]


def select_adapter_class(
    *,
    difficulty_band: str | None,
    difficulty_score: float | None,
    security_sensitive: bool,
    freshness: str | None,
    gap_count: int,
    objective: str,
) -> tuple[str, list[str]]:
    """Return (adapter_class, rationale_bullets)."""
    reasons: list[str] = []
    band = (difficulty_band or "").lower()
    score = float(difficulty_score) if difficulty_score is not None else None
    obj = (objective or "").lower()

    if security_sensitive or "secret" in obj or "auth" in obj or "credential" in obj:
        chosen = "premium"
        reasons.append("security-sensitive objective → premium adapter class")
    elif band in {"very_high", "high"} or (score is not None and score >= 50):
        chosen = "premium"
        reasons.append(f"difficulty band/score ({band or score}) → premium")
    elif band == "moderate" or (score is not None and score >= 25) or gap_count > 0:
        chosen = "hosted"
        reasons.append(
            f"moderate difficulty or capability gaps ({gap_count}) → hosted"
        )
    elif any(k in obj for k in ("architect", "plan", "design", "multi-file", "refactor")):
        chosen = "hosted"
        reasons.append("planning/architecture keywords → hosted")
    else:
        chosen = "local"
        reasons.append("low difficulty / bounded objective → local")

    fresh = (freshness or "").lower()
    if fresh in {"stale", "no_snapshot"} and chosen != "premium":
        bumped = _bump(chosen)
        if bumped != chosen:
            reasons.append(
                f"brain freshness={fresh} → bump {chosen}→{bumped} for safer context"
            )
            chosen = bumped

    return chosen, reasons


def fallback_chain(adapter_class: str) -> list[str]:
    """Ordered fallbacks excluding the primary class, higher then lower."""
    idx = CLASS_ORDER.index(adapter_class)
    higher = list(CLASS_ORDER[idx + 1 :])
    lower = list(reversed(CLASS_ORDER[:idx]))
    return higher + lower


def expected_budget(adapter_class: str) -> dict[str, Any]:
    return dict(BUDGET_BY_CLASS[adapter_class])
