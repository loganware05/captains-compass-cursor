"""Operator service for northstar cycle begin|checkpoint|close + learning review (C4)."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.assess.enabled import assess_enabled
from orchestrator.assess.service import assess_project
from orchestrator.cognitive.git_facts import git_sha
from orchestrator.cycle.enabled import require_cycle_enabled
from orchestrator.cycle.store import CycleStoreError, list_cycles, load_cycle, write_cycle
from orchestrator.schemas.validate import validate_document
from orchestrator.telemetry.record import record_workstream
from orchestrator.telemetry.store import list_experiences

_TOKEN = re.compile(r"[a-z0-9]+", re.I)
_SAFE_CHECKPOINT = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


class CycleServiceError(ValueError):
    """Operator-facing cycle errors."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _optional_brain_snapshot(repo_root: Path) -> dict[str, Any] | None:
    try:
        from orchestrator.cognitive.enabled import brain_enabled
        from orchestrator.cognitive.store import load_latest

        if not brain_enabled():
            return None
        return load_latest(repo_root)
    except Exception:
        return None


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "") if len(t) > 2}


def _similar_experiences(
    repo_root: Path, objective: str, *, top_k: int = 5
) -> list[dict[str, Any]]:
    obj_tokens = _tokenize(objective)
    if not obj_tokens:
        return []
    scored: list[dict[str, Any]] = []
    for exp in list_experiences(repo_root):
        exp_id = str(exp.get("experience_id") or exp.get("id") or "")
        if not exp_id:
            continue
        other = _tokenize(str(exp.get("objective") or ""))
        if not other:
            continue
        overlap = len(obj_tokens & other) / max(1, len(obj_tokens | other))
        if overlap <= 0:
            continue
        scored.append(
            {
                "experience_id": exp_id,
                "similarity": round(overlap, 4),
                "outcome": str(exp.get("outcome") or ""),
                "objective": str(exp.get("objective") or "")[:200],
            }
        )
    scored.sort(key=lambda row: (-row["similarity"], row["experience_id"]))
    return scored[:top_k]


def _assessment_summary(assessment: dict[str, Any]) -> dict[str, Any]:
    return {
        "assessment_id": str(assessment.get("assessment_id") or ""),
        "difficulty_score": float(assessment.get("difficulty_score") or 0),
        "band": str(assessment.get("band") or ""),
        "confidence": float(assessment.get("confidence") or 0),
        "capability_gaps": list(assessment.get("capability_gaps") or []),
        "recommended_skill_ids": list(assessment.get("recommended_skill_ids") or []),
        "task_count": int(assessment.get("task_count") or 0),
        "experience_count": int(assessment.get("experience_count") or 0),
    }


def cycle_begin(
    repo_root: Path,
    objective: str,
    *,
    plan_id: str | None = None,
) -> dict[str, Any]:
    """Begin an adaptive cycle: compose C1 snapshot + C3 assess + Experience hits."""
    require_cycle_enabled()
    repo_root = Path(repo_root).resolve()
    obj = (objective or "").strip()
    if not obj:
        raise CycleServiceError("--objective is required for cycle begin")
    if not assess_enabled():
        raise CycleServiceError(
            "cycle begin requires COMPASS_ASSESS_ENABLED=1 for C3 assessment compose"
        )

    assessment = assess_project(repo_root, obj)
    summary = _assessment_summary(assessment)
    snapshot = _optional_brain_snapshot(repo_root)
    head_sha = git_sha(repo_root) or str(assessment.get("repository_sha") or "")
    snapshot_id = str((snapshot or {}).get("snapshot_id") or assessment.get("snapshot_id") or "") or None
    version = _version(repo_root)
    similar = _similar_experiences(repo_root, obj)
    plan = (plan_id or "").strip() or "unplanned-cycle"

    digest = hashlib.sha256(f"{obj}|{head_sha}|{summary['band']}".encode("utf-8")).hexdigest()[
        :12
    ]
    execution_id = f"cycle-{digest}-{uuid4().hex[:6]}"
    now = _utc_now()

    citations: list[dict[str, str]] = [
        {"kind": "git", "ref": f"HEAD={head_sha}", "claim_kind": "observed"},
        {
            "kind": "assessment",
            "ref": summary["assessment_id"],
            "claim_kind": "observed",
        },
    ]
    if snapshot_id:
        citations.append(
            {"kind": "snapshot", "ref": snapshot_id, "claim_kind": "observed"}
        )
    for exp in similar:
        citations.append(
            {
                "kind": "experience",
                "ref": exp["experience_id"],
                "claim_kind": "observed",
            }
        )
    citations.append(
        {
            "kind": "task_graph",
            "ref": f"tasks={summary['task_count']}",
            "claim_kind": "proposed",
        }
    )

    gaps = list(summary["capability_gaps"])
    forecast_note = (
        f"Estimated band {summary['band']} "
        f"(score {summary['difficulty_score']}, confidence {summary['confidence']}). "
        f"{len(gaps)} capability gap(s); {len(similar)} similar Experience(s)."
    )

    state: dict[str, Any] = {
        "schema_version": "1",
        "execution_id": execution_id,
        "phase": "begun",
        "status": "active",
        "objective": obj,
        "plan_id": plan,
        "repository_sha": head_sha,
        "snapshot_id": snapshot_id,
        "northstar_version": version,
        "assessment": summary,
        "capability_gaps": gaps,
        "recommended_skill_ids": list(summary["recommended_skill_ids"]),
        "task_count": summary["task_count"],
        "similar_experiences": similar,
        "checkpoints": [],
        "remaining_work_forecast": {
            "notes": forecast_note,
            "confidence": float(summary["confidence"]),
            "scope_expanded": False,
        },
        "difficulty_estimate": {
            "score": summary["difficulty_score"],
            "band": summary["band"],
            "confidence": summary["confidence"],
        },
        "difficulty_actual": None,
        "execution_run_id": None,
        "experience_id": None,
        "draft_proposals": [],
        "citations": citations,
        "notes": (
            "Cognitive Core C4 Adaptive Development Loop — begin. "
            "Advisory only; does not approve plans, promote Skills/Policies, or merge."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "created_at": now,
        "updated_at": now,
    }
    write_cycle(repo_root, state)
    return state


def cycle_checkpoint(
    repo_root: Path,
    execution_id: str,
    *,
    checkpoint_key: str,
    outcome: str = "in_progress",
    retries: int = 0,
    notes: str = "",
    skills: list[str] | None = None,
    cost_units: float = 0.0,
) -> dict[str, Any]:
    """Record an idempotent checkpoint; never expands approved scope."""
    require_cycle_enabled()
    repo_root = Path(repo_root).resolve()
    key = (checkpoint_key or "").strip()
    if not key:
        raise CycleServiceError("--checkpoint-key is required for cycle checkpoint")
    if not _SAFE_CHECKPOINT.match(key):
        raise CycleServiceError(f"invalid checkpoint_key: {key!r}")

    try:
        state = load_cycle(repo_root, execution_id)
    except CycleStoreError as exc:
        raise CycleServiceError(str(exc)) from exc

    if state.get("status") == "closed":
        raise CycleServiceError(f"cycle already closed: {execution_id}")

    for existing in state.get("checkpoints") or []:
        if existing.get("checkpoint_key") == key:
            # Idempotent return
            return state

    est = state.get("difficulty_estimate") or {}
    est_score = float(est.get("score") or 0)
    # Actual difficulty heuristic from retries + outcome friction (advisory).
    friction = min(100.0, est_score + (retries * 8.0) + (15.0 if outcome == "failed" else 0.0))
    band = str(est.get("band") or "moderate")
    if friction >= 75:
        band = "very_high"
    elif friction >= 50:
        band = "high"
    elif friction >= 25:
        band = "moderate"
    else:
        band = "low"

    entry = {
        "checkpoint_key": key,
        "recorded_at": _utc_now(),
        "outcome": outcome,
        "retries": int(retries),
        "notes": (notes or "")[:2000],
        "skills": list(skills or []),
        "cost_units": float(cost_units),
    }
    checkpoints = list(state.get("checkpoints") or [])
    checkpoints.append(entry)

    forecast = dict(state.get("remaining_work_forecast") or {})
    forecast["scope_expanded"] = False
    forecast["notes"] = (
        f"Checkpoint {key}: outcome={outcome}, retries={retries}. "
        f"Estimated score was {est_score}; observed friction≈{round(friction, 2)}. "
        "Approved scope unchanged."
    )
    forecast["confidence"] = max(
        0.1, min(1.0, float(forecast.get("confidence") or 0.5) - (0.05 * retries))
    )

    state["checkpoints"] = checkpoints
    state["phase"] = "checkpointed"
    state["difficulty_actual"] = {
        "score": round(friction, 2),
        "band": band,
        "confidence": forecast["confidence"],
        "basis": "checkpoint_friction",
    }
    state["remaining_work_forecast"] = forecast
    state["updated_at"] = _utc_now()
    state["approved_for_execution"] = False
    state["authority_mutation"] = False
    write_cycle(repo_root, state)
    return state


def cycle_close(
    repo_root: Path,
    execution_id: str,
    *,
    outcome: str = "success",
) -> dict[str, Any]:
    """Close cycle: finalize ExecutionRun + Experience; draft proposals only."""
    require_cycle_enabled()
    repo_root = Path(repo_root).resolve()
    if outcome not in {"success", "partial", "failed", "cancelled"}:
        raise CycleServiceError(
            "outcome must be one of: success, partial, failed, cancelled"
        )

    try:
        state = load_cycle(repo_root, execution_id)
    except CycleStoreError as exc:
        raise CycleServiceError(str(exc)) from exc

    if state.get("status") == "closed" and state.get("execution_run_id"):
        return state

    skills: list[str] = []
    retries = 0
    for cp in state.get("checkpoints") or []:
        retries = max(retries, int(cp.get("retries") or 0))
        for skill in cp.get("skills") or []:
            if skill and skill not in skills:
                skills.append(str(skill))

    paths = record_workstream(
        repo_root,
        plan_id=str(state.get("plan_id") or "unplanned-cycle"),
        outcome=outcome,
        objective=str(state.get("objective") or ""),
        skills=skills,
        provenance={
            "cycle_execution_id": execution_id,
            "repository_sha": state.get("repository_sha"),
            "assessment_id": (state.get("assessment") or {}).get("assessment_id"),
        },
        lessons=[
            "C4 cycle close — Experience recorded; promotion remains Captain-gated.",
        ],
        task_id="task-cycle-close",
    )
    run_doc = json_load(paths["execution_run"])
    exp_doc = json_load(paths["experience"])

    drafts: list[dict[str, Any]] = []
    gaps = list(state.get("capability_gaps") or [])
    if gaps:
        drafts.append(
            {
                "kind": "skill_gap",
                "title": "Capability gaps observed during cycle",
                "summary": f"{len(gaps)} gap(s): {', '.join(str(g) for g in gaps[:8])}",
                "evidence_paths": [str(paths["execution_run"]), str(paths["experience"])],
                "auto_promoted": False,
            }
        )
    est = state.get("difficulty_estimate") or {}
    actual = state.get("difficulty_actual") or {}
    if actual and abs(float(actual.get("score") or 0) - float(est.get("score") or 0)) >= 15:
        drafts.append(
            {
                "kind": "difficulty_calibration",
                "title": "Difficulty estimate vs observed friction drifted",
                "summary": (
                    f"estimate={est.get('score')} ({est.get('band')}) "
                    f"actual≈{actual.get('score')} ({actual.get('band')})"
                ),
                "evidence_paths": [str(paths["execution_run"])],
                "auto_promoted": False,
            }
        )
    drafts.append(
        {
            "kind": "learning_review",
            "title": "Captain Learning Review ready",
            "summary": (
                "Draft proposals only — run northstar learning review; "
                "do not promote Skills/Policies without Captain approval."
            ),
            "evidence_paths": [str(paths["experience"])],
            "auto_promoted": False,
        }
    )

    # Best-effort behavior evaluate when gate is on — never fail close.
    behavior_note = "behavior_eval_skipped"
    try:
        from orchestrator.behavior.enabled import behavior_eval_enabled
        from orchestrator.behavior.service import evaluate_execution

        if behavior_eval_enabled():
            evaluate_execution(repo_root, str(run_doc.get("run_id") or execution_id))
            behavior_note = "behavior_eval_attempted"
    except Exception:
        behavior_note = "behavior_eval_error"

    state["phase"] = "closed"
    state["status"] = "closed"
    state["execution_run_id"] = str(run_doc.get("run_id") or "")
    state["experience_id"] = str(exp_doc.get("experience_id") or "")
    state["draft_proposals"] = drafts
    state["updated_at"] = _utc_now()
    state["notes"] = (
        f"Cognitive Core C4 cycle closed ({outcome}). "
        f"{behavior_note}. Promotion gates unchanged; authority flags locked false."
    )
    state["approved_for_execution"] = False
    state["authority_mutation"] = False
    if state.get("difficulty_actual") is None:
        state["difficulty_actual"] = {
            "score": float((state.get("difficulty_estimate") or {}).get("score") or 0),
            "band": str((state.get("difficulty_estimate") or {}).get("band") or "low"),
            "confidence": float(
                (state.get("difficulty_estimate") or {}).get("confidence") or 0
            ),
            "basis": "close_without_checkpoint",
        }
    write_cycle(repo_root, state)
    return state


def json_load(path: Path) -> dict[str, Any]:
    import json

    return json.loads(Path(path).read_text(encoding="utf-8"))


def learning_review(repo_root: Path) -> dict[str, Any]:
    """Aggregate draft proposals from closed/active cycles — advisory only."""
    require_cycle_enabled()
    repo_root = Path(repo_root).resolve()
    cycles = list_cycles(repo_root)
    open_proposals: list[dict[str, Any]] = []
    citations: list[dict[str, str]] = []
    for cycle in cycles:
        exec_id = str(cycle.get("execution_id") or "")
        citations.append(
            {"kind": "cycle", "ref": exec_id, "claim_kind": "observed"}
        )
        for draft in cycle.get("draft_proposals") or []:
            open_proposals.append(
                {
                    "execution_id": exec_id,
                    "kind": str(draft.get("kind") or "unknown"),
                    "title": str(draft.get("title") or ""),
                    "summary": str(draft.get("summary") or ""),
                    "evidence_paths": list(draft.get("evidence_paths") or []),
                    "auto_promoted": False,
                    "cycle_status": str(cycle.get("status") or ""),
                }
            )

    digest = hashlib.sha256(
        f"review|{len(cycles)}|{len(open_proposals)}".encode("utf-8")
    ).hexdigest()[:12]
    payload: dict[str, Any] = {
        "schema_version": "1",
        "review_id": f"learning-review-{digest}-{uuid4().hex[:6]}",
        "cycles_scanned": len(cycles),
        "open_proposals": open_proposals,
        "citations": citations,
        "northstar_version": _version(repo_root),
        "notes": (
            "Captain Learning Review — advisory packet of draft proposals. "
            "Does not install Skills, activate Policies, merge PRs, or grant authority."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }
    validate_document(payload, "learning-review.schema.json")
    return payload
