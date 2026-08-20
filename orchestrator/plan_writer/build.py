"""Assemble machine-readable planning artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from orchestrator.assembler.manifest import build_manifests
from orchestrator.planner.build import build_task_graph
from orchestrator.providers.technology_intelligence import StubTechnologyIntelligenceProvider
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates
from orchestrator.registry.compiler import write_registry
from orchestrator.registry.load import load_registry
from orchestrator.resolver.resolve import resolve_capabilities


@dataclass
class CapabilityPlanArtifacts:
    plan_id: str
    objective: str
    resolve: dict
    task_graph: dict
    manifests: dict
    technology_intelligence_candidates: list[dict] = field(default_factory=list)
    artifact_paths: dict[str, str] = field(default_factory=dict)


def build_capability_plan(
    repo_root: Path,
    objective: str,
    context: dict | None = None,
    *,
    plan_id: str = "draft",
) -> CapabilityPlanArtifacts:
    repo_root = Path(repo_root)
    context = dict(context or {})
    write_registry(repo_root)

    resolve_result = resolve_capabilities(repo_root, objective, context)
    task_graph = build_task_graph(objective, context)
    registry = load_registry(repo_root)
    manifests = build_manifests(task_graph, registry, plan_id=plan_id)

    ti_provider = StubTechnologyIntelligenceProvider()
    candidates = [
        item.to_dict()
        for item in ti_provider.discover_candidates(objective, context)
    ]
    validate_ti_candidates(candidates)

    plans_dir = repo_root / ".agent" / "plans" / plan_id
    plans_dir.mkdir(parents=True, exist_ok=True)

    task_graph_path = plans_dir / "task-graph.json"
    manifests_path = plans_dir / "manifests.json"
    resolve_path = plans_dir / "resolve.json"

    with task_graph_path.open("w", encoding="utf-8") as handle:
        json.dump(task_graph, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with manifests_path.open("w", encoding="utf-8") as handle:
        json.dump(manifests, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with resolve_path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "objective": objective,
                "required_capabilities": resolve_result.intent.required_capabilities,
                "capability_gaps": resolve_result.capability_gaps,
                "recommended_skill_ids": resolve_result.recommended_skill_ids,
                "domains_detected": resolve_result.intent.domains_detected,
                "security_sensitive": resolve_result.intent.security_sensitive,
                "stacks": resolve_result.intent.stacks,
                "ranked_skills": [
                    {
                        "skill_id": item.skill_id,
                        "score": item.score,
                        "scoring_breakdown": item.scoring_breakdown,
                    }
                    for item in resolve_result.ranked_skills
                ],
            },
            handle,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")

    resolve_payload = {
        "objective": objective,
        "required_capabilities": resolve_result.intent.required_capabilities,
        "capability_gaps": resolve_result.capability_gaps,
        "recommended_skill_ids": resolve_result.recommended_skill_ids,
        "domains_detected": resolve_result.intent.domains_detected,
        "security_sensitive": resolve_result.intent.security_sensitive,
        "stacks": resolve_result.intent.stacks,
        "ranked_skills": [
            {
                "skill_id": item.skill_id,
                "score": item.score,
                "scoring_breakdown": item.scoring_breakdown,
            }
            for item in resolve_result.ranked_skills
        ],
    }

    return CapabilityPlanArtifacts(
        plan_id=plan_id,
        objective=objective,
        resolve=resolve_payload,
        task_graph=task_graph,
        manifests=manifests,
        technology_intelligence_candidates=candidates,
        artifact_paths={
            "task_graph": str(task_graph_path.relative_to(repo_root)),
            "manifests": str(manifests_path.relative_to(repo_root)),
            "resolve": str(resolve_path.relative_to(repo_root)),
        },
    )
