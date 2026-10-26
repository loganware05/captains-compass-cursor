"""Hermetic arm simulation and metric aggregation for N4."""

from __future__ import annotations

import statistics
from typing import Any


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    k = (len(ordered) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(ordered) - 1)
    if f == c:
        return float(ordered[f])
    return float(ordered[f] + (ordered[c] - ordered[f]) * (k - f))


def simulate_task_result(
    task: dict[str, Any],
    *,
    arm: str,
) -> dict[str, Any]:
    """Deterministic hermetic outcome from fixture fields.

    Evidence arm may improve accept / reuse / retrieval when fixture provides
    ``evidence_boost``; never invents live LLM spend.
    """
    herm = task.get("hermetic") or {}
    base_accept = bool(herm.get("baseline_accept", True))
    evidence_accept = bool(herm.get("evidence_accept", base_accept))
    accepted = evidence_accept if arm == "evidence" else base_accept

    base_cost = float(herm.get("inference_cost_units", 1.0))
    eng = float(herm.get("engineering_cost_units", 1.0))
    latency = float(herm.get("latency_ms", 100.0))
    retries = float(herm.get("retries", 0.0))
    first_pass = float(herm.get("first_pass_test_rate", 1.0 if accepted else 0.0))
    skill_reuse = float(herm.get("skill_reuse_rate", 0.4))
    retrieval = float(herm.get("retrieval_precision", 0.5))
    review = float(herm.get("review_precision", 0.7))

    if arm == "evidence":
        boost = float(herm.get("evidence_boost", 0.05))
        skill_reuse = min(1.0, skill_reuse + boost)
        retrieval = min(1.0, retrieval + boost)
        # Slightly higher inference cost for evidence path (context retrieval)
        base_cost = base_cost * float(herm.get("evidence_cost_factor", 1.1))
        latency = latency * float(herm.get("evidence_latency_factor", 1.05))

    return {
        "task_id": task["task_id"],
        "stack_id": task["stack_id"],
        "difficulty": task["difficulty"],
        "held_out": bool(task.get("held_out")),
        "arm": arm,
        "accepted": accepted,
        "inference_cost_units": round(base_cost, 4),
        "engineering_cost_units": round(eng, 4),
        "latency_ms": round(latency, 4),
        "retries": retries,
        "first_pass_test_rate": first_pass,
        "skill_reuse_rate": round(skill_reuse, 4),
        "retrieval_precision": round(retrieval, 4),
        "review_precision": round(review, 4),
    }


def summarize_arm(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    accepted = sum(1 for r in results if r["accepted"])
    inf = sum(float(r["inference_cost_units"]) for r in results)
    eng = sum(float(r["engineering_cost_units"]) for r in results)
    latencies = [float(r["latency_ms"]) for r in results]
    retries = statistics.fmean(float(r["retries"]) for r in results) if results else 0.0
    first_pass = (
        statistics.fmean(float(r["first_pass_test_rate"]) for r in results)
        if results
        else 0.0
    )
    skill = (
        statistics.fmean(float(r["skill_reuse_rate"]) for r in results) if results else 0.0
    )
    retrieval = (
        statistics.fmean(float(r["retrieval_precision"]) for r in results)
        if results
        else 0.0
    )
    review = (
        statistics.fmean(float(r["review_precision"]) for r in results) if results else 0.0
    )
    return {
        "accepted": accepted,
        "total": total,
        "accept_rate": round(accepted / total, 4) if total else 0.0,
        "inference_cost_units": round(inf, 4),
        "engineering_cost_units": round(eng, 4),
        "latency_p50_ms": round(_percentile(latencies, 50), 4),
        "latency_p95_ms": round(_percentile(latencies, 95), 4),
        "retries": round(retries, 4),
        "first_pass_test_rate": round(first_pass, 4),
        "skill_reuse_rate": round(skill, 4),
        "retrieval_precision": round(retrieval, 4),
        "review_precision": round(review, 4),
    }


def primary_efficiency(arm: dict[str, Any]) -> float | None:
    denom = float(arm["inference_cost_units"]) + float(arm["engineering_cost_units"])
    if denom <= 0:
        return None
    return round(float(arm["accepted"]) / denom, 6)
