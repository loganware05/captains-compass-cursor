"""Heuristic + fixture candidate generation for hermetic code review."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_SECRET_ASSIGN = re.compile(
    r"(?i)(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}",
)
_HARDCODED_AWS = re.compile(r"AKIA[0-9A-Z]{16}")


def load_candidates_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("findings"), list):
        return [f for f in data["findings"] if isinstance(f, dict)]
    if isinstance(data, list):
        return [f for f in data if isinstance(f, dict)]
    raise ValueError(f"candidates file must be a list or {{findings: []}}: {path}")


def generate_heuristic_candidates(
    *,
    detection: dict[str, Any],
    context_pack: dict[str, Any],
) -> list[dict[str, Any]]:
    """Produce deterministic candidate findings without model calls."""
    candidates: list[dict[str, Any]] = []
    diff = str(context_pack.get("diff") or "")
    changed = list(detection.get("changed_paths") or [])
    intent = detection.get("intent") or {}

    if _SECRET_ASSIGN.search(diff) or _HARDCODED_AWS.search(diff):
        evidence = changed[:3] or ["(diff)"]
        candidates.append(
            {
                "id": "sec-secret-in-diff",
                "title": "Possible secret material in diff",
                "detail": (
                    "Diff matches credential-assignment or cloud key patterns. "
                    "Confirm secrets are not committed."
                ),
                "severity": "high",
                "confidence": 0.9,
                "skill": "security-review",
                "category": "secrets",
                "evidence_paths": evidence,
                "suggested_fix": "Remove secrets; rotate if exposed; use env/secret manager.",
            }
        )

    non_goals = [str(x).casefold() for x in (intent.get("non_goals") or [])]
    joined_paths = " ".join(changed).casefold()
    for idx, ng in enumerate(non_goals):
        # crude keyword overlap: if a non-goal mentions github review posting etc.
        tokens = [t for t in re.split(r"[^a-z0-9]+", ng) if len(t) >= 5]
        hits = [t for t in tokens if t in joined_paths]
        if hits:
            candidates.append(
                {
                    "id": f"scope-nongoal-{idx}",
                    "title": "Possible non-goal / deferred scope touch",
                    "detail": (
                        f"Changed paths overlap tokens from plan non-goal: {ng!r} "
                        f"(tokens={hits[:5]})."
                    ),
                    "severity": "medium",
                    "confidence": 0.62,
                    "skill": "code-reviewer",
                    "category": "scope-drift",
                    "evidence_paths": changed[:5] or [str(intent.get("plan_path") or "IMPLEMENTATION_PLAN.md")],
                    "suggested_fix": "Confirm change stays inside approved MVP scope.",
                }
            )

    ac = list(intent.get("acceptance_criteria") or [])
    if ac and changed:
        # Emit a low-confidence reminder finding that intent should be checked.
        candidates.append(
            {
                "id": "intent-ac-presence",
                "title": "Intent artifact present — verify acceptance criteria coverage",
                "detail": (
                    f"Loaded {len(ac)} acceptance-criteria bullet(s) from plan. "
                    "Confirm the diff advances them and does not contradict non-goals."
                ),
                "severity": "info",
                "confidence": 0.7,
                "skill": "code-reviewer",
                "category": "intent",
                "evidence_paths": [str(intent.get("plan_path") or "IMPLEMENTATION_PLAN.md")]
                + changed[:3],
                "suggested_fix": "Map each AC to evidence or tests before merge.",
            }
        )

    domains = set(detection.get("domains") or [])
    if "security" in domains and not any(p for p in changed if "test" in p.casefold()):
        candidates.append(
            {
                "id": "sec-missing-tests",
                "title": "Security-sensitive paths changed without obvious tests",
                "detail": "Security-related paths detected; no test path in the change set.",
                "severity": "medium",
                "confidence": 0.8,
                "skill": "security-review",
                "category": "testing",
                "evidence_paths": [p for p in changed if re.search(r"auth|session|token|secret|permission", p, re.I)]
                or changed[:3],
                "suggested_fix": "Add or update tests covering authz/authn failure paths.",
            }
        )

    # Always include one discardable low-signal finding so verify filter is exercised
    # when callers rely solely on heuristics.
    candidates.append(
        {
            "id": "noise-style-nit",
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
    return candidates
