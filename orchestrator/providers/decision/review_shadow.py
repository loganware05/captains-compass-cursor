"""Shadow-mode review triage: DecisionProvider signals vs deterministic review."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from orchestrator.providers.decision.change_state import build_review_change_summary
from orchestrator.providers.decision.file_provider import (
    decision_review_shadow_enabled,
    select_decision_provider,
)
from orchestrator.providers.decision.types import ReviewTriageRequest, ReviewTriageResult

EVIDENCE_ROOT_REL = Path(".agent") / "evidence" / "m44-jev-review-triage"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_review_triage_evidence(
    repo_root: Path,
    *,
    change_hash: str,
    result: ReviewTriageResult,
    baseline: dict[str, Any],
    plan_id: str | None = None,
) -> dict[str, Any]:
    """Persist full review-triage artifact under `.agent/evidence/` only."""
    repo_root = Path(repo_root)
    run_id = f"{_utc_stamp()}-{uuid.uuid4().hex[:8]}"
    rel_dir = EVIDENCE_ROOT_REL / "shadow" / run_id
    abs_dir = repo_root / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "northstar.decision_review_triage.v1",
        "run_id": run_id,
        "plan_id_ref": plan_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "change_hash": change_hash,
        "applied": False,
        "baseline": baseline,
        "provider_result": result.to_dict(applied=False),
        "env": {
            "COMPASS_DECISION_PROVIDER": os.environ.get("COMPASS_DECISION_PROVIDER", "stub"),
            "COMPASS_DECISION_REVIEW_SHADOW": os.environ.get(
                "COMPASS_DECISION_REVIEW_SHADOW", ""
            ),
            "COMPASS_JEV_MODEL_ID": os.environ.get("COMPASS_JEV_MODEL_ID", ""),
        },
    }
    path = abs_dir / "decision-review-triage.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    rel_path = str(rel_dir / "decision-review-triage.json")
    return {
        "evidence_id": run_id,
        "evidence_path": rel_path,
        "applied": False,
        "provider": result.provider,
        "model_id": result.model_id,
        "abstain": result.abstain,
        "investigation_priority": result.investigation_priority,
        "specialist_security_warranted": result.specialist_security_warranted,
        "error": result.error,
    }


def maybe_run_review_triage_shadow(
    repo_root: Path,
    *,
    changed_paths: Sequence[str] | None = None,
    domains: Sequence[str] | None = None,
    specialist_skill_ids: Sequence[str] | None = None,
    candidate_count: int = 0,
    objective: str = "",
    plan_id: str | None = None,
) -> dict[str, Any] | None:
    """If review shadow enabled and provider ≠ stub, write evidence; never mutate review."""
    if not decision_review_shadow_enabled():
        return None
    provider = select_decision_provider(repo_root)
    if getattr(provider, "name", "stub") == "stub":
        return None

    summary, change_hash, _state = build_review_change_summary(
        changed_paths=changed_paths,
        domains=domains,
        specialist_skill_ids=specialist_skill_ids,
        candidate_count=candidate_count,
        objective=objective,
    )
    request = ReviewTriageRequest(change=summary, change_hash=change_hash)
    result = provider.triage_review(request)
    baseline = {
        "domains": list(summary.domains),
        "path_flags": dict(summary.path_flags),
        "specialist_skill_ids": list(summary.specialist_skill_ids),
        "candidate_count": summary.candidate_count,
    }
    return write_review_triage_evidence(
        repo_root,
        change_hash=change_hash,
        result=result,
        baseline=baseline,
        plan_id=plan_id,
    )
