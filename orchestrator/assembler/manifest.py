"""Build per-task agent manifests from task graphs and capability registry."""

from __future__ import annotations

from pathlib import Path

from orchestrator.assembler.profiles import (
    model_class_for_task,
    permissions_for_task,
    reference_profile_for_task,
    role_for_task,
)
from orchestrator.matcher.score import rank_skills
from orchestrator.model_profiles import load_catalog
from orchestrator.registry.load import load_registry, registry_skills
from orchestrator.schemas.validate import ValidationError, validate_document


class ManifestBuildError(ValueError):
    """Raised when manifest assembly fails."""


def _model_recommendation(model_class: str) -> dict:
    catalog = load_catalog()
    for profile in catalog["profiles"]:
        if profile["class"] == model_class:
            slugs = profile.get("recommended_slugs") or ["inherit"]
            return {"class": model_class, "recommendation": slugs[0]}
    return {"class": model_class, "recommendation": "inherit"}


def _select_skills(
    skills: list[dict],
    required_capabilities: list[str],
    *,
    reference_profile: str,
    stacks: list[str],
    security_sensitive: bool,
    top_n: int,
) -> tuple[list[str], list[dict]]:
    ranked = rank_skills(
        skills,
        required_capabilities,
        stacks=stacks,
        security_sensitive=security_sensitive,
        preferred_profile=reference_profile,
    )
    if not ranked:
        return [], []
    chosen = ranked[:top_n]
    return [item.skill_id for item in chosen], chosen[0].scoring_breakdown


def _rationale(
    task: dict,
    reference_profile: str,
    skill_ids: list[str],
    model_class: str,
) -> str:
    caps = ", ".join(task.get("required_capabilities") or []) or "general"
    skills = ", ".join(skill_ids) if skill_ids else "none matched"
    return (
        f"Task '{task['id']}' requires [{caps}]. "
        f"Reference profile '{reference_profile}' with model class '{model_class}'. "
        f"Selected Skills: [{skills}]."
    )


def build_manifest_for_task(
    task: dict,
    skills: list[dict],
    *,
    stacks: list[str],
    security_sensitive: bool,
    plan_id: str,
    top_n: int = 3,
) -> dict:
    task_id = task["id"]
    reference_profile = reference_profile_for_task(task_id)
    model_class = model_class_for_task(task_id)
    required = list(task.get("required_capabilities") or [])

    skill_ids, breakdown = _select_skills(
        skills,
        required,
        reference_profile=reference_profile,
        stacks=stacks,
        security_sensitive=security_sensitive,
        top_n=top_n,
    )

    manifest = {
        "task_id": task_id,
        "role": role_for_task(task_id, reference_profile),
        "reference_profile": reference_profile,
        "model": _model_recommendation(model_class),
        "skills": skill_ids,
        "tools": ["Read", "Shell", "Grep", "Glob"],
        "permissions": permissions_for_task(task_id),
        "autonomy_budget": {
            "max_iterations": 10 if task_id.startswith("task-impl") or task_id == "task-implementation" else 5,
            "ledger_path": f".agent/budgets/{plan_id}.md",
        },
        "rationale": _rationale(task, reference_profile, skill_ids, model_class),
    }
    if breakdown:
        manifest["scoring_breakdown"] = breakdown

    validate_document(manifest, "agent-manifest.schema.json")
    return manifest


def build_manifests(
    task_graph: dict,
    registry: dict,
    *,
    plan_id: str = "draft",
    top_n: int = 3,
) -> dict:
    tasks = task_graph.get("tasks") or []
    if not tasks:
        raise ManifestBuildError("task graph contains no tasks")

    skills = registry_skills(registry)
    stacks = list(task_graph.get("stacks") or [])
    security_sensitive = bool(task_graph.get("security_sensitive"))

    manifests = [
        build_manifest_for_task(
            task,
            skills,
            stacks=stacks,
            security_sensitive=security_sensitive,
            plan_id=plan_id,
            top_n=top_n,
        )
        for task in tasks
    ]

    payload = {
        "version": "1.0.0",
        "plan_id": plan_id,
        "objective": task_graph.get("objective", ""),
        "manifests": manifests,
    }
    return payload


def build_manifests_for_objective(
    repo_root: Path,
    objective: str,
    context: dict | None = None,
    *,
    plan_id: str = "draft",
    top_n: int = 3,
) -> dict:
    from orchestrator.planner.build import build_task_graph

    repo_root = Path(repo_root)
    context = dict(context or {})
    task_graph = build_task_graph(objective, context)
    registry = load_registry(repo_root)
    return build_manifests(task_graph, registry, plan_id=plan_id, top_n=top_n)


def write_manifests(
    repo_root: Path,
    objective: str,
    context: dict | None = None,
    *,
    plan_id: str = "draft",
    output_path: Path | None = None,
) -> dict:
    import json

    payload = build_manifests_for_objective(
        repo_root, objective, context, plan_id=plan_id
    )
    out = output_path or (Path(repo_root) / ".agent" / "plans" / plan_id / "manifests.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return payload
