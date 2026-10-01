"""Operator service layer for northstar prompt-eval (M49)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from orchestrator.behavior.enabled import require_prompt_eval_enabled
from orchestrator.behavior.prompt_eval.compare import (
    PromptEvalCompareError,
    compose_baseline_and_candidate,
    run_prompt_eval,
)
from orchestrator.behavior.prompt_eval.cases import PromptEvalCase, load_cases
from orchestrator.behavior.prompt_eval.report import (
    PromptEvalReportError,
    list_reports,
    load_report,
    prompt_eval_root,
)


class PromptEvalServiceError(ValueError):
    """Operator-facing prompt-eval errors."""


def run_harness(
    repo_root: Path,
    *,
    cases_path: Path | None = None,
    control_root: Path | None = None,
) -> dict[str, Any]:
    require_prompt_eval_enabled()
    try:
        report = run_prompt_eval(
            repo_root,
            cases_path=cases_path,
            control_root=control_root,
            persist=True,
        )
    except PromptEvalCompareError as exc:
        raise PromptEvalServiceError(str(exc)) from exc
    return {"status": "completed", "report": report}


def compare_bundles(
    repo_root: Path,
    *,
    agent: str = "",
    skill_id: str = "",
    task_type: str = "",
    model_hint: str = "",
    cases_path: Path | None = None,
    control_root: Path | None = None,
) -> dict[str, Any]:
    """Compare baseline vs candidate for one context (optional first matching case)."""
    require_prompt_eval_enabled()
    control = Path(control_root or repo_root)
    if cases_path:
        cases = load_cases(Path(cases_path))
        case = next(
            (
                c
                for c in cases
                if (not agent or c.agent == agent)
                and (not skill_id or c.skill_id == skill_id)
            ),
            None,
        )
        if case is None:
            case = PromptEvalCase(
                case_id="ad-hoc",
                agent=agent,
                skill_id=skill_id,
                task_type=task_type,
                model_hint=model_hint,
                seed_global=True,
            )
    else:
        case = PromptEvalCase(
            case_id="ad-hoc",
            agent=agent,
            skill_id=skill_id,
            task_type=task_type,
            model_hint=model_hint,
            seed_global=True,
        )
    try:
        baseline, candidate = compose_baseline_and_candidate(repo_root, case)
    except PromptEvalCompareError as exc:
        raise PromptEvalServiceError(str(exc)) from exc
    return {
        "status": "compared",
        "case_id": case.case_id,
        "baseline": {
            "prompt_bundle_hash": baseline.get("prompt_bundle_hash"),
            "instruction_ids": baseline.get("instruction_ids"),
            "instruction_count": len(baseline.get("instructions") or []),
        },
        "candidate": {
            "prompt_bundle_hash": candidate.get("prompt_bundle_hash"),
            "instruction_ids": candidate.get("instruction_ids"),
            "instruction_count": len(candidate.get("instructions") or []),
        },
        "hashes_differ": baseline.get("prompt_bundle_hash")
        != candidate.get("prompt_bundle_hash"),
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def export_report_csv(
    repo_root: Path,
    dest: Path,
    *,
    report_id: str = "",
) -> Path:
    require_prompt_eval_enabled()
    try:
        if report_id:
            report = load_report(repo_root, report_id)
        else:
            reports = list_reports(repo_root)
            if not reports:
                raise PromptEvalServiceError(
                    f"no prompt-eval reports under {prompt_eval_root(repo_root)}"
                )
            report = reports[-1]
    except PromptEvalReportError as exc:
        raise PromptEvalServiceError(str(exc)) from exc

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "report_id",
        "case_id",
        "non_regression",
        "baseline_hash",
        "candidate_hash",
        "failures",
    ]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for case in report.get("cases") or []:
            writer.writerow(
                {
                    "report_id": report.get("report_id", ""),
                    "case_id": case.get("case_id", ""),
                    "non_regression": case.get("non_regression", ""),
                    "baseline_hash": case.get("baseline_hash", ""),
                    "candidate_hash": case.get("candidate_hash", ""),
                    "failures": "; ".join(case.get("failures") or []),
                }
            )
    return dest
