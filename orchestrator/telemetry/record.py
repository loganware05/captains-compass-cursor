"""Build ExecutionRun and Experience records from workstream inputs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.telemetry.store import write_execution_run, write_experience


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_execution_run(
    *,
    plan_id: str,
    task_id: str = "task-close-workstream",
    objective: str = "",
    outcome: str = "success",
    skills: list[str] | None = None,
    agents: list[str] | None = None,
    models: list[str] | None = None,
    provenance: dict[str, Any] | None = None,
    lessons: list[str] | None = None,
    retries: int = 0,
    run_id: str | None = None,
) -> dict:
    return {
        "run_id": run_id or f"run-{uuid4().hex[:12]}",
        "plan_id": plan_id,
        "task_id": task_id,
        "objective": objective,
        "outcome": outcome,
        "skills": list(skills or []),
        "agents": list(agents or []),
        "models": list(models or []),
        "provenance": dict(provenance or {}),
        "lessons": list(lessons or []),
        "retries": retries,
        "recorded_at": _utc_now(),
    }


def experience_from_run(
    run: dict,
    *,
    source_instance: str = "control-live",
    capabilities_exercised: list[str] | None = None,
    experience_id: str | None = None,
) -> dict:
    return {
        "experience_id": experience_id or f"exp-{uuid4().hex[:12]}",
        "plan_id": run["plan_id"],
        "run_id": run["run_id"],
        "objective": run.get("objective", ""),
        "outcome": run["outcome"],
        "source_instance": source_instance,
        "skills_used": list(run.get("skills") or []),
        "capabilities_exercised": list(capabilities_exercised or []),
        "lessons": list(run.get("lessons") or []),
        "provenance": dict(run.get("provenance") or {}),
        "created_at": _utc_now(),
    }


def record_workstream(
    repo_root: Path,
    *,
    plan_id: str,
    outcome: str = "success",
    objective: str = "",
    skills: list[str] | None = None,
    provenance: dict[str, Any] | None = None,
    lessons: list[str] | None = None,
    source_instance: str = "control-live",
    task_id: str = "task-close-workstream",
) -> dict[str, Path]:
    """Write ExecutionRun + linked Experience; return artifact paths."""
    run = build_execution_run(
        plan_id=plan_id,
        task_id=task_id,
        objective=objective,
        outcome=outcome,
        skills=skills,
        provenance=provenance,
        lessons=lessons,
    )
    experience = experience_from_run(run, source_instance=source_instance)
    run["experience_id"] = experience["experience_id"]
    run_path = write_execution_run(repo_root, run)
    exp_path = write_experience(repo_root, experience)
    return {"execution_run": run_path, "experience": exp_path}
