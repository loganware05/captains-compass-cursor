"""Hermetic labeled evaluation for DecisionProvider shadow skill suggestion (M41 WS4)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orchestrator.providers.decision.file_provider import FileDecisionProvider
from orchestrator.providers.decision.types import (
    EligibleSkillSummary,
    SkillSuggestionRequest,
)

DEFAULT_CASES_PATH = (
    Path(__file__).resolve().parent / "eval_data" / "eval-cases-v1.json"
)


@dataclass
class EvalCase:
    case_id: str
    objective: str
    gold_skill_id: str | None  # None => uncovered (no skill should be suggested)
    eligible: list[EligibleSkillSummary]
    matcher_top: list[str]


def load_cases(path: Path | None = None) -> list[EvalCase]:
    target = path or DEFAULT_CASES_PATH
    with target.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    cases: list[EvalCase] = []
    for item in raw.get("cases") or []:
        eligible = [
            EligibleSkillSummary(
                skill_id=str(s["skill_id"]),
                name=str(s.get("name") or s["skill_id"]),
                description=str(s.get("description") or ""),
                lifecycle_stage=str(s.get("lifecycle_stage") or ""),
                categories=tuple(s.get("categories") or ()),
            )
            for s in item.get("eligible") or []
        ]
        cases.append(
            EvalCase(
                case_id=str(item["case_id"]),
                objective=str(item["objective"]),
                gold_skill_id=item.get("gold_skill_id"),
                eligible=eligible,
                matcher_top=list(item.get("matcher_top") or []),
            )
        )
    return cases


def _provider_top(request: SkillSuggestionRequest, provider: FileDecisionProvider) -> list[str]:
    result = provider.suggest_skills(request)
    if result.abstain or not result.suggested_skill_id:
        return []
    rest = [r.skill_id for r in result.ranked if r.skill_id != result.suggested_skill_id]
    return [result.suggested_skill_id, *rest]


def evaluate_file_provider(cases: list[EvalCase] | None = None) -> dict[str, Any]:
    """Compare file DecisionProvider vs gold labels + matcher baseline (hermetic)."""
    cases = cases if cases is not None else load_cases()
    provider = FileDecisionProvider()
    covered = [c for c in cases if c.gold_skill_id]
    uncovered = [c for c in cases if not c.gold_skill_id]

    wrong = 0
    missed = 0
    for case in covered:
        request = SkillSuggestionRequest(
            objective=case.objective,
            eligible_skills=case.eligible,
            roster_hash=case.case_id,
        )
        top = _provider_top(request, provider)
        if not top:
            missed += 1
        elif top[0] != case.gold_skill_id:
            wrong += 1

    unnecessary = 0
    for case in uncovered:
        request = SkillSuggestionRequest(
            objective=case.objective,
            eligible_skills=case.eligible,
            roster_hash=case.case_id,
        )
        top = _provider_top(request, provider)
        if top:
            unnecessary += 1

    disagreement = 0
    for case in cases:
        request = SkillSuggestionRequest(
            objective=case.objective,
            eligible_skills=case.eligible,
            roster_hash=case.case_id,
        )
        provider_ids = _provider_top(request, provider)
        matcher_ids = list(case.matcher_top)
        width = max(len(provider_ids), len(matcher_ids), 1)
        for idx in range(width):
            left = matcher_ids[idx] if idx < len(matcher_ids) else None
            right = provider_ids[idx] if idx < len(provider_ids) else None
            if left != right:
                disagreement += 1
                break

    covered_n = max(len(covered), 1)
    uncovered_n = max(len(uncovered), 1)
    report = {
        "schema": "northstar.decision_eval.v1",
        "provider": "file",
        "model_id": "jev-1.13.0",
        "case_count": len(cases),
        "covered_count": len(covered),
        "uncovered_count": len(uncovered),
        "metrics": {
            "wrong_skill_loads": wrong / covered_n if covered else 0.0,
            "wrong_skill_loads_count": wrong,
            "missed_useful_skills": missed / covered_n if covered else 0.0,
            "missed_useful_skills_count": missed,
            "unnecessary_skill_loads": unnecessary / uncovered_n if uncovered else 0.0,
            "unnecessary_skill_loads_count": unnecessary,
            "disagreement_rate": disagreement / max(len(cases), 1),
            "disagreement_count": disagreement,
            "latency_ms": 0,
            "cost_usd": 0,
        },
        "applied": False,
    }
    return report


def write_eval_report(repo_root: Path, report: dict[str, Any] | None = None) -> Path:
    repo_root = Path(repo_root)
    report = report if report is not None else evaluate_file_provider()
    out_dir = repo_root / ".agent" / "evidence" / "m41-jev-decision-service" / "eval"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "file-provider-eval-v1.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
