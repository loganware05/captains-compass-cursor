"""Compact change-state builder for DecisionProvider review triage (M44)."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Sequence

from orchestrator.providers.decision.state import assert_state_safe, redact_text
from orchestrator.providers.decision.types import ReviewChangeSummary

_MAX_PATHS = 40
_AUTH = re.compile(r"(auth|session|token|secret|permission|credential|oauth)", re.I)
_SENSITIVE = re.compile(
    r"(secret|password|private[_-]?key|encrypt|pii|gdpr|network|http|"
    r"Dockerfile|docker-compose|\.github/workflows/|deploy|helm|terraform|"
    r"package(-lock)?\.json|requirements.*\.txt|pyproject\.toml|go\.mod|"
    r"\.cursor/hooks|hooks\.json)",
    re.I,
)
_HOOK = re.compile(
    r"(^|/)\.cursor/hooks(/|$)|(^|/)\.cursor/hooks\.json$|(^|/)hooks\.json$",
    re.I,
)
_DEP = re.compile(
    r"(package(-lock)?\.json|requirements.*\.txt|pyproject\.toml|go\.mod|Cargo\.toml|"
    r"Gemfile|composer\.json|pnpm-lock|yarn\.lock)",
    re.I,
)
_NETWORK = re.compile(r"(httpx|requests|aiohttp|fetch\(|axios|urllib|websocket)", re.I)


def _flag_paths(paths: Sequence[str]) -> dict[str, bool]:
    joined = "\n".join(paths)
    return {
        "touches_authz": bool(_AUTH.search(joined)),
        "touches_sensitive": bool(_SENSITIVE.search(joined)),
        "touches_hooks": bool(_HOOK.search(joined)),
        "touches_deps": bool(_DEP.search(joined)),
        "touches_network_hint": bool(_NETWORK.search(joined)),
    }


def build_review_change_summary(
    *,
    changed_paths: Sequence[str] | None = None,
    domains: Sequence[str] | None = None,
    specialist_skill_ids: Sequence[str] | None = None,
    candidate_count: int = 0,
    objective: str = "",
) -> tuple[ReviewChangeSummary, str, dict[str, Any]]:
    """Return (summary, change_hash, state_dict) safe for DecisionProvider."""
    paths = [redact_text(str(p))[:240] for p in (changed_paths or []) if str(p).strip()]
    paths = paths[:_MAX_PATHS]
    domain_list = [redact_text(str(d))[:80] for d in (domains or []) if str(d).strip()]
    specialists = [
        redact_text(str(s))[:120] for s in (specialist_skill_ids or []) if str(s).strip()
    ]
    objective_clean = redact_text(objective or "")[:500]
    flags = _flag_paths(paths)
    summary = ReviewChangeSummary(
        changed_paths=tuple(paths),
        domains=tuple(domain_list),
        path_flags=flags,
        specialist_skill_ids=tuple(specialists),
        candidate_count=int(candidate_count),
        objective=objective_clean,
    )
    state = {
        "change": summary.to_dict(),
    }
    assert_state_safe(state)
    digest = hashlib.sha256(
        json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return summary, digest, state
