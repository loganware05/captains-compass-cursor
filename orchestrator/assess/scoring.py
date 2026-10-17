"""Deterministic difficulty factor scoring (Notion C3 weights)."""

from __future__ import annotations

from typing import Any

# Notion Cognitive Core — Project Difficulty & Capability-Fit Assessment
WEIGHTS: dict[str, float] = {
    "gap_severity": 0.25,
    "skill_uncertainty": 0.20,
    "repository_complexity": 0.15,
    "task_graph_complexity": 0.15,
    "operational_risk": 0.15,
    "validation_burden": 0.10,
}


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def band_for(score: float) -> str:
    if score < 25:
        return "low"
    if score < 50:
        return "moderate"
    if score < 75:
        return "high"
    return "very_high"


def score_gap_severity(
    *,
    required_count: int,
    gap_count: int,
    security_sensitive: bool,
) -> tuple[float, dict[str, Any]]:
    if required_count <= 0:
        base = 10.0 if gap_count == 0 else 40.0
    else:
        ratio = gap_count / required_count
        base = clamp(ratio * 100.0)
        # Covered requirements still imply residual coordination load.
        if gap_count == 0:
            base = clamp(min(28.0, required_count * 5.0))
    # Security-sensitive objectives always raise severity, even with zero gaps.
    if security_sensitive:
        base = clamp(base + (30.0 if gap_count == 0 else 20.0))
    return round(base, 2), {
        "required_count": required_count,
        "gap_count": gap_count,
        "security_sensitive": security_sensitive,
    }


def score_skill_uncertainty(
    *,
    ranked_skills: list[dict[str, Any]],
    proven_count: int,
    available_count: int,
) -> tuple[float, dict[str, Any]]:
    if not ranked_skills:
        return 85.0, {
            "ranked_count": 0,
            "top_score": 0.0,
            "proven_count": proven_count,
            "available_count": available_count,
        }
    top_score = float(ranked_skills[0].get("score") or 0.0)
    # Matcher scores are typically 0–1ish or 0–100; normalize softly.
    if top_score <= 1.5:
        top_pct = top_score * 100.0
    else:
        top_pct = top_score
    uncertainty = clamp(100.0 - top_pct)
    if proven_count == 0:
        uncertainty = clamp(uncertainty + 15.0)
    elif proven_count < 2:
        uncertainty = clamp(uncertainty + 8.0)
    if available_count == 0 and proven_count == 0:
        uncertainty = clamp(uncertainty + 10.0)
    return round(uncertainty, 2), {
        "ranked_count": len(ranked_skills),
        "top_score": round(top_score, 4),
        "proven_count": proven_count,
        "available_count": available_count,
    }


def score_repository_complexity(
    *,
    skill_count_fs: int,
    working_tree_dirty: bool,
    context_inode_present: bool,
    memory_doc_missing: int,
) -> tuple[float, dict[str, Any]]:
    # Cap skill-count contribution so large control libraries do not dominate.
    skill_component = clamp(min(skill_count_fs, 24) * 1.1)
    dirty = 12.0 if working_tree_dirty else 0.0
    inode = 8.0 if context_inode_present else 0.0
    missing = clamp(memory_doc_missing * 10.0)
    score = clamp(0.55 * skill_component + dirty + inode + missing)
    return round(score, 2), {
        "skill_count_fs": skill_count_fs,
        "working_tree_dirty": working_tree_dirty,
        "context_inode_present": context_inode_present,
        "memory_doc_missing": memory_doc_missing,
    }


def _dependency_depth(tasks: list[dict[str, Any]]) -> int:
    deps_map: dict[str, list[str]] = {}
    for task in tasks:
        tid = str(task.get("id") or task.get("task_id") or "")
        if not tid:
            continue
        deps = task.get("depends_on") or task.get("dependencies") or []
        deps_map[tid] = [str(d) for d in deps]

    memo: dict[str, int] = {}

    def depth(node: str, stack: set[str]) -> int:
        if node in memo:
            return memo[node]
        if node in stack:
            return 1
        stack.add(node)
        children = deps_map.get(node) or []
        if not children:
            value = 1
        else:
            value = 1 + max(depth(child, stack) for child in children)
        stack.remove(node)
        memo[node] = value
        return value

    if not deps_map:
        return 1 if tasks else 0
    return max(depth(node, set()) for node in deps_map)


def score_task_graph_complexity(
    *,
    tasks: list[dict[str, Any]],
) -> tuple[float, dict[str, Any]]:
    count = len(tasks)
    depth = _dependency_depth(tasks)
    # 1 task ~15, 6 tasks ~60, depth adds up to +30
    count_score = clamp(count * 12.0)
    depth_score = clamp(max(0, depth - 1) * 15.0)
    score = clamp(0.7 * count_score + 0.3 * depth_score)
    return round(score, 2), {
        "task_count": count,
        "dependency_depth": depth,
    }


def score_operational_risk(
    *,
    security_sensitive: bool,
    stacks: list[str],
    objective: str,
) -> tuple[float, dict[str, Any]]:
    score = 15.0
    reasons: list[str] = []
    if security_sensitive:
        score += 35.0
        reasons.append("security_sensitive")
    obj = objective.lower()
    for token, bump in (
        ("migration", 20.0),
        ("deploy", 15.0),
        ("production", 15.0),
        ("auth", 12.0),
        ("secret", 12.0),
        ("database", 10.0),
        ("rollback", 8.0),
    ):
        if token in obj:
            score += bump
            reasons.append(token)
    for stack in stacks:
        s = str(stack).lower()
        if s in {"postgres", "prisma", "docker", "kubernetes"}:
            score += 8.0
            reasons.append(f"stack:{s}")
    return round(clamp(score), 2), {"reasons": sorted(set(reasons)), "stacks": list(stacks)}


def score_validation_burden(
    *,
    objective: str,
    task_count: int,
    security_sensitive: bool,
) -> tuple[float, dict[str, Any]]:
    score = 20.0 + min(task_count, 8) * 5.0
    obj = objective.lower()
    hits: list[str] = []
    for token, bump in (
        ("e2e", 15.0),
        ("end-to-end", 15.0),
        ("accessibility", 12.0),
        ("a11y", 12.0),
        ("security", 15.0),
        ("browser", 10.0),
        ("screenshot", 8.0),
        ("integration", 8.0),
    ):
        if token in obj:
            score += bump
            hits.append(token)
    if security_sensitive:
        score += 10.0
        hits.append("security_sensitive")
    return round(clamp(score), 2), {"tokens": sorted(set(hits)), "task_count": task_count}


def combine_difficulty(factors: dict[str, float]) -> float:
    total = 0.0
    for key, weight in WEIGHTS.items():
        total += weight * float(factors[key])
    # Extreme operational risk must clear at least "high" when validation is heavy.
    if float(factors.get("operational_risk") or 0) >= 90:
        total = max(total, 52.0)
    if (
        float(factors.get("operational_risk") or 0) >= 90
        and float(factors.get("validation_burden") or 0) >= 70
    ):
        total = max(total, 58.0)
    return round(clamp(total), 2)


def compute_confidence(
    *,
    experience_count: int,
    gap_count: int,
    ranked_count: int,
    has_snapshot: bool,
) -> float:
    conf = 0.55
    if experience_count >= 5:
        conf += 0.2
    elif experience_count >= 2:
        conf += 0.1
    elif experience_count == 0:
        conf -= 0.15
    if gap_count:
        conf -= min(0.2, 0.05 * gap_count)
    if ranked_count == 0:
        conf -= 0.15
    if not has_snapshot:
        conf -= 0.05
    return round(max(0.05, min(0.95, conf)), 3)


def recommendations_for(band: str, *, gap_count: int) -> dict[str, Any]:
    if band == "low":
        return {
            "decompose": False,
            "validation_depth": "standard",
            "autonomy_budget_hint": "generous",
            "notes": "Low difficulty — standard validation; still Captain-gated.",
        }
    if band == "moderate":
        return {
            "decompose": gap_count > 0,
            "validation_depth": "elevated",
            "autonomy_budget_hint": "standard",
            "notes": "Moderate difficulty — prefer explicit task graph and elevated validation.",
        }
    if band == "high":
        return {
            "decompose": True,
            "validation_depth": "elevated",
            "autonomy_budget_hint": "tight",
            "notes": "High difficulty — decompose workstreams; tighten autonomy budget.",
        }
    return {
        "decompose": True,
        "validation_depth": "maximum",
        "autonomy_budget_hint": "minimal",
        "notes": "Very high difficulty — maximum validation; minimal autonomy until Captain review.",
    }
