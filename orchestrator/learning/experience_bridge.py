"""Bridge skill-learning-runs into ExecutionRun + Experience records (M20)."""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator.promotion.advance import (
    PromotionError,
    count_successful_experiences_for_skill,
    load_candidate_json,
    proven_threshold,
    write_staging_candidate,
)
from orchestrator.telemetry.record import record_workstream


class ExperienceBridgeError(ValueError):
    """Raised when learning-run → Experience bridging fails closed."""


def load_learning_run(path: Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict) or doc.get("kind") != "skill-learning-run":
        raise ExperienceBridgeError("file is not a skill-learning-run report")
    return doc


def _skills_for_entry(entry: dict) -> list[str]:
    skills = ["skill-learning-loop"]
    target = str(entry.get("target_skill_slug") or entry.get("skill_slug") or "")
    if target and target not in skills:
        skills.insert(0, target)
    return skills


def bridge_learning_run_to_experiences(
    repo_root: Path,
    learning_run: dict | Path,
    *,
    source_instance: str = "control-test",
    plan_id: str | None = None,
) -> dict:
    """
    Record one Experience per learning-run result.

    Does not promote to PROVEN or mutate live Skills.
    """
    repo_root = Path(repo_root).resolve()
    if isinstance(learning_run, (str, Path)):
        report = load_learning_run(Path(learning_run))
    else:
        report = dict(learning_run)
    if report.get("kind") != "skill-learning-run":
        raise ExperienceBridgeError("expected kind=skill-learning-run")

    run_id = str(report.get("run_id") or "learning-run")
    plan = plan_id or f"skill-learning-{run_id}"
    results = report.get("results") or []
    if not isinstance(results, list) or not results:
        raise ExperienceBridgeError("learning run has no results to bridge")

    recorded: list[dict] = []
    for index, entry in enumerate(results):
        if not isinstance(entry, dict):
            continue
        skills = _skills_for_entry(entry)
        if entry.get("mode") == "improve-existing":
            lessons = [
                f"Similar existing Skill `{entry.get('target_skill_slug')}` "
                "received an improvement proposal from categorized Stars."
            ]
        else:
            lessons = [
                f"New Skill draft `{entry.get('skill_slug')}` staged from categorized Stars."
            ]
        paths = record_workstream(
            repo_root,
            plan_id=plan,
            outcome="success",
            objective=str(report.get("objective") or "skill learning loop"),
            skills=skills,
            provenance={
                "learning_run_id": run_id,
                "candidate_id": entry.get("candidate_id"),
                "star_category": entry.get("star_category"),
                "mode": entry.get("mode"),
                "source_repo_path": str(entry.get("staging_path") or ""),
            },
            lessons=lessons,
            source_instance=source_instance,
            task_id=f"task-skill-learning-{index}",
        )
        recorded.append(
            {
                "candidate_id": entry.get("candidate_id"),
                "skills_used": skills,
                "execution_run": str(paths["execution_run"]),
                "experience": str(paths["experience"]),
            }
        )

    return {
        "kind": "skill-learning-experience-bridge",
        "learning_run_id": run_id,
        "plan_id": plan,
        "count": len(recorded),
        "records": recorded,
        "approved_for_execution": False,
        "notes": "Experiences recorded only — PROVEN still requires --captain-approved",
    }


def promote_proven_from_bridge(
    repo_root: Path,
    *,
    candidate_path: Path,
    skill_slug: str,
    evidence_paths: list[str],
    captain_approved: bool,
) -> Path:
    """Advance staging candidate to PROVEN_SKILL when Experience threshold is met."""
    if not captain_approved:
        raise ExperienceBridgeError("PROVEN_SKILL requires --captain-approved")
    candidate = load_candidate_json(Path(candidate_path))
    successes = count_successful_experiences_for_skill(
        repo_root,
        skill_slug,
        candidate_id=str(candidate.get("id") or "") or None,
    )
    threshold = proven_threshold()
    if successes < threshold:
        raise ExperienceBridgeError(
            f"PROVEN_SKILL requires ≥{threshold} successful Experiences "
            f"for {skill_slug!r}; found {successes}"
        )
    try:
        return write_staging_candidate(
            repo_root,
            candidate,
            target_stage="PROVEN_SKILL",
            evidence_paths=evidence_paths,
            captain_approved=True,
            skill_slug=skill_slug,
        )
    except PromotionError as exc:
        raise ExperienceBridgeError(str(exc)) from exc
