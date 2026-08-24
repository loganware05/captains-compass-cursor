"""Render capability-aware planning sections for IMPLEMENTATION_PLAN.md."""

from __future__ import annotations

from orchestrator.plan_writer.build import CapabilityPlanArtifacts


def _bullet_list(items: list[str]) -> str:
    if not items:
        return "- *(none)*\n"
    return "".join(f"- {item}\n" for item in items)


def render_required_capabilities(artifacts: CapabilityPlanArtifacts) -> str:
    lines = [
        "## Required Capabilities",
        "",
        "Inferred from the objective and repository context.",
        "",
        _bullet_list(artifacts.resolve.get("required_capabilities") or []),
    ]
    domains = artifacts.resolve.get("domains_detected") or []
    if domains:
        lines.extend(["", f"**Domains detected:** {', '.join(domains)}"])
    if artifacts.resolve.get("security_sensitive"):
        lines.extend(["", "**Security-sensitive:** yes"])
    lines.append("")
    return "\n".join(lines)


def render_reusable_capabilities(artifacts: CapabilityPlanArtifacts) -> str:
    lines = [
        "## Reusable Capabilities Found",
        "",
        "Approved Compass Skills ranked for this objective (deterministic matcher).",
        "",
        "| Skill | Score | Notes |",
        "|---|---:|---|",
    ]
    for item in artifacts.resolve.get("ranked_skills") or []:
        skill_id = item["skill_id"]
        score = item["score"]
        note = "top match"
        if item.get("scoring_breakdown"):
            top_factor = max(item["scoring_breakdown"], key=lambda x: x["score"])
            note = f"{top_factor['factor']}={top_factor['score']}"
        lines.append(f"| `{skill_id}` | {score} | {note} |")

    gaps = artifacts.resolve.get("capability_gaps") or []
    lines.extend(["", "### Capability Gaps", ""])
    if gaps:
        lines.append(
            "The following required capabilities have **no approved Skill** in the registry:"
        )
        lines.append("")
        lines.extend(_bullet_list(gaps).splitlines())
        lines.extend(
            [
                "",
                "**Next steps:** propose a new Skill, external candidate review, or Captain-approved manual procedure. "
                "Do not silently improvise execution.",
            ]
        )
    else:
        lines.append("No capability gaps detected for the inferred requirements.")
    lines.append("")
    return "\n".join(lines)


def render_technology_intelligence_candidates(artifacts: CapabilityPlanArtifacts) -> str:
    import os

    provider_name = os.environ.get("COMPASS_TI_PROVIDER", "stub").strip().lower() or "stub"
    lines = [
        "## Technology Intelligence Candidates",
        "",
        "> **NOT APPROVED FOR EXECUTION** — discovery signals only.",
        "",
    ]
    candidates = artifacts.technology_intelligence_candidates
    if not candidates:
        lines.append(
            f"*No external candidates queried (Technology Intelligence provider: {provider_name}).*"
        )
    else:
        lines.extend(["| ID | Signal | Lifecycle |", "|---|---|---|"])
        for candidate in candidates:
            lines.append(
                f"| `{candidate.get('id')}` | {candidate.get('discovery_signal', 'n/a')} | "
                f"{candidate.get('lifecycle_stage', 'DISCOVERED')} |"
            )
        lines.extend(["", f"*Provider: `{provider_name}` (candidates remain non-executable).*"])
    lines.append("")
    return "\n".join(lines)


def render_experience_signals(artifacts: CapabilityPlanArtifacts) -> str:
    """Informational Experience readback — does not alter Skill rankings."""
    lines = [
        "## Experience Signals",
        "",
        "Informational readback from Experience fixtures/stores. "
        "**Does not auto-adjust matcher weights** (proposal-only via Skill `experience-routing`).",
        "",
    ]
    signals = artifacts.experience_signals or []
    if not signals:
        lines.append("*No Experience signals loaded for this plan.*")
    else:
        lines.extend(["| Experience | Outcome | Skills |", "|---|---|---|"])
        for item in signals:
            skills = ", ".join(f"`{s}`" for s in (item.get("skills_used") or [])[:5]) or "—"
            lines.append(
                f"| `{item.get('experience_id', 'n/a')}` | {item.get('outcome', 'n/a')} | {skills} |"
            )
    lines.append("")
    return "\n".join(lines)


def render_knowledge_context(artifacts: CapabilityPlanArtifacts) -> str:
    """Informational knowledge readback — does not alter Skill rankings."""
    lines = [
        "## Knowledge Context",
        "",
        f"Informational readback from `.agent/knowledge/` ({artifacts.knowledge_search_mode} search). "
        "**Does not alter Skill rankings or matcher weights.** "
        "Populate via explicit `./scripts/ingest-knowledge.sh`.",
        "",
    ]
    items = artifacts.knowledge_context or []
    if not items:
        lines.append("*No knowledge items matched this objective (store empty or no index).*")
    else:
        lines.extend(["| Item | Kind | Score | Title |", "|---|---|---:|---|"])
        for item in items:
            lines.append(
                f"| `{item.get('item_id', 'n/a')}` | {item.get('kind', 'n/a')} | "
                f"{item.get('query_score', 0)} | {str(item.get('title', '')).replace('|', '/')} |"
            )
    lines.append("")
    return "\n".join(lines)


def render_task_graph(artifacts: CapabilityPlanArtifacts) -> str:
    lines = [
        "## Task Graph",
        "",
        f"Execution order: {' → '.join(artifacts.task_graph.get('execution_order') or [])}",
        "",
        "| Task ID | Objective | Dependencies | Parallelizable |",
        "|---|---|---|---|",
    ]
    for task in artifacts.task_graph.get("tasks") or []:
        deps = ", ".join(task.get("dependencies") or []) or "—"
        parallel = "yes" if task.get("parallelizable") else "no"
        objective = task.get("objective", "").replace("|", "\\|")
        lines.append(
            f"| `{task['id']}` | {objective} | {deps} | {parallel} |"
        )
    lines.extend(
        [
            "",
            f"Machine artifact: `{artifacts.artifact_paths.get('task_graph', '')}`",
            "",
        ]
    )
    return "\n".join(lines)


def render_agent_configuration(artifacts: CapabilityPlanArtifacts) -> str:
    lines = [
        "## Proposed Agent Configuration",
        "",
        "One manifest per task. Reference profiles map to existing `.cursor/agents/` templates.",
        "",
        "| Task | Profile | Model class | Skills | Rationale |",
        "|---|---|---|---|---|",
    ]
    for manifest in artifacts.manifests.get("manifests") or []:
        skills = ", ".join(f"`{s}`" for s in manifest.get("skills") or []) or "—"
        rationale = manifest.get("rationale", "").replace("|", "\\|")
        model_class = (manifest.get("model") or {}).get("class", "inherit")
        lines.append(
            f"| `{manifest['task_id']}` | `{manifest['reference_profile']}` | "
            f"{model_class} | {skills} | {rationale} |"
        )
    lines.extend(
        [
            "",
            f"Machine artifact: `{artifacts.artifact_paths.get('manifests', '')}`",
            "",
        ]
    )
    return "\n".join(lines)


def render_evaluation_strategy(artifacts: CapabilityPlanArtifacts) -> str:
    return "\n".join(
        [
            "## Evaluation Strategy",
            "",
            "After implementation (post-approval), Captain Compass will determine success by:",
            "",
            "- Matching task acceptance criteria from the task graph",
            "- Applicable validation layers from `TESTING.md` / evidence matrix",
            "- Security and accessibility reviews when manifests include those tasks",
            "- Adversarial review before merge when scope is non-trivial",
            "- Comparison of outcome vs inferred required capabilities",
            "",
            "Capability planning quality for this plan is evaluated by:",
            "",
            "- Explicit capability gaps (must not be silent)",
            "- Deterministic Skill ranking reproducibility",
            "- Inspectable agent manifest rationale per task",
            "",
        ]
    )


def render_learning_plan(artifacts: CapabilityPlanArtifacts) -> str:
    return "\n".join(
        [
            "## Learning Plan",
            "",
            "Retain under `.agent/plans/"
            f"{artifacts.plan_id}/`:",
            "",
            _bullet_list(
                [
                    artifacts.artifact_paths.get("resolve", "resolve.json"),
                    artifacts.artifact_paths.get("task_graph", "task-graph.json"),
                    artifacts.artifact_paths.get("manifests", "manifests.json"),
                    "Link to issue, branch, PR, tests, and evaluation evidence after execution",
                ]
            ).rstrip(),
            "",
            "Use execution evidence in Milestone 2+ to tune Skill confidence and routing.",
            "",
        ]
    )


def render_approval_boundary() -> str:
    return "\n".join(
        [
            "## Approval Boundary",
            "",
            "**Implementation must not begin until the Captain explicitly approves this plan.**",
            "",
            "Machine-generated capability matches and agent manifests are **proposals** only. "
            "The Captain may approve, revise, or reject before any product implementation proceeds.",
            "",
        ]
    )


def render_capability_plan_sections(artifacts: CapabilityPlanArtifacts) -> str:
    sections = [
        render_required_capabilities(artifacts),
        render_reusable_capabilities(artifacts),
        render_technology_intelligence_candidates(artifacts),
        render_experience_signals(artifacts),
        render_knowledge_context(artifacts),
        render_task_graph(artifacts),
        render_agent_configuration(artifacts),
        render_evaluation_strategy(artifacts),
        render_learning_plan(artifacts),
        render_approval_boundary(),
    ]
    return "\n".join(sections)
