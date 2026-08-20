"""Map tasks to reference agent profiles and model classes."""

from __future__ import annotations

# Task id prefix/exact → reference agent profile id
TASK_PROFILE_MAP: tuple[tuple[str, str], ...] = (
    ("task-discovery", "repository-scout"),
    ("task-architecture", "architecture-agent"),
    ("task-impl-frontend", "implementation-agent"),
    ("task-impl-backend", "implementation-agent"),
    ("task-impl-database", "implementation-agent"),
    ("task-impl-ml", "implementation-agent"),
    ("task-impl-ios", "implementation-agent"),
    ("task-impl-docker", "implementation-agent"),
    ("task-implementation", "implementation-agent"),
    ("task-validation", "test-engineer"),
    ("task-security-review", "security-reviewer"),
    ("task-documentation", "documentation-agent"),
)

TASK_MODEL_CLASS: dict[str, str] = {
    "task-discovery": "reasoning-strong",
    "task-architecture": "reasoning-strong",
    "task-validation": "coding-strong",
    "task-security-review": "reasoning-strong",
    "task-documentation": "fast-iter",
}

DEFAULT_IMPL_MODEL = "coding-strong"
DEFAULT_ROLE_SUFFIX = "worker"


def reference_profile_for_task(task_id: str) -> str:
    for prefix, profile in TASK_PROFILE_MAP:
        if task_id == prefix:
            return profile
    if task_id.startswith("task-impl-"):
        return "implementation-agent"
    return "implementation-agent"


def model_class_for_task(task_id: str) -> str:
    if task_id in TASK_MODEL_CLASS:
        return TASK_MODEL_CLASS[task_id]
    if task_id.startswith("task-impl-"):
        return DEFAULT_IMPL_MODEL
    return "inherit"


def role_for_task(task_id: str, profile_id: str) -> str:
    if task_id == "task-discovery":
        return "discovery-worker"
    if task_id == "task-architecture":
        return "architecture-worker"
    if task_id.startswith("task-impl-"):
        return task_id.replace("task-impl-", "") + "-worker"
    if task_id == "task-implementation":
        return "implementation-worker"
    if task_id == "task-validation":
        return "validation-worker"
    if task_id == "task-security-review":
        return "security-review-worker"
    if task_id == "task-documentation":
        return "documentation-worker"
    return profile_id.replace("-agent", "").replace("-reviewer", "").replace("-scout", "") + f"-{DEFAULT_ROLE_SUFFIX}"


def permissions_for_task(task_id: str) -> list[str]:
    if task_id in {"task-discovery", "task-architecture", "task-security-review"}:
        return ["read-repo"]
    if task_id == "task-validation":
        return ["read-repo", "run-tests", "write-evidence"]
    if task_id == "task-documentation":
        return ["read-repo", "write-docs"]
    if task_id.startswith("task-impl-") or task_id == "task-implementation":
        return ["read-repo", "write-product-on-approved-branch"]
    return ["read-repo"]
