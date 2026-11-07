"""Normalize Sentry issue payloads into evidence packets."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from orchestrator.integrations.events import redact_secrets, utc_now

_SEVERITY_MAP = {
    "fatal": "fatal",
    "error": "error",
    "warning": "warning",
    "info": "info",
    "debug": "debug",
}


def _excerpt(text: str, limit: int = 2000) -> str:
    compact = redact_secrets(str(text or ""))
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _severity(raw: Any) -> str:
    level = str(raw or "unknown").strip().lower()
    return _SEVERITY_MAP.get(level, "unknown")


def _fingerprint(issue: dict[str, Any]) -> str:
    fp = issue.get("fingerprint")
    if isinstance(fp, list) and fp:
        return "|".join(str(x) for x in fp)
    if isinstance(fp, str) and fp.strip():
        return fp.strip()
    issue_id = str(issue.get("id") or issue.get("shortId") or "unknown")
    title = str(issue.get("title") or "")
    return hashlib.sha256(f"{issue_id}:{title}".encode("utf-8")).hexdigest()[:24]


def _packet_id(org: str, project: str, issue_id: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", f"{org}-{project}-{issue_id}".lower()).strip("-")
    return f"sentry-{slug[:100]}"


def normalize_issue(
    issue: dict[str, Any],
    *,
    org: str,
    project: str,
    mode: str,
) -> dict[str, Any]:
    """Map a Sentry issue (API or fixture) to a schema packet."""
    issue_id = str(issue.get("id") or issue.get("shortId") or "").strip()
    if not issue_id:
        raise ValueError("sentry issue missing id")
    title = str(issue.get("title") or issue.get("metadata", {}).get("type") or "untitled")
    count_raw = issue.get("count")
    try:
        count = int(count_raw) if count_raw is not None else 0
    except (TypeError, ValueError):
        count = 0
    metadata = issue.get("metadata") if isinstance(issue.get("metadata"), dict) else {}
    stack = (
        issue.get("stack_excerpt")
        or metadata.get("value")
        or issue.get("culprit")
        or ""
    )
    release = issue.get("release") or (issue.get("firstRelease") or {}).get("version")
    if isinstance(release, dict):
        release = release.get("version")
    commit = issue.get("commit_sha") or issue.get("commit")
    permalink = issue.get("permalink") or issue.get("url")
    env = issue.get("environment")
    if isinstance(env, list):
        env = env[0] if env else None

    packet_id = _packet_id(org, project, issue_id)
    fingerprint = _fingerprint(issue)
    refs = [
        {"kind": "sentry_issue", "ref": issue_id},
        {"kind": "fixture" if mode == "fixture" else "sentry_issue", "ref": packet_id},
    ]
    if release:
        refs.append({"kind": "release", "ref": str(release)})
    if commit:
        refs.append({"kind": "git", "ref": str(commit)})

    hint = (
        f"Investigate Sentry issue {issue_id} ({title}) as external evidence only. "
        "Do not auto-repair or write back to Sentry."
    )
    return {
        "schema_version": "1",
        "packet_id": packet_id,
        "provider": "sentry",
        "mode": mode,
        "org": org,
        "project": project,
        "environment": str(env) if env else None,
        "issue_id": issue_id,
        "title": _excerpt(title, 240),
        "culprit": _excerpt(str(issue.get("culprit") or ""), 240),
        "fingerprint": fingerprint,
        "severity": _severity(issue.get("level") or metadata.get("level")),
        "occurrence_count": max(0, count),
        "first_seen": str(issue.get("firstSeen") or issue.get("first_seen") or "unknown"),
        "last_seen": str(issue.get("lastSeen") or issue.get("last_seen") or "unknown"),
        "release": str(release) if release else None,
        "commit_sha": str(commit) if commit else None,
        "permalink": str(permalink) if permalink else None,
        "stack_excerpt": _excerpt(str(stack)),
        "source_refs": refs,
        "claim_kind": "external",
        "investigation_hint": hint,
        "retrieved_at": utc_now(),
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "write_to_sentry": False,
    }
