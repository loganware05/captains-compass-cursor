"""Promotion evidence gates (M50)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from orchestrator.behavior.ledger import list_records
from orchestrator.behavior.prompt_eval.report import PromptEvalReportError, load_report
from orchestrator.behavior.policy.states import CAPTAIN_REQUIRED


class PolicyGateError(ValueError):
    """Raised when a promotion gate fails closed."""


def proven_threshold() -> int:
    raw = os.environ.get("COMPASS_POLICY_PROVEN_THRESHOLD", "").strip()
    if not raw:
        raw = os.environ.get("COMPASS_PROVEN_SUCCESS_THRESHOLD", "2").strip() or "2"
    try:
        value = int(raw)
    except ValueError as exc:
        raise PolicyGateError(f"invalid proven threshold: {raw!r}") from exc
    if value < 1:
        raise PolicyGateError("proven threshold must be >= 1")
    return value


def require_captain_approved(to_state: str, *, captain_approved: bool) -> None:
    if to_state in CAPTAIN_REQUIRED and not captain_approved:
        raise PolicyGateError(
            f"transition to {to_state!r} requires --captain-approved"
        )


def require_prompt_eval_pass(repo_root: Path, report_id: str) -> dict[str, Any]:
    if not report_id:
        raise PolicyGateError("sandbox_evaluated requires --prompt-eval-report")
    try:
        report = load_report(repo_root, report_id)
    except PromptEvalReportError as exc:
        raise PolicyGateError(str(exc)) from exc
    if report.get("non_regression") != "pass":
        raise PolicyGateError(
            f"prompt-eval report {report_id!r} non_regression must be pass, "
            f"got {report.get('non_regression')!r}"
        )
    return report


def require_shadow_present(policy: dict[str, Any]) -> None:
    if not policy.get("shadow_report_id"):
        raise PolicyGateError(
            "transition to approved requires a prior shadow report "
            "(run northstar policy shadow first)"
        )


def count_successful_evaluations(
    repo_root: Path,
    *,
    policy_id: str,
    prompt_bundle_hash: str = "",
) -> tuple[int, list[str]]:
    """Count non-abstaining successful M46 evaluations referencing policy/bundle."""
    matched: list[str] = []
    for record in list_records(repo_root):
        if record.get("abstain"):
            continue
        if str(record.get("outcome") or "") != "success":
            continue
        evaluator = record.get("evaluator") or {}
        bundle = str(evaluator.get("prompt_bundle_hash") or "")
        evidence_blob = json.dumps(record.get("evidence") or [], sort_keys=True)
        hit = False
        if prompt_bundle_hash and bundle == prompt_bundle_hash:
            hit = True
        if policy_id and policy_id in evidence_blob:
            hit = True
        # Also accept evaluator.policy_id if present (forward-compatible)
        if policy_id and str(evaluator.get("policy_id") or "") == policy_id:
            hit = True
        if hit:
            matched.append(str(record.get("evaluation_id") or ""))
    return len(matched), matched


def require_proven_evidence(
    repo_root: Path,
    policy: dict[str, Any],
) -> list[str]:
    threshold = proven_threshold()
    count, ids = count_successful_evaluations(
        repo_root,
        policy_id=str(policy.get("policy_id") or ""),
        prompt_bundle_hash=str(policy.get("prompt_bundle_hash") or ""),
    )
    if count < threshold:
        raise PolicyGateError(
            f"proven requires >= {threshold} successful evaluations "
            f"referencing policy/bundle; found {count}"
        )
    return ids
