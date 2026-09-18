"""Validate task graph integrity."""

from __future__ import annotations

from typing import Any

LINK_TYPES = frozenset({"hard", "symlink"})


class GraphValidationError(ValueError):
    """Raised when a task graph is invalid."""


def normalize_dependency(dep: Any, *, task_id: str = "") -> str:
    """Return the target task id for a dependency in either form.

    Legacy form: a plain task-id string (ordering edge).
    Typed form (M40): an object ``{"target", "link", "contract"?, "paths"?}``
    where ``link`` is ``hard`` (version-locked contract coupling) or
    ``symlink`` (loose module path reference).
    """
    where = f"task {task_id}: " if task_id else ""
    if isinstance(dep, str):
        if not dep.strip():
            raise GraphValidationError(f"{where}dependency id must be non-empty")
        return dep
    if isinstance(dep, dict):
        target = dep.get("target")
        if not isinstance(target, str) or not target.strip():
            raise GraphValidationError(f"{where}typed dependency requires non-empty 'target'")
        link = dep.get("link")
        if link not in LINK_TYPES:
            raise GraphValidationError(
                f"{where}typed dependency 'link' must be one of {sorted(LINK_TYPES)}, got {link!r}"
            )
        contract = dep.get("contract")
        if contract is not None and not isinstance(contract, str):
            raise GraphValidationError(f"{where}typed dependency 'contract' must be a string")
        paths = dep.get("paths")
        if paths is not None and not (
            isinstance(paths, list) and all(isinstance(p, str) for p in paths)
        ):
            raise GraphValidationError(f"{where}typed dependency 'paths' must be a list of strings")
        return target
    raise GraphValidationError(f"{where}dependency must be a string or typed object")


def normalize_dependencies(task: dict) -> list[str]:
    """Return dependency target ids for a task, accepting both forms."""
    return [
        normalize_dependency(dep, task_id=str(task.get("id") or ""))
        for dep in task.get("dependencies") or []
    ]


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
        normalized = normalize_dependencies(task)
        for dep in normalized:
            if dep not in ids:
                raise GraphValidationError(f"task {task_id}: missing dependency {dep!r}")
            if dep == task_id:
                raise GraphValidationError(f"task {task_id}: self dependency")
        graph[task_id] = normalized

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
        for dep in normalize_dependencies(index[task_id]):
            visit(dep)
        visited.add(task_id)
        order.append(task_id)

    for task_id in ids:
        visit(task_id)
    return order
