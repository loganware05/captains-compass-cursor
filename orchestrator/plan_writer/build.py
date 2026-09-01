"""Assemble machine-readable planning artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from orchestrator.assembler.manifest import build_manifests
from orchestrator.planner.build import build_task_graph
from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider
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
    experience_signals: list[dict] = field(default_factory=list)
    knowledge_context: list[dict] = field(default_factory=list)
    knowledge_search_mode: str = "keyword"
    performance_context: list[dict] = field(default_factory=list)
    procedure_context: list[dict] = field(default_factory=list)
    artifact_context: list[dict] = field(default_factory=list)
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

    ti_provider = select_ti_provider(repo_root)
    experience_signals: list[dict] = []
    knowledge_context: list[dict] = []
    knowledge_search_mode = "keyword"
    performance_context: list[dict] = []
    procedure_context: list[dict] = []
    artifact_context: list[dict] = []
    candidates: list[dict] = []

    try:
        from orchestrator.planning.context_selection import fetch_plan_context_slices, load_active_context_profile

        active_profile = load_active_context_profile(repo_root)
        slices = fetch_plan_context_slices(repo_root, objective, profile=active_profile)
        knowledge_context = list(slices.get("knowledge_context") or [])
        knowledge_search_mode = str(slices.get("knowledge_search_mode") or "keyword")
        performance_context = list(slices.get("performance_context") or [])
        procedure_context = list(slices.get("procedure_context") or [])
        artifact_context = list(slices.get("artifact_context") or [])
        candidates = list(slices.get("technology_intelligence_candidates") or [])
        experience_signals = list(slices.get("experience_signals") or [])
    except Exception:
        from orchestrator.planning.context_selection import load_active_context_profile

        try:
            active_profile = load_active_context_profile(repo_root)
            profile_slices = active_profile["slices"]
        except Exception:
            from orchestrator.planning.context_selection import DEFAULT_SLICE_CONFIG

            profile_slices = DEFAULT_SLICE_CONFIG
        if profile_slices["technology_intelligence"]["enabled"]:
            ti_top = profile_slices["technology_intelligence"]["top_n"]
            candidates = [
                item.to_dict()
                for item in ti_provider.discover_candidates(objective, context)
            ][:ti_top]

        if profile_slices["experience_signals"]["enabled"]:
            exp_top = profile_slices["experience_signals"]["top_n"]
            for folder in (
                repo_root / "tests" / "fixtures" / "experience",
                repo_root / ".agent" / "experience",
            ):
                if not folder.is_dir():
                    continue
                for path in sorted(folder.glob("*.json"))[:exp_top]:
                    try:
                        with path.open(encoding="utf-8") as handle:
                            doc = json.load(handle)
                        if isinstance(doc, dict) and doc.get("experience_id"):
                            experience_signals.append(
                                {
                                    "experience_id": doc.get("experience_id"),
                                    "outcome": doc.get("outcome"),
                                    "skills_used": list(doc.get("skills_used") or [])[:8],
                                }
                            )
                    except (OSError, json.JSONDecodeError):
                        continue

        try:
            from orchestrator.knowledge.vector_index import select_knowledge_search_mode

            knowledge_search_mode = select_knowledge_search_mode(repo_root)
        except Exception:
            knowledge_search_mode = "keyword"

        if profile_slices["knowledge"]["enabled"] and profile_slices["knowledge"]["top_n"] > 0:
            try:
                from orchestrator.knowledge.query import query_knowledge

                knowledge_context = query_knowledge(
                    repo_root,
                    objective,
                    top_n=profile_slices["knowledge"]["top_n"],
                    rebuild_index=False,
                    mode=knowledge_search_mode,
                )
            except Exception:
                knowledge_context = []

        if profile_slices["performance"]["enabled"] and profile_slices["performance"]["top_n"] > 0:
            try:
                from orchestrator.knowledge.query import query_knowledge

                performance_context = query_knowledge(
                    repo_root,
                    objective,
                    kind="performance",
                    top_n=profile_slices["performance"]["top_n"],
                    rebuild_index=False,
                    mode=knowledge_search_mode,
                )
            except Exception:
                performance_context = []

        if profile_slices["procedure"]["enabled"] and profile_slices["procedure"]["top_n"] > 0:
            try:
                from orchestrator.knowledge.query import query_knowledge

                procedure_context = query_knowledge(
                    repo_root,
                    objective,
                    kind="procedure",
                    top_n=profile_slices["procedure"]["top_n"],
                    rebuild_index=False,
                    mode=knowledge_search_mode,
                )
            except Exception:
                procedure_context = []

        if profile_slices["artifact"]["enabled"] and profile_slices["artifact"]["top_n"] > 0:
            try:
                from orchestrator.knowledge.query import query_knowledge

                artifact_context = query_knowledge(
                    repo_root,
                    objective,
                    kind="artifact",
                    top_n=profile_slices["artifact"]["top_n"],
                    rebuild_index=False,
                    mode=knowledge_search_mode,
                )
            except Exception:
                artifact_context = []

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
        experience_signals=experience_signals,
        knowledge_context=knowledge_context,
        knowledge_search_mode=knowledge_search_mode,
        performance_context=performance_context,
        procedure_context=procedure_context,
        artifact_context=artifact_context,
        artifact_paths={
            "task_graph": str(task_graph_path.relative_to(repo_root)),
            "manifests": str(manifests_path.relative_to(repo_root)),
            "resolve": str(resolve_path.relative_to(repo_root)),
        },
    )
