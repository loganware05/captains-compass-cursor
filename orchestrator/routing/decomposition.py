"""Light decomposition hints for matcher sub-capability weight tuning (M17)."""

from __future__ import annotations

from typing import Any

from orchestrator.matcher.score import WEIGHT_KEYS, get_weights, normalize_weights

_MAX_DELTA = 0.03

_SKILL_FACTOR_MAP: dict[str, str] = {
    "testing-validation": "capability_overlap",
    "capability-planning": "capability_overlap",
    "security-review": "security_bonus",
    "dependency-supply-chain": "security_bonus",
    "react-engineering": "stack_match",
    "node-engineering": "stack_match",
    "postgres-prisma": "stack_match",
    "compass-evaluator": "agent_affinity",
    "experience-routing": "agent_affinity",
    "bounded-autonomy": "agent_affinity",
    "procedure-playbooks": "lifecycle_stage",
    "skill-lifecycle": "lifecycle_stage",
}


def build_decomposition_hints(experiences: list[dict]) -> list[dict[str, Any]]:
    """Derive bounded matcher-factor deltas from successful Experience skill usage."""
    factor_scores: dict[str, float] = {key: 0.0 for key in WEIGHT_KEYS}
    factor_caps: dict[str, set[str]] = {key: set() for key in WEIGHT_KEYS}

    for exp in experiences:
        if exp.get("outcome") != "success":
            continue
        for skill in exp.get("skills_used") or []:
            skill = str(skill)
            factor = _SKILL_FACTOR_MAP.get(skill)
            if not factor:
                continue
            factor_scores[factor] += 0.01
            factor_caps[factor].add(skill)

    hints: list[dict[str, Any]] = []
    for factor, score in sorted(factor_scores.items()):
        if score <= 0:
            continue
        delta = round(min(_MAX_DELTA, score), 4)
        caps = sorted(factor_caps[factor])
        hints.append(
            {
                "matcher_factor": factor,
                "weight_delta": delta,
                "sub_capabilities": caps,
                "rationale": (
                    f"Success experiences emphasized {', '.join(caps)} "
                    f"(proposal-only decomposition hint; max delta {delta})"
                ),
            }
        )
    return hints


def merge_decomposition_hints(
    base_weights: dict[str, float] | None = None,
    hints: list[dict[str, Any]] | None = None,
) -> dict[str, float]:
    """Apply bounded decomposition hints onto matcher weights."""
    merged = dict(base_weights or get_weights())
    if not hints:
        return normalize_weights(merged)
    for hint in hints:
        factor = str(hint.get("matcher_factor") or "")
        if factor not in merged:
            continue
        delta = float(hint.get("weight_delta") or 0.0)
        delta = max(-_MAX_DELTA, min(_MAX_DELTA, delta))
        merged[factor] = round(merged[factor] + delta, 4)
    return normalize_weights(merged)
