"""Build and validate complete task graphs."""

from __future__ import annotations

from pathlib import Path

from orchestrator.intent.infer_capabilities import infer_capabilities
from orchestrator.planner.decompose import decompose
from orchestrator.planner.validate_graph import GraphValidationError, topological_order, validate_task_graph
from orchestrator.schemas.validate import validate_document


def build_task_graph(objective: str, context: dict | None = None) -> dict:
    context = dict(context or {})
    intent = infer_capabilities(objective, context)
    tasks = decompose(objective, intent)
    validate_task_graph(tasks)
    for task in tasks:
        validate_document(task, "task.schema.json")

    return {
        "version": "1.0.0",
        "objective": objective,
        "domains_detected": intent.domains_detected,
        "security_sensitive": intent.security_sensitive,
        "stacks": intent.stacks,
        "execution_order": topological_order(tasks),
        "tasks": tasks,
    }


def write_task_graph(
    repo_root: Path,
    objective: str,
    context: dict | None = None,
    output_path: Path | None = None,
) -> dict:
    graph = build_task_graph(objective, context)
    out = output_path or (Path(repo_root) / ".agent" / "plans" / "draft" / "task-graph.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    import json

    with out.open("w", encoding="utf-8") as handle:
        json.dump(graph, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return graph
