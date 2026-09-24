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
_HOOK_PATH = re.compile(
    r"(^|/)\.cursor/hooks(/|$)|(^|/)\.cursor/hooks\.json$|(^|/)hooks\.json$",
    re.I,
)
# Executable hook control plane only — docs under .cursor/hooks/ (README) must
# not feed fail-closed detectors (M42 / M40 sandbox FP).
_HOOK_SCAN_PATH = re.compile(
    r"(^|/)\.cursor/hooks/[^/]+\.(sh|bash|zsh)$|"
    r"(^|/)\.cursor/hooks\.json$|"
    r"(^|/)hooks\.json$",
    re.I,
)
_PLAN_EXEMPT = re.compile(
    r"^\+.*\bIMPLEMENTATION_PLAN\.md\b",
    re.M,
)
_PLAN_ALLOW_CASE = re.compile(
    r"^\+.*\bIMPLEMENTATION_PLAN\.md\b.*allow|"
    r"^\+.*case\s+[\"'].*IMPLEMENTATION_PLAN\.md",
    re.M | re.I,
)
_BRANCH_PREFIX = r"(?:feature|fix|chore|docs|agent|hotfix|cursor)"
_CHECKOUT_SHORTCIRCUIT = re.compile(
    # Literal shell (`checkout -b feature/` / `switch -c cursor/`) OR grep-pattern
    # source (`checkout[[:space:]]+(-b|--branch)[[:space:]]+(feature|…)`).
    r"(?:checkout(?:\s+|\[\[:space:\]\]\+)+"
    r"(?:-b|--branch|\(-b\|--branch\))"
    r"|switch(?:\s+|\[\[:space:\]\]\+)+"
    r"(?:-c|--create|\(-c\|--create\)))"
    r".{0,120}" + _BRANCH_PREFIX,
    re.I,
)
_ALLOW_NEAR_CHECKOUT = re.compile(
    r"(?:checkout|switch)(?:\s+|\[\[:space:\]\]\+)+"
    r"(?:-b|--branch|-c|--create|\(-b\|--branch\)|\(-c\|--create\)).{0,240}\ballow\b|"
    r"\ballow\b.{0,120}(?:checkout|switch)(?:\s+|\[\[:space:\]\]\+)+"
    r"(?:-b|--branch|-c|--create|\(-b\|--branch\)|\(-c\|--create\))",
    re.I | re.S,
)
# Command-argv -C parsing (not merely `git -C` for local rev-parse).
_CMD_C_PARSE = re.compile(
    r"""tokens\[[^\]]+\]\s*==\s*['\"]-C['\"]"""
    r"""|\bt\s*==\s*['\"]-C['\"]"""
    r"""|startswith\(\s*['\"]-C['\"]"""
    r"""|tok\s*==\s*['\"]-C['\"]""",
)
_REFSPEC_HINT = re.compile(
    r"refspec|HEAD:\w+|refs/heads/"
    r"""|split\(\s*['\"]:['\"]\s*\)"""
    r"""|partition\(\s*['\"]:['\"]\s*\)"""
    r"""|['\"]:['\"]\s*in\s+\w+"""
    r"""|is_protected_ref""",
    re.I,
)
_PUSH_VERB = re.compile(
    r"""verb\s*==\s*['\"]push['\"]"""
    r"""|git\s+push\b"""
    r"""|git\[\[:space:\]\]\+\(commit\|push\|merge\|rebase\)"""
    r"""|[\"']push[\"']\s*in\s*\{"""
    r"""|\(commit\|push\|merge\|rebase\)""",
    re.I,
)
_PLAN_APPROVAL_HOOK = re.compile(r"plan-approval-check", re.I)
_PROTECTED_BRANCH_HOOK = re.compile(r"protected-branch", re.I)


def _diff_and_paths(
    detection: dict[str, Any],
    context_pack: dict[str, Any],
) -> tuple[str, list[str]]:
    diff = str(context_pack.get("diff") or "")
    changed = list(detection.get("changed_paths") or [])
    return diff, changed


def _hook_control_plane_touched(changed: list[str], diff: str) -> bool:
    if any(_HOOK_PATH.search(p) for p in changed):
        return True
    # Diff-only path headers when changed_paths omitted
    return bool(
        re.search(
            r"^diff --git a/.*\.cursor/hooks/|"
            r"^diff --git a/.*hooks\.json|"
            r"^\+\+\+ b/.*\.cursor/hooks/",
            diff,
            re.M,
        )
    )


def _paths_and_headers(changed: list[str], diff: str) -> list[str]:
    paths = [p for p in changed if _HOOK_PATH.search(p)]
    for match in re.finditer(
        r"^diff --git a/(\S+) b/(\S+)",
        diff,
        re.M,
    ):
        paths.append(match.group(2))
    # Preserve order, unique
    seen: set[str] = set()
    out: list[str] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _added_text(diff: str) -> str:
    lines: list[str] = []
    for line in diff.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        body = line[1:]
        # Drop shell / python comments so advisory notes do not fake mitigations
        if body.lstrip().startswith("#"):
            continue
        if "  #" in body:
            body = body.split("  #", 1)[0]
        lines.append(body)
    return "\n".join(lines)


def _added_text_by_file(diff: str) -> dict[str, str]:
    """Map each diff path to its added-line body (comments stripped).

    Removed lines (``-``) and file headers are ignored — detectors must not
    fire on deletions or on unrelated docs that merely describe a pattern.
    """
    current: str | None = None
    buckets: dict[str, list[str]] = {}
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            match = re.match(r"^diff --git a/(\S+) b/(\S+)", line)
            current = match.group(2) if match else None
            if current is not None:
                buckets.setdefault(current, [])
            continue
        if current is None:
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if not line.startswith("+"):
            continue
        body = line[1:]
        if body.lstrip().startswith("#"):
            continue
        if "  #" in body:
            body = body.split("  #", 1)[0]
        buckets[current].append(body)
    return {path: "\n".join(rows) for path, rows in buckets.items()}


def _hook_added_text(diff: str, changed: list[str]) -> str:
    """Added text from executable hook scripts / hooks.json only.

    Excludes docs under ``.cursor/hooks/`` (e.g. README) so descriptive text
    about removed short-circuits cannot false-positive detectors.
    """
    by_file = _added_text_by_file(diff)
    hook_paths = {
        p for p in list(by_file) + list(changed) if _HOOK_SCAN_PATH.search(p)
    }
    chunks = [by_file[p] for p in sorted(hook_paths) if by_file.get(p)]
    return "\n".join(chunks)


def _strip_string_literals(text: str) -> str:
    """Remove quoted strings so deny-message text cannot fake mitigations."""
    text = re.sub(r"\"(?:\\.|[^\"\\])*\"", '""', text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", "''", text)
    return text


def _strip_message_contexts(text: str) -> str:
    """Drop deny/print/user_message payloads so they cannot fake mitigations.

    Unlike full string-literal stripping, this keeps executable quoted tokens
    such as ``t == "-C"`` and ``os.environ.get("COMPASS_CAPTAIN_APPROVE")``.
    Shell ``echo | grep`` control-flow lines are preserved (not message-only).
    """
    patterns = (
        r"\bprint\s*\((?:[^()]|\([^()]*\))*\)",
        r"\bdeny\s*\((?:[^()]|\([^()]*\))*\)",
        r"(?:user_message|agent_message|agentMessage|userMessage)\s*=\s*"
        r"(?:\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')",
        # echo '{"permission":"deny",...}' / deny JSON payloads
        r"""\becho\s+['\"]\{[^'\"]*permission[^'\"]*\}['\"]""",
        r"""\becho\s+['\"][^'\"]*COMPASS_CAPTAIN_APPROVE[^'\"]*['\"]""",
        r"""\becho\s+['\"][^'\"]*refspec[^'\"]*['\"]""",
        r"""\becho\s+['\"][^'\"]*HEAD:IMPLEMENTATION_PLAN\.md[^'\"]*['\"]""",
    )
    out = text
    for pat in patterns:
        out = re.sub(pat, " ", out, flags=re.I | re.S)
    return out


_CAPTAIN_GATE = re.compile(
    r"os\.environ\.get\(\s*[\"']COMPASS_CAPTAIN_APPROVE[\"']"
    r"|\$\{?COMPASS_CAPTAIN_APPROVE\b"
    r"|\[\[?\s*[\"']?\$\{?COMPASS_CAPTAIN_APPROVE",
    re.I,
)
_COMMITTED_PLAN = re.compile(
    r"[\"']git[\"']\s*,\s*[\"']show[\"']\s*,\s*[\"']HEAD:IMPLEMENTATION_PLAN\.md[\"']"
    r"|subprocess\.run\(\s*\[[^\]]*HEAD:IMPLEMENTATION_PLAN\.md"
    r"|git\s+show\s+HEAD:IMPLEMENTATION_PLAN\.md",
    re.I,
)


def _emit_fail_closed_hook_candidates(
    *,
    diff: str,
    changed: list[str],
) -> list[dict[str, Any]]:
    """Agentic-equivalent hermetic checks for fail-closed hook control gaps (M37).

    Encodes the two medium classes from Cursor Agentic Security Review on
    bitcoin-data-collector PR #7: self-serve plan-approval and protected-branch
    bypasses (refspecs / git -C / checkout substring short-circuit).
    """
    if not _hook_control_plane_touched(changed, diff):
        return []

    # Scope pattern matching to hook-file added lines only. Whole-diff
    # ``_added_text`` includes docs/markdown that mention legacy patterns and
    # caused M40 sandbox FPs when short-circuits were *removed*.
    added = _hook_added_text(diff, changed)
    # Mitigation presence must ignore echo/deny/print message text (fail-open
    # otherwise). Do not full-strip string literals — that erases real gates.
    logic = _strip_message_contexts(added)
    out: list[dict[str, Any]] = []
    hook_paths = _paths_and_headers(changed, diff) or [".cursor/hooks/"]
    joined_paths = " ".join(hook_paths)
    is_plan_hook = bool(_PLAN_APPROVAL_HOOK.search(joined_paths))
    is_protected_hook = bool(_PROTECTED_BRANCH_HOOK.search(joined_paths))
    if not is_plan_hook and not is_protected_hook:
        headers = " ".join(
            m.group(0)
            for m in re.finditer(r"^diff --git .+$", diff, re.M)
        )
        is_plan_hook = bool(_PLAN_APPROVAL_HOOK.search(headers))
        is_protected_hook = bool(_PROTECTED_BRANCH_HOOK.search(headers))

    # Behavioral fallback for renamed hooks (filename gate alone is fail-open).
    plan_signals = bool(_PLAN_EXEMPT.search(diff) or _PLAN_ALLOW_CASE.search(diff))
    # Protected-class body signal: guards main/master (not merely any commit/push hook).
    guards_protected_base = bool(
        re.search(
            r"""\b(main|master|develop|release|production)\b.{0,80}\bdeny\b"""
            r"""|\bdeny\b.{0,80}\b(main|master|develop|release|production)\b"""
            r"""|is_protected_ref|PROTECTED\s*=""",
            added,
            re.I | re.S,
        )
    )
    protected_signals = bool(
        (_CHECKOUT_SHORTCIRCUIT.search(added) and guards_protected_base)
        or (_PUSH_VERB.search(added) and guards_protected_base)
    )
    if not is_plan_hook and plan_signals:
        is_plan_hook = True
    if not is_protected_hook and protected_signals:
        is_protected_hook = True

    # Class 1 — plan-approval self-serve
    if is_plan_hook and plan_signals:
        has_captain = bool(_CAPTAIN_GATE.search(logic))
        has_committed = bool(_COMMITTED_PLAN.search(logic))
        missing_captain = not has_captain
        missing_committed = not has_committed

        if missing_captain or missing_committed:
            gaps = []
            if missing_captain:
                gaps.append("no COMPASS_CAPTAIN_APPROVE gate on plan Status promotion")
            if missing_committed:
                gaps.append("no committed HEAD:IMPLEMENTATION_PLAN.md check")
            out.append(
                {
                    "id": "sec-hook-plan-self-serve",
                    "title": "Fail-closed plan-approval hook may be self-servable",
                    "detail": (
                        "Security specialist (agentic-equivalent): hook diff exempts "
                        "IMPLEMENTATION_PLAN.md from Write/StrReplace while product "
                        "edits trust plan Status — "
                        + "; ".join(gaps)
                        + ". An agent can forge APPROVED in the exempt file."
                    ),
                    "severity": "medium",
                    "confidence": 0.88 if _PLAN_APPROVAL_HOOK.search(joined_paths) else 0.8,
                    "skill": "security-review",
                    "category": "fail-closed-control",
                    "evidence_paths": [
                        p for p in hook_paths if _PLAN_APPROVAL_HOOK.search(p)
                    ][:5]
                    or hook_paths[:5],
                    "suggested_fix": (
                        "Require COMPASS_CAPTAIN_APPROVE=1 to write APPROVED status; "
                        "gate product edits on committed plan Status + real Approval "
                        "Record (see M36 / ADR-053)."
                    ),
                }
            )

    if not is_protected_hook:
        return out

    # Class 2a — checkout/switch substring short-circuit
    has_checkout_sc = bool(_CHECKOUT_SHORTCIRCUIT.search(added))
    checkout_allows = bool(
        _ALLOW_NEAR_CHECKOUT.search(added)
        or re.search(
            r"(?:checkout|switch).{0,160}\b(?:allow|compass_allow)\s*(\(|\{)?",
            added,
            re.I | re.S,
        )
        or (
            re.search(r"checkout|switch", added, re.I)
            and re.search(r"^\s*(?:allow|compass_allow)\b", added, re.M)
            and _CHECKOUT_SHORTCIRCUIT.search(added)
        )
    )
    if has_checkout_sc and checkout_allows:
        out.append(
            {
                "id": "sec-hook-checkout-shortcircuit",
                "title": "Protected-branch hook short-circuits on checkout -b substring",
                "detail": (
                    "Security specialist (agentic-equivalent): fail-closed protected-"
                    "branch hook allows when the command string contains "
                    "`git checkout -b` / `git switch -c` with a feature-like prefix, "
                    "which does not prove HEAD left a protected branch before "
                    "commit/push."
                ),
                "severity": "medium",
                "confidence": 0.9,
                "skill": "security-review",
                "category": "fail-closed-control",
                "evidence_paths": [p for p in hook_paths if _PROTECTED_BRANCH_HOOK.search(p)][:5]
                or hook_paths[:5],
                "suggested_fix": (
                    "Remove checkout/switch substring short-circuit; decide allow/deny "
                    "from resolved repo HEAD and push refspecs only."
                ),
            }
        )

    # Class 2b — push path without refspec awareness (ignore message fakes)
    handles_push = bool(_PUSH_VERB.search(added))
    if handles_push and not _REFSPEC_HINT.search(logic):
        out.append(
            {
                "id": "sec-hook-push-refspec-gap",
                "title": "Protected-branch hook ignores push refspecs",
                "detail": (
                    "Security specialist (agentic-equivalent): hook mentions git push "
                    "but added code lacks refspec / HEAD:branch / refs/heads parsing — "
                    "`git push origin HEAD:main` can mutate protected branches while "
                    "feature HEAD looks safe."
                ),
                "severity": "medium",
                "confidence": 0.86,
                "skill": "security-review",
                "category": "fail-closed-control",
                "evidence_paths": [p for p in hook_paths if _PROTECTED_BRANCH_HOOK.search(p)][:5]
                or hook_paths[:5],
                "suggested_fix": (
                    "Parse push refspecs and deny destinations that resolve to "
                    "main/master/develop/release/production."
                ),
            }
        )

    # Class 2c — missing command-argv git -C parsing (not local `git -C` rev-parse)
    handles_mutation = bool(_PUSH_VERB.search(added) or _CHECKOUT_SHORTCIRCUIT.search(added))
    if handles_mutation and not _CMD_C_PARSE.search(logic):
        out.append(
            {
                "id": "sec-hook-git-c-gap",
                "title": "Protected-branch hook may miss git -C target repo",
                "detail": (
                    "Security specialist (agentic-equivalent): mutation hook does not "
                    "parse `git -C <path>` from the command argv, so "
                    "`cd other && git -C <protected-repo> commit` can bypass cwd/"
                    "cd-prefix checks (local `git -C` for rev-parse alone is not enough)."
                ),
                "severity": "medium",
                "confidence": 0.84,
                "skill": "security-review",
                "category": "fail-closed-control",
                "evidence_paths": [p for p in hook_paths if _PROTECTED_BRANCH_HOOK.search(p)][:5]
                or hook_paths[:5],
                "suggested_fix": (
                    "Resolve repo from command-token `-C` (and cd prefix / hook cwd); "
                    "check that repo's HEAD / refspecs."
                ),
            }
        )

    return out


def emit_security_candidates(
    *,
    detection: dict[str, Any],
    context_pack: dict[str, Any],
) -> list[dict[str, Any]]:
    """Security-review specialist — secrets, authz gaps, fail-open / fail-closed."""
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

    out.extend(_emit_fail_closed_hook_candidates(diff=diff, changed=changed))
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
