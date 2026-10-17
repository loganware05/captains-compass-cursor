"""Operator service for northstar assess project (C3)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.assess.enabled import require_assess_enabled
from orchestrator.assess.scoring import (
    WEIGHTS,
    band_for,
    combine_difficulty,
    compute_confidence,
    recommendations_for,
    score_gap_severity,
    score_operational_risk,
    score_repository_complexity,
    score_skill_uncertainty,
    score_task_graph_complexity,
    score_validation_burden,
)
from orchestrator.cognitive.git_facts import git_sha, working_tree_dirty
from orchestrator.planner.build import build_task_graph
from orchestrator.registry.load import load_registry, registry_skills
from orchestrator.resolver.resolve import resolve_capabilities
from orchestrator.schemas.validate import validate_document
from orchestrator.status.drift import REQUIRED_MEMORY_DOCS, count_skills_fs
from orchestrator.telemetry.store import list_experiences


class AssessServiceError(ValueError):
    """Operator-facing assess errors."""


def _skill_lifecycle(skill: dict[str, Any]) -> str:
    return str(
        skill.get("lifecycle_stage")
        or skill.get("lifecycle")
        or skill.get("status")
        or (skill.get("promotion") or {}).get("lifecycle")
        or ""
    ).upper()


def _count_lifecycle(skills: list[dict[str, Any]], label: str) -> int:
    # lifecycle_stage values look like PROVEN_SKILL / AVAILABLE_SKILL
    return sum(1 for skill in skills if label in _skill_lifecycle(skill))


def _optional_brain_snapshot(repo_root: Path) -> dict[str, Any] | None:
    try:
        from orchestrator.cognitive.enabled import brain_enabled
        from orchestrator.cognitive.store import load_latest

        if not brain_enabled():
            return None
        return load_latest(repo_root)
    except Exception:
        return None


def _memory_docs_missing(repo_root: Path) -> int:
    return sum(1 for name in REQUIRED_MEMORY_DOCS if not (repo_root / name).is_file())


def assess_project(repo_root: Path, objective: str) -> dict[str, Any]:
    """Build a schema-validated ProjectDifficultyAssessment (read-oriented)."""
    require_assess_enabled()
    repo_root = Path(repo_root)
    obj = (objective or "").strip()
    if not obj:
        raise AssessServiceError("--objective is required for assess project")

    resolve = resolve_capabilities(repo_root, obj)
    task_graph = build_task_graph(obj)
    tasks = list(task_graph.get("tasks") or [])
    registry = load_registry(repo_root)
    skills = registry_skills(registry)
    experiences = list_experiences(repo_root)
    # Also count fixture experiences when repo store empty (hermetic / CI)
    if not experiences:
        fixture_dir = repo_root / "tests" / "fixtures" / "experience"
        if fixture_dir.is_dir():
            import json

            for path in sorted(fixture_dir.glob("*.json")):
                try:
                    experiences.append(json.loads(path.read_text(encoding="utf-8")))
                except (OSError, json.JSONDecodeError):
                    continue

    ranked = [
        {
            "skill_id": item.skill_id,
            "score": item.score,
        }
        for item in resolve.ranked_skills
    ]
    proven = _count_lifecycle(skills, "PROVEN")
    available = _count_lifecycle(skills, "AVAILABLE")

    gap_score, gap_detail = score_gap_severity(
        required_count=len(resolve.intent.required_capabilities),
        gap_count=len(resolve.capability_gaps),
        security_sensitive=bool(resolve.intent.security_sensitive),
    )
    skill_score, skill_detail = score_skill_uncertainty(
        ranked_skills=ranked,
        proven_count=proven,
        available_count=available,
    )
    inode_present = (repo_root / ".agent" / "context" / "inodes").is_dir() or (
        repo_root / ".cursor" / "skills" / "context-inodes" / "SKILL.md"
    ).is_file()
    repo_score, repo_detail = score_repository_complexity(
        skill_count_fs=count_skills_fs(repo_root),
        working_tree_dirty=working_tree_dirty(repo_root),
        context_inode_present=inode_present,
        memory_doc_missing=_memory_docs_missing(repo_root),
    )
    graph_score, graph_detail = score_task_graph_complexity(tasks=tasks)
    op_score, op_detail = score_operational_risk(
        security_sensitive=bool(resolve.intent.security_sensitive),
        stacks=list(resolve.intent.stacks or []),
        objective=obj,
    )
    val_score, val_detail = score_validation_burden(
        objective=obj,
        task_count=len(tasks),
        security_sensitive=bool(resolve.intent.security_sensitive),
    )

    factors = {
        "gap_severity": gap_score,
        "skill_uncertainty": skill_score,
        "repository_complexity": repo_score,
        "task_graph_complexity": graph_score,
        "operational_risk": op_score,
        "validation_burden": val_score,
    }
    difficulty = combine_difficulty(factors)
    band = band_for(difficulty)

    snapshot = _optional_brain_snapshot(repo_root)
    head_sha = git_sha(repo_root)
    snapshot_id = str((snapshot or {}).get("snapshot_id") or "") or None
    snapshot_sha = str((snapshot or {}).get("repository_sha") or "") or head_sha
    version = ""
    version_path = repo_root / "VERSION"
    if version_path.is_file():
        version = version_path.read_text(encoding="utf-8").strip()

    confidence = compute_confidence(
        experience_count=len(experiences),
        gap_count=len(resolve.capability_gaps),
        ranked_count=len(ranked),
        has_snapshot=bool(snapshot_id),
    )

    citations: list[dict[str, str]] = []
    if head_sha:
        citations.append(
            {"kind": "git", "ref": f"HEAD={head_sha}", "claim_kind": "observed"}
        )
    if snapshot_id:
        citations.append(
            {"kind": "snapshot", "ref": snapshot_id, "claim_kind": "observed"}
        )
    if version:
        citations.append(
            {"kind": "version", "ref": f"VERSION={version}", "claim_kind": "observed"}
        )
    for cap in resolve.intent.required_capabilities[:12]:
        citations.append(
            {"kind": "capability", "ref": str(cap), "claim_kind": "documented"}
        )
    for skill_id in resolve.recommended_skill_ids[:8]:
        citations.append(
            {"kind": "skill", "ref": str(skill_id), "claim_kind": "documented"}
        )
    for exp in experiences[:5]:
        exp_id = str(exp.get("experience_id") or exp.get("id") or "")
        if exp_id:
            citations.append(
                {"kind": "experience", "ref": exp_id, "claim_kind": "observed"}
            )
    citations.append(
        {
            "kind": "task_graph",
            "ref": f"tasks={len(tasks)}",
            "claim_kind": "proposed",
        }
    )

    digest = hashlib.sha256(
        f"{obj}|{snapshot_sha}|{difficulty}|{band}".encode("utf-8")
    ).hexdigest()[:12]
    assessment_id = f"assess-{digest}-{uuid4().hex[:6]}"

    payload: dict[str, Any] = {
        "schema_version": "1",
        "assessment_id": assessment_id,
        "objective": obj,
        "difficulty_score": difficulty,
        "band": band,
        "confidence": confidence,
        "factors": factors,
        "weights": dict(WEIGHTS),
        "factor_details": {
            "gap_severity": gap_detail,
            "skill_uncertainty": skill_detail,
            "repository_complexity": repo_detail,
            "task_graph_complexity": graph_detail,
            "operational_risk": op_detail,
            "validation_burden": val_detail,
        },
        "citations": citations,
        "recommendations": recommendations_for(
            band, gap_count=len(resolve.capability_gaps)
        ),
        "repository_sha": snapshot_sha,
        "snapshot_id": snapshot_id,
        "northstar_version": version,
        "required_capabilities": list(resolve.intent.required_capabilities),
        "capability_gaps": list(resolve.capability_gaps),
        "recommended_skill_ids": list(resolve.recommended_skill_ids),
        "task_count": len(tasks),
        "experience_count": len(experiences),
        "notes": (
            "Cognitive Core C3 ProjectDifficultyAssessment. "
            "Advisory only — does not approve plans or mutate authority."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    validate_document(payload, "project-difficulty-assessment.schema.json")
    return payload
