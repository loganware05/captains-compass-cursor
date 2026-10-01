"""Baseline vs candidate prompt-bundle comparison (M49)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.behavior.instructions.composer import compose_prompt_bundle
from orchestrator.behavior.instructions.store import (
    InstructionStoreError,
    build_instruction,
    seed_global_operating_brief,
    write_instruction,
)
from orchestrator.behavior.prompt_eval.cases import (
    PromptEvalCase,
    PromptEvalCaseError,
    default_cases_path,
    load_cases,
)
from orchestrator.behavior.prompt_eval.report import (
    PromptEvalReportError,
    report_id_for_payload,
    write_report,
)
from orchestrator.behavior.prompt_eval.score import score_case


class PromptEvalCompareError(ValueError):
    """Raised when prompt-eval comparison cannot proceed."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_version(repo_root: Path) -> str:
    path = Path(repo_root) / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _seed_case_registry(repo_root: Path, case: PromptEvalCase) -> None:
    if case.seed_global:
        seed_global_operating_brief(repo_root)
    for item in case.global_instructions:
        instruction = build_instruction(
            title=str(item.get("title") or f"global-{case.case_id}"),
            body=str(item.get("body") or ""),
            scope="global",
            approval_state=str(item.get("approval_state") or "draft"),
            instruction_id=item.get("instruction_id"),
        )
        write_instruction(repo_root, instruction)
    for item in case.proposal_instructions:
        instruction = build_instruction(
            title=str(item.get("title") or f"proposal-{case.case_id}"),
            body=str(item.get("body") or ""),
            scope="proposal",
            agent=str(item.get("agent") or case.agent),
            skill_id=str(item.get("skill_id") or case.skill_id),
            task_type=str(item.get("task_type") or case.task_type),
            model_hint=str(item.get("model_hint") or case.model_hint),
            approval_state=str(item.get("approval_state") or "draft"),
            instruction_id=item.get("instruction_id"),
        )
        write_instruction(repo_root, instruction)


def compose_baseline_and_candidate(
    repo_root: Path,
    case: PromptEvalCase,
    *,
    persist_bundles: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compose baseline (no proposals) and candidate (with proposals)."""
    _seed_case_registry(repo_root, case)
    try:
        baseline = compose_prompt_bundle(
            repo_root,
            agent=case.agent,
            skill_id=case.skill_id,
            task_type=case.task_type,
            model_hint=case.model_hint,
            persist=persist_bundles,
            include_proposals=False,
            seed_if_empty=case.seed_global,
        )
        candidate = compose_prompt_bundle(
            repo_root,
            agent=case.agent,
            skill_id=case.skill_id,
            task_type=case.task_type,
            model_hint=case.model_hint,
            persist=persist_bundles,
            include_proposals=True,
            seed_if_empty=case.seed_global,
        )
    except InstructionStoreError as exc:
        raise PromptEvalCompareError(str(exc)) from exc
    return baseline, candidate


def evaluate_case(repo_root: Path, case: PromptEvalCase) -> dict[str, Any]:
    baseline, candidate = compose_baseline_and_candidate(repo_root, case)
    scored = score_case(case, baseline, candidate)
    observed = scored["non_regression"]
    # Negative fixtures expect the scorer to fail; suite pass when expectation matches.
    expectation_met = observed == case.expect_non_regression
    return {
        "case_id": case.case_id,
        "non_regression": "pass" if expectation_met else "fail",
        "observed_non_regression": observed,
        "expect_non_regression": case.expect_non_regression,
        "baseline_hash": str(baseline.get("prompt_bundle_hash") or ""),
        "candidate_hash": str(candidate.get("prompt_bundle_hash") or ""),
        "baseline_instruction_ids": list(baseline.get("instruction_ids") or []),
        "candidate_instruction_ids": list(candidate.get("instruction_ids") or []),
        "metrics": scored["metrics"],
        "failures": list(scored["failures"])
        + (
            []
            if expectation_met
            else [
                f"expected observed_non_regression={case.expect_non_regression}, "
                f"got {observed}"
            ]
        ),
    }


def run_prompt_eval(
    repo_root: Path,
    *,
    cases_path: Path | None = None,
    control_root: Path | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    """Run hermetic baseline-vs-candidate prompt evaluation for all cases."""
    control = Path(control_root or repo_root)
    path = Path(cases_path) if cases_path else default_cases_path(control)
    try:
        cases = load_cases(path)
    except PromptEvalCaseError as exc:
        raise PromptEvalCompareError(str(exc)) from exc

    case_results: list[dict[str, Any]] = []
    for case in cases:
        case_results.append(evaluate_case(repo_root, case))

    passed = sum(1 for c in case_results if c["non_regression"] == "pass")
    failed = len(case_results) - passed
    report: dict[str, Any] = {
        "schema_version": "1",
        "created_at": _utc_now(),
        "non_regression": "pass" if failed == 0 else "fail",
        "case_count": len(case_results),
        "passed_count": passed,
        "failed_count": failed,
        "cases": case_results,
        "baseline_mode": "include_proposals=false",
        "candidate_mode": "include_proposals=true",
        "cases_path": str(path),
        "northstar_version": _read_version(control),
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    report["report_id"] = report_id_for_payload(report)
    if persist:
        try:
            report = write_report(repo_root, report)
        except PromptEvalReportError as exc:
            raise PromptEvalCompareError(str(exc)) from exc
    return report
