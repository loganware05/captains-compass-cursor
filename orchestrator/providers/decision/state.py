"""Compact eligible-skill state construction with redaction invariants."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable

from orchestrator.providers.decision.types import EligibleSkillSummary

# Patterns that must never appear in provider-bound state.
_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|authorization)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[a-z0-9\-._~+/]+=*"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
)

_MAX_DESCRIPTION_CHARS = 280
_MAX_EVIDENCE_CHARS = 120
_FORBIDDEN_STATE_KEYS = frozenset(
    {
        "diff",
        "diffs",
        "patch",
        "raw_diff",
        "env",
        "secrets",
        "credentials",
        "repo_tree",
        "full_memory",
        "decisions_md",
        "project_context",
    }
)


def redact_text(text: str) -> str:
    cleaned = text or ""
    for pattern in _SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    return cleaned


def truncate(text: str, limit: int) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def assert_state_safe(payload: dict[str, Any]) -> None:
    """Fail closed if compact state includes forbidden keys or secret-shaped text."""

    def _walk(node: Any, *, path: str) -> None:
        if isinstance(node, dict):
            forbidden = _FORBIDDEN_STATE_KEYS & set(node.keys())
            if forbidden:
                raise ValueError(
                    f"decision state contains forbidden keys at {path or '$'}: "
                    f"{sorted(forbidden)}"
                )
            for key, value in node.items():
                _walk(value, path=f"{path}.{key}" if path else str(key))
        elif isinstance(node, list):
            for idx, value in enumerate(node):
                _walk(value, path=f"{path}[{idx}]")

    _walk(payload, path="")
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    for pattern in _SECRET_PATTERNS:
        if pattern.search(blob):
            raise ValueError("decision state failed secret redaction invariant")


def summarize_skill(skill: dict[str, Any]) -> EligibleSkillSummary:
    """Build a compact summary from a registry skill document."""
    skill_id = str(skill.get("id") or skill.get("skill_id") or "").strip()
    name = str(skill.get("name") or skill_id).strip()
    description = redact_text(
        str(
            skill.get("description")
            or skill.get("summary")
            or skill.get("notes")
            or ""
        )
    )
    categories = skill.get("categories") or []
    if not isinstance(categories, list):
        categories = []
    evidence = redact_text(str(skill.get("evidence_notes") or skill.get("notes") or ""))
    return EligibleSkillSummary(
        skill_id=skill_id,
        name=truncate(redact_text(name), 120),
        description=truncate(description, _MAX_DESCRIPTION_CHARS),
        lifecycle_stage=str(skill.get("lifecycle_stage") or ""),
        maturity=str(skill.get("maturity") or ""),
        categories=tuple(str(c) for c in categories),
        evidence_notes=truncate(evidence, _MAX_EVIDENCE_CHARS),
    )


def roster_content_hash(skills: Iterable[EligibleSkillSummary]) -> str:
    payload = [s.to_dict() for s in skills]
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_compact_state(
    objective: str,
    skills: Iterable[dict[str, Any]] | Iterable[EligibleSkillSummary],
) -> tuple[str, list[EligibleSkillSummary], str, dict[str, Any]]:
    """Return (objective, summaries, roster_hash, state_dict) for provider calls."""
    summaries: list[EligibleSkillSummary] = []
    for item in skills:
        if isinstance(item, EligibleSkillSummary):
            summaries.append(item)
        elif isinstance(item, dict):
            summaries.append(summarize_skill(item))
    summaries = [s for s in summaries if s.skill_id]
    summaries.sort(key=lambda s: s.skill_id)
    objective_clean = truncate(redact_text(objective), 2000)
    roster_hash = roster_content_hash(summaries)
    state = {
        "objective": objective_clean,
        "eligible_skills": [s.to_dict() for s in summaries],
        "roster_hash": roster_hash,
    }
    assert_state_safe(state)
    return objective_clean, summaries, roster_hash, state
