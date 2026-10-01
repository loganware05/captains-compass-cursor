"""Canonical behavior-evaluation signal identifiers and glossary (M46)."""

from __future__ import annotations

# Distinct signals — weak_verification / weak_test_coverage / unverified_claim
# are NOT aliases (Captain decision 2026-10-01).
BEHAVIOR_SIGNALS: tuple[str, ...] = (
    "wrong_answer",
    "ignored_instruction",
    "format_violation",
    "hedging",
    "repeated_request",
    "praise",
    "unnecessary_scope",
    "hallucinated_repository_state",
    "unverified_claim",
    "tool_misuse",
    "boundary_violation",
    "weak_test_coverage",
    "test_workaround",
    "unsafe_git_operation",
    "excessive_context",
    "unnecessary_abstraction",
    "missing_evidence",
    "rework_required",
    "weak_verification",
)

SIGNAL_DEFINITIONS: dict[str, str] = {
    "wrong_answer": "Response or change contradicts the stated objective or accepted plan.",
    "ignored_instruction": "Explicit instruction or constraint from plan/Captain was skipped.",
    "format_violation": "Output violated required schema, file layout, or formatting contract.",
    "hedging": "Excessive uncertainty language that obscured a required decision.",
    "repeated_request": "Same Captain correction or request had to be repeated.",
    "praise": "Positive signal — behavior worth preserving (success exemplar).",
    "unnecessary_scope": "Changes expanded beyond the approved plan without justification.",
    "hallucinated_repository_state": "Claimed files/APIs/paths that do not match repository reality.",
    "unverified_claim": "Asserted correctness without citing tests, evidence, or review.",
    "tool_misuse": "Used tools incorrectly or unsafely relative to the task.",
    "boundary_violation": "Crossed authority, approval, or module boundary without gate.",
    "weak_test_coverage": "Insufficient or shallow tests for the claimed change.",
    "test_workaround": "Weakened, skipped, or gamed tests to force green.",
    "unsafe_git_operation": "Risky git operation (force-push, protected branch, secret commit).",
    "excessive_context": "Loaded or transmitted far more context than needed.",
    "unnecessary_abstraction": "Introduced abstraction without proportionate benefit.",
    "missing_evidence": "Validation evidence required by Definition of Done was omitted.",
    "rework_required": "Follow-up repair was needed due to quality or correctness gaps.",
    "weak_verification": "Verification steps were incomplete relative to risk of the change.",
}

SCHEMA_VERSION = "1"
QUESTION_REVISION_BEHAVIOR_EVAL = "behavior_eval_v1"


def empty_signals() -> dict[str, float]:
    return {name: 0.0 for name in BEHAVIOR_SIGNALS}


def clamp_signal(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def normalize_signals(raw: dict | None) -> dict[str, float]:
    out = empty_signals()
    if not isinstance(raw, dict):
        return out
    for key, value in raw.items():
        name = str(key)
        if name not in out:
            continue
        try:
            out[name] = clamp_signal(float(value))
        except (TypeError, ValueError):
            continue
    return out
