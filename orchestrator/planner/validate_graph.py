"""Validate task graph integrity."""

from __future__ import annotations


class GraphValidationError(ValueError):
    """Raised when a task graph is invalid."""


def validate_task_graph(tasks: list[dict]) -> None:
    """Ensure dependencies exist and contain no cycles."""
    if not tasks:
        raise GraphValidationError("task graph is empty")

    ids = {task["id"] for task in tasks}
    if len(ids) != len(tasks):
        duplicates = [task["id"] for task in tasks]
        seen: set[str] = set()
        dupes = []
        for task_id in duplicates:
            if task_id in seen:
                dupes.append(task_id)
            seen.add(task_id)
        raise GraphValidationError(f"duplicate task ids: {sorted(set(dupes))}")

    graph: dict[str, list[str]] = {}
    for task in tasks:
        task_id = task["id"]
        deps = task.get("dependencies") or []
        if not isinstance(deps, list):
            raise GraphValidationError(f"task {task_id}: dependencies must be a list")
        for dep in deps:
            if dep not in ids:
                raise GraphValidationError(f"task {task_id}: missing dependency {dep!r}")
            if dep == task_id:
                raise GraphValidationError(f"task {task_id}: self dependency")
        graph[task_id] = list(deps)

    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str) -> None:
        if node in visiting:
            raise GraphValidationError(f"dependency cycle detected at task {node!r}")
        if node in visited:
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            dfs(dep)
        visiting.remove(node)
        visited.add(node)

    for task_id in ids:
        dfs(task_id)


def topological_order(tasks: list[dict]) -> list[str]:
    """Return task ids in dependency order (dependencies first)."""
    validate_task_graph(tasks)
    ids = [task["id"] for task in tasks]
    index = {task_id: task for task_id, task in ((t["id"], t) for t in tasks)}
    order: list[str] = []
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visited:
            return
        for dep in index[task_id].get("dependencies") or []:
            visit(dep)
        visited.add(task_id)
        order.append(task_id)

    for task_id in ids:
        visit(task_id)
    return order
