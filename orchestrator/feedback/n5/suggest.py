"""Deterministic Skill-fit suggestions from N4 deltas (proposal-only)."""

from __future__ import annotations

from typing import Any

# Minimum absolute delta to emit a boost suggestion (plan default).
MIN_DELTA = 0.05
# Bound informational confidence deltas like experience-routing (M3).
MAX_CONFIDENCE_DELTA = 0.05

# Stack → Skills that evidence-informed routing historically exercises.
STACK_SKILL_MAP: dict[str, list[str]] = {
    "traphouse": ["experience-routing", "testing-validation", "execution-telemetry"],
    "sandbox": ["capability-planning", "implementation-planning", "autonomy-budget"],
    "bitcoin": ["repository-discovery", "docker-cloud", "harness-gc"],
}

# Metric → Skills when cross-stack delta clears threshold.
METRIC_SKILL_MAP: dict[str, list[str]] = {
    "skill_reuse_rate": ["experience-routing", "knowledge-steward"],
    "accept_rate": ["testing-validation", "capability-planning"],
    "retrieval_precision": ["knowledge-steward", "repository-discovery"],
    "primary_efficiency": ["execution-telemetry", "autonomy-budget"],
}


def _clamp(delta: float) -> float:
    return round(max(-MAX_CONFIDENCE_DELTA, min(MAX_CONFIDENCE_DELTA, delta)), 4)


def build_skill_fit_suggestions(n4_report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return Skill-fit suggestion rows from N4 deltas + stacks."""
    deltas = n4_report.get("deltas") or {}
    stacks = n4_report.get("stacks") or []
    suggestions: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(skill_id: str, delta: float, rationale: str, metric: str) -> None:
        key = f"{skill_id}|{metric}"
        if key in seen:
            return
        seen.add(key)
        suggestions.append(
            {
                "skill_id": skill_id,
                "action": "boost" if delta > 0 else "dampen" if delta < 0 else "no_change",
                "confidence_delta": _clamp(delta),
                "metric": metric,
                "rationale": rationale,
            }
        )

    metric_values = {
        "skill_reuse_rate": float(deltas.get("skill_reuse_rate") or 0.0),
        "accept_rate": float(deltas.get("accept_rate") or 0.0),
        "retrieval_precision": float(deltas.get("retrieval_precision") or 0.0),
        "primary_efficiency": float(deltas.get("primary_efficiency") or 0.0),
    }

    any_positive = False
    for metric, value in metric_values.items():
        if abs(value) < MIN_DELTA:
            continue
        any_positive = any_positive or value >= MIN_DELTA
        for skill_id in METRIC_SKILL_MAP.get(metric, []):
            add(
                skill_id,
                value if value > 0 else value,
                (
                    f"N4 delta {metric}={value:+.4f} "
                    f"(threshold ±{MIN_DELTA}); proposal-only"
                ),
                metric,
            )

    if any_positive:
        for stack in stacks:
            stack_id = str(stack.get("stack_id") or "")
            for skill_id in STACK_SKILL_MAP.get(stack_id, []):
                reuse = metric_values["skill_reuse_rate"]
                if abs(reuse) < MIN_DELTA:
                    reuse = metric_values["accept_rate"]
                if abs(reuse) < MIN_DELTA:
                    continue
                add(
                    skill_id,
                    reuse,
                    (
                        f"Stack {stack_id} evidence arm improved "
                        f"vs baseline; Skill-fit proposal-only"
                    ),
                    "stack_fit",
                )

    if not suggestions:
        suggestions.append(
            {
                "skill_id": "(none)",
                "action": "no_change",
                "confidence_delta": 0.0,
                "metric": "none",
                "rationale": (
                    f"No N4 delta met ±{MIN_DELTA} threshold; "
                    "no Skill-fit change proposed"
                ),
            }
        )

    return suggestions


def skill_confidence_deltas_from_suggestions(
    suggestions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Collapse Skill-fit rows into RoutingProposal skill_confidence_deltas."""
    by_skill: dict[str, dict[str, Any]] = {}
    for row in suggestions:
        skill_id = str(row.get("skill_id") or "")
        if not skill_id or skill_id == "(none)":
            continue
        delta = float(row.get("confidence_delta") or 0.0)
        if skill_id not in by_skill:
            by_skill[skill_id] = {
                "skill_id": skill_id,
                "delta": _clamp(delta),
                "rationale": str(row.get("rationale") or ""),
            }
        else:
            # Keep largest absolute informational delta.
            prev = float(by_skill[skill_id]["delta"])
            if abs(delta) > abs(prev):
                by_skill[skill_id]["delta"] = _clamp(delta)
                by_skill[skill_id]["rationale"] = str(row.get("rationale") or "")
    return [by_skill[k] for k in sorted(by_skill)]
