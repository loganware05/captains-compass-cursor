"""Resolve preferred reference profiles from proficiency and persistent-role registry."""

from __future__ import annotations

from pathlib import Path

from orchestrator.agents.promote import (
    PROFICIENCY_RANK,
    load_persistent_role_registry,
    load_proficiency_records,
)
from orchestrator.assembler.profiles import reference_profile_for_task

# Task id → classification tokens that may match proficiency / persistent roles
TASK_CLASSIFICATION_HINTS: dict[str, frozenset[str]] = {
    "task-discovery": frozenset({"discovery", "scouting", "repository"}),
    "task-architecture": frozenset({"architecture", "design"}),
    "task-validation": frozenset({"evaluation", "testing", "validation", "arbitration"}),
    "task-security-review": frozenset({"security"}),
    "task-documentation": frozenset({"documentation", "docs"}),
}


def _hints_for_task(task_id: str) -> frozenset[str]:
    if task_id in TASK_CLASSIFICATION_HINTS:
        return TASK_CLASSIFICATION_HINTS[task_id]
    if task_id.startswith("task-impl-"):
        return frozenset({"implementation", "coding"})
    if task_id == "task-implementation":
        return frozenset({"implementation", "coding"})
    return frozenset()


def _reference_profile_exists(repo_root: Path, profile_id: str) -> bool:
    path = Path(repo_root) / "orchestrator" / "reference-profiles" / f"{profile_id}.json"
    return path.is_file()


def _classification_overlap(classifications: list[str], hints: frozenset[str]) -> int:
    tokens = {c.lower().replace("_", "-") for c in classifications}
    hint_norm = {h.lower() for h in hints}
    return len(tokens & hint_norm)


def resolve_reference_profile(
    task: dict,
    repo_root: Path | None = None,
) -> tuple[str, list[dict[str, str | float]]]:
    """
    Prefer Captain-approved proficient / persistent-role agents when affinity matches.

    Staging drafts never override live profiles — only registry entries and
    captain_approved proficiency for agents that already have reference profiles.
    """
    task_id = str(task["id"])
    default = reference_profile_for_task(task_id)
    notes: list[dict[str, str | float]] = [
        {
            "factor": "reference_profile_default",
            "score": 0.0,
            "note": f"static map → {default}",
        }
    ]
    if repo_root is None:
        return default, notes

    repo_root = Path(repo_root)
    hints = _hints_for_task(task_id)
    candidates: list[tuple[int, int, str, str]] = []

    for role in load_persistent_role_registry(repo_root):
        if not role.get("captain_approved", True):
            continue
        agent_id = str(role.get("agent_id") or role.get("profile_id") or "")
        if not agent_id or not _reference_profile_exists(repo_root, agent_id):
            continue
        overlap = _classification_overlap(list(role.get("classifications") or []), hints)
        if agent_id == default:
            overlap = max(overlap, 1)
        if overlap <= 0 and agent_id != default:
            continue
        candidates.append((2, overlap, agent_id, "persistent-role-registry"))

    for record in load_proficiency_records(repo_root):
        if not record.get("captain_approved"):
            continue
        level = str(record.get("proficiency_level") or "")
        if PROFICIENCY_RANK.get(level, -1) < PROFICIENCY_RANK["proficient"]:
            continue
        agent_id = str(record.get("agent_id") or "")
        if not agent_id or not _reference_profile_exists(repo_root, agent_id):
            continue
        overlap = _classification_overlap(list(record.get("classifications") or []), hints)
        if agent_id == default:
            overlap = max(overlap, 1)
        if overlap <= 0:
            continue
        candidates.append(
            (PROFICIENCY_RANK.get(level, 0), overlap, agent_id, f"proficiency:{level}")
        )

    if not candidates:
        return default, notes

    candidates.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    rank, overlap, chosen, source = candidates[0]
    notes.append(
        {
            "factor": "persistent_role_preference",
            "score": float(rank),
            "note": (
                f"preferred {chosen} via {source} "
                f"(overlap={overlap}; default was {default})"
            ),
        }
    )
    return chosen, notes
