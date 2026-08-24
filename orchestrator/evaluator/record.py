"""Write schema-valid Evaluation artifacts under .agent/evaluations/."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.schemas.validate import ValidationError, validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class EvaluatorError(ValueError):
    """Raised when evaluation recording is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluations_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evaluations"


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise EvaluatorError(f"unsafe {label}: {value!r}")
    return value


def build_evaluation(
    *,
    plan_id: str,
    objective: str,
    alternatives: list[dict[str, Any]],
    recommendation: str,
    hypothesis: str = "",
    method: str = "bounded-comparison",
    outcome: str = "complete",
    winner_alternative_id: str = "",
    evidence_paths: list[str] | None = None,
    provenance: dict[str, Any] | None = None,
    evaluation_id: str | None = None,
) -> dict:
    if len(alternatives) < 2:
        raise EvaluatorError("at least two alternatives are required")
    return {
        "evaluation_id": evaluation_id or f"eval-{uuid4().hex[:12]}",
        "plan_id": plan_id,
        "objective": objective,
        "hypothesis": hypothesis,
        "alternatives": alternatives,
        "method": method,
        "outcome": outcome,
        "recommendation": recommendation,
        "winner_alternative_id": winner_alternative_id,
        "evidence_paths": list(evidence_paths or []),
        "provenance": dict(provenance or {}),
        "created_at": _utc_now(),
        "captain_approval_required": True,
    }


def write_evaluation(repo_root: Path, evaluation: dict) -> Path:
    validate_document(evaluation, "evaluation.schema.json")
    eid = _safe_id(str(evaluation["evaluation_id"]), label="evaluation_id")
    out_dir = evaluations_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{eid}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(evaluation, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def record_evaluation(repo_root: Path, **kwargs: Any) -> Path:
    """Build + validate + write an Evaluation; return path."""
    try:
        evaluation = build_evaluation(**kwargs)
        return write_evaluation(repo_root, evaluation)
    except ValidationError as exc:
        raise EvaluatorError(str(exc)) from exc
