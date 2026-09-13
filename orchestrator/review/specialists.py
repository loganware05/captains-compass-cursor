"""Hermetic specialist candidate emitters for NorthStar Code Reviewer (M28).

Security, adversarial, and testing specialists produce deterministic candidate
JSON that feeds the existing verify → report gate. No model calls.
"""

from __future__ import annotations

import re
from typing import Any

_SECRET_ASSIGN = re.compile(
    r"(?i)(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}",
)
_HARDCODED_AWS = re.compile(r"AKIA[0-9A-Z]{16}")
_BROAD_EXCEPT = re.compile(r"except\s+(Exception|BaseException|:\s*)", re.I)
_ASSERT_TRUE = re.compile(r"assert\s+True\b")
_EMPTY_TEST = re.compile(r"^\s*pass\s*$", re.M)
_HTTP_CLIENT = re.compile(r"(httpx|requests|aiohttp|urllib)", re.I)
_AUTH_PATH = re.compile(r"(auth|session|token|secret|permission|credential)", re.I)
_DEPLOY_PATH = re.compile(
    r"(Dockerfile|docker-compose|\.github/workflows/|deploy|helm|terraform)",
    re.I,
)
_TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec)/|\.(test|spec)\.", re.I)


def _diff_and_paths(
    detection: dict[str, Any],
    context_pack: dict[str, Any],
) -> tuple[str, list[str]]:
    diff = str(context_pack.get("diff") or "")
    changed = list(detection.get("changed_paths") or [])
    return diff, changed


def emit_security_candidates(
    *,
    detection: dict[str, Any],
    context_pack: dict[str, Any],
) -> list[dict[str, Any]]:
    """Security-review specialist — secrets, authz gaps, fail-open catches."""
    diff, changed = _diff_and_paths(detection, context_pack)
    out: list[dict[str, Any]] = []
    auth_paths = [p for p in changed if _AUTH_PATH.search(p)]
    test_changed = any(_TEST_PATH.search(p) for p in changed)

    if _SECRET_ASSIGN.search(diff) or _HARDCODED_AWS.search(diff):
        out.append(
            {
                "id": "sec-secret-in-diff",
                "title": "Possible secret material in diff",
                "detail": (
                    "Security specialist: diff matches credential-assignment or "
                    "cloud key patterns. Confirm secrets are not committed."
                ),
                "severity": "high",
                "confidence": 0.92,
                "skill": "security-review",
                "category": "secrets",
                "evidence_paths": changed[:3] or ["(diff)"],
                "suggested_fix": (
                    "Remove secrets; rotate if exposed; use env/secret manager."
                ),
            }
        )

    if auth_paths and not test_changed:
        out.append(
            {
                "id": "sec-auth-without-tests",
                "title": "Auth/credential paths changed without tests",
                "detail": (
                    "Security specialist: authentication/credential-related paths "
                    "changed with no accompanying test paths."
                ),
                "severity": "medium",
                "confidence": 0.82,
                "skill": "security-review",
                "category": "testing",
                "evidence_paths": auth_paths[:5],
                "suggested_fix": (
                    "Add tests for authn/authz failure paths and missing credentials."
                ),
            }
        )

    if auth_paths and _BROAD_EXCEPT.search(diff):
        out.append(
            {
                "id": "sec-broad-except-near-auth",
                "title": "Broad exception handler near auth/credential code",
                "detail": (
                    "Security specialist: broad `except Exception` (or similar) "
                    "appears alongside auth/credential changes — risk of fail-open."
                ),
                "severity": "high",
                "confidence": 0.8,
                "skill": "security-review",
                "category": "fail-open",
                "evidence_paths": auth_paths[:3] or changed[:3],
                "suggested_fix": (
                    "Catch specific exceptions; fail closed on auth/config errors."
                ),
            }
        )

    return out


def emit_adversarial_candidates(
    *,
    detection: dict[str, Any],
    context_pack: dict[str, Any],
) -> list[dict[str, Any]]:
    """Adversarial-reviewer specialist — scope drift, weak tests, missing rollback."""
    diff, changed = _diff_and_paths(detection, context_pack)
    intent = detection.get("intent") or {}
    out: list[dict[str, Any]] = []

    non_goals = [str(x).casefold() for x in (intent.get("non_goals") or [])]
    joined = " ".join(changed).casefold()
    for idx, ng in enumerate(non_goals):
        tokens = [t for t in re.split(r"[^a-z0-9]+", ng) if len(t) >= 5]
        hits = [t for t in tokens if t in joined]
        if hits:
            out.append(
                {
                    "id": f"adv-nongoal-{idx}",
                    "title": "Possible non-goal / deferred scope touch",
                    "detail": (
                        "Adversarial specialist: changed paths overlap tokens from "
                        f"plan non-goal {ng!r} (tokens={hits[:5]})."
                    ),
                    "severity": "medium",
                    "confidence": 0.66,
                    "skill": "adversarial-reviewer",
                    "category": "scope-drift",
                    "evidence_paths": changed[:5]
                    or [str(intent.get("plan_path") or "IMPLEMENTATION_PLAN.md")],
                    "suggested_fix": "Confirm change stays inside approved MVP scope.",
                }
            )

    test_paths = [p for p in changed if _TEST_PATH.search(p)]
    if _ASSERT_TRUE.search(diff) or (test_paths and _EMPTY_TEST.search(diff)):
        out.append(
            {
                "id": "adv-weak-test",
                "title": "Test may pass for the wrong reason",
                "detail": (
                    "Adversarial specialist: diff introduces `assert True` or an "
                    "empty test body — weak signal that tests prove little."
                ),
                "severity": "medium",
                "confidence": 0.78,
                "skill": "adversarial-reviewer",
                "category": "testing",
                "evidence_paths": test_paths or changed[:3] or ["(diff)"],
                "suggested_fix": (
                    "Replace tautological asserts with behavior assertions."
                ),
            }
        )

    deploy_touched = [p for p in changed if _DEPLOY_PATH.search(p)]
    if deploy_touched:
        plan_text = str(intent.get("excerpt") or "").casefold()
        if "rollback" not in plan_text and "roll back" not in plan_text:
            out.append(
                {
                    "id": "adv-missing-rollback",
                    "title": "Deploy-related change without rollback mention in plan",
                    "detail": (
                        "Adversarial specialist: deploy/workflow paths changed but "
                        "intent excerpt does not mention rollback."
                    ),
                    "severity": "medium",
                    "confidence": 0.7,
                    "skill": "adversarial-reviewer",
                    "category": "rollback",
                    "evidence_paths": deploy_touched[:5],
                    "suggested_fix": (
                        "Document rollback steps in IMPLEMENTATION_PLAN before merge."
                    ),
                }
            )

    if _BROAD_EXCEPT.search(diff):
        out.append(
            {
                "id": "adv-broad-except",
                "title": "Over-broad exception handling",
                "detail": (
                    "Adversarial specialist: broad exception catch can hide defects "
                    "and mask failures in live clients."
                ),
                "severity": "medium",
                "confidence": 0.72,
                "skill": "adversarial-reviewer",
                "category": "error-handling",
                "evidence_paths": changed[:5] or ["(diff)"],
                "suggested_fix": (
                    "Narrow exception types; log and fail closed on unexpected errors."
                ),
            }
        )

    return out


def emit_testing_candidates(
    *,
    detection: dict[str, Any],
    context_pack: dict[str, Any],
) -> list[dict[str, Any]]:
    """Testing-validation specialist — coverage gaps for production/client changes."""
    diff, changed = _diff_and_paths(detection, context_pack)
    out: list[dict[str, Any]] = []
    prod_paths = [
        p
        for p in changed
        if not _TEST_PATH.search(p) and not p.casefold().endswith((".md", ".txt", ".rst"))
    ]
    test_changed = any(_TEST_PATH.search(p) for p in changed)

    if prod_paths and not test_changed:
        out.append(
            {
                "id": "test-missing-for-prod-change",
                "title": "Production paths changed without test updates",
                "detail": (
                    "Testing specialist: non-doc production paths changed with no "
                    "test path in the change set."
                ),
                "severity": "medium",
                "confidence": 0.8,
                "skill": "testing-validation",
                "category": "coverage",
                "evidence_paths": prod_paths[:5],
                "suggested_fix": (
                    "Add or update unit/integration tests for the changed behavior."
                ),
            }
        )

    py_prod = [p for p in prod_paths if p.casefold().endswith(".py")]
    if py_prod and _HTTP_CLIENT.search(diff) and not test_changed:
        out.append(
            {
                "id": "test-http-client-no-failure-path",
                "title": "HTTP client changes lack failure-path tests",
                "detail": (
                    "Testing specialist: diff touches HTTP client usage "
                    "(httpx/requests/aiohttp) without test updates for timeouts, "
                    "4xx/5xx, or auth failures."
                ),
                "severity": "medium",
                "confidence": 0.76,
                "skill": "testing-validation",
                "category": "resilience",
                "evidence_paths": py_prod[:5],
                "suggested_fix": (
                    "Add tests for network/auth failure paths and timeouts."
                ),
            }
        )

    return out


SPECIALIST_EMITTERS = (
    ("security-review", emit_security_candidates),
    ("adversarial-reviewer", emit_adversarial_candidates),
    ("testing-validation", emit_testing_candidates),
)


def compose_specialist_candidates(
    *,
    detection: dict[str, Any],
    context_pack: dict[str, Any],
    include_heuristics: bool = False,
) -> tuple[list[dict[str, Any]], list[str], str]:
    """Run specialist emitters; optionally merge legacy heuristics.

    Returns (candidates, skills_invoked, candidates_source).
    """
    from orchestrator.review.candidates import generate_heuristic_candidates

    candidates: list[dict[str, Any]] = []
    skills: list[str] = []
    seen_ids: set[str] = set()

    for skill, emitter in SPECIALIST_EMITTERS:
        batch = emitter(detection=detection, context_pack=context_pack)
        if batch:
            skills.append(skill)
        for item in batch:
            cid = str(item.get("id") or "")
            if cid and cid in seen_ids:
                continue
            if cid:
                seen_ids.add(cid)
            candidates.append(item)

    source = "specialists"
    if include_heuristics:
        for item in generate_heuristic_candidates(
            detection=detection,
            context_pack=context_pack,
        ):
            cid = str(item.get("id") or "")
            if cid and cid in seen_ids:
                continue
            if cid:
                seen_ids.add(cid)
            candidates.append(item)
        source = "specialists+heuristics"

    # Always include one discardable low-signal finding so verify filter is exercised
    # when specialists alone yield an empty set.
    noise_id = "noise-style-nit"
    if noise_id not in seen_ids:
        candidates.append(
            {
                "id": noise_id,
                "title": "Style nit without evidence",
                "detail": "Placeholder low-signal nit used to exercise discard rules.",
                "severity": "low",
                "confidence": 0.2,
                "skill": "code-reviewer",
                "category": "noise",
                "evidence_paths": [],
                "suggested_fix": "",
            }
        )

    return candidates, skills, source
