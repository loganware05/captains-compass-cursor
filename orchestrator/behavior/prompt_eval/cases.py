"""Load hermetic prompt-eval fixture cases (M49)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_CASES_REL = Path("tests/fixtures/behavior/prompt-eval/cases.json")

METRIC_NAMES = (
    "instruction_adherence",
    "schema_validity",
    "hallucinated_repository_state",
    "unnecessary_scope",
    "verified_review_precision",
    "evidence_completeness",
    "approval_boundary_compliance",
)


@dataclass
class PromptEvalCase:
    case_id: str
    agent: str = ""
    skill_id: str = ""
    task_type: str = ""
    model_hint: str = ""
    seed_global: bool = True
    proposal_instructions: list[dict[str, Any]] = field(default_factory=list)
    global_instructions: list[dict[str, Any]] = field(default_factory=list)
    must_pass: list[str] = field(default_factory=list)
    expectations: dict[str, Any] = field(default_factory=dict)
    # "pass" = case must non-regress; "fail" = negative fixture (scorer must catch)
    expect_non_regression: str = "pass"


class PromptEvalCaseError(ValueError):
    """Raised when fixture cases are missing or malformed."""


def default_cases_path(control_root: Path) -> Path:
    return Path(control_root) / DEFAULT_CASES_REL


def load_cases(path: Path) -> list[PromptEvalCase]:
    target = Path(path)
    if not target.is_file():
        raise PromptEvalCaseError(f"cases file not found: {target}")
    try:
        with target.open(encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PromptEvalCaseError(f"invalid cases file: {target}: {exc}") from exc
    if not isinstance(raw, dict):
        raise PromptEvalCaseError("cases root must be an object")
    items = raw.get("cases")
    if not isinstance(items, list) or not items:
        raise PromptEvalCaseError("cases must be a non-empty array")
    out: list[PromptEvalCase] = []
    for item in items:
        if not isinstance(item, dict):
            raise PromptEvalCaseError("each case must be an object")
        case_id = str(item.get("case_id") or "").strip()
        if not case_id:
            raise PromptEvalCaseError("case_id required")
        expectations = dict(item.get("expectations") or {})
        must_pass = [str(x) for x in (item.get("must_pass") or expectations.get("must_pass") or [])]
        if not must_pass:
            must_pass = list(METRIC_NAMES)
        expect = str(item.get("expect_non_regression") or "pass").strip().lower()
        if expect not in {"pass", "fail"}:
            raise PromptEvalCaseError(
                f"expect_non_regression must be pass|fail, got {expect!r}"
            )
        out.append(
            PromptEvalCase(
                case_id=case_id,
                agent=str(item.get("agent") or ""),
                skill_id=str(item.get("skill_id") or ""),
                task_type=str(item.get("task_type") or ""),
                model_hint=str(item.get("model_hint") or ""),
                seed_global=bool(item.get("seed_global", True)),
                proposal_instructions=list(item.get("proposal_instructions") or []),
                global_instructions=list(item.get("global_instructions") or []),
                must_pass=must_pass,
                expectations=expectations,
                expect_non_regression=expect,
            )
        )
    return out
