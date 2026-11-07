"""Fixture and optional live Sentry issue readers (read-only)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote

from orchestrator.integrations.sentry.enabled import require_sentry_live_enabled
from orchestrator.integrations.transport import HttpTransport, UrllibTransport

DEFAULT_API = "https://sentry.io/api/0"
DEFAULT_FIXTURE = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "fixtures"
    / "sentry"
    / "sample-issues.json"
)


class SentryClientError(ValueError):
    """Raised when Sentry fetch fails."""


def load_fixture_issues(path: Path | None = None) -> list[dict[str, Any]]:
    fixture = Path(path) if path else DEFAULT_FIXTURE
    if not fixture.is_file():
        raise SentryClientError(f"sentry fixture not found: {fixture}")
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SentryClientError(str(exc)) from exc
    if isinstance(payload, dict) and isinstance(payload.get("issues"), list):
        issues = payload["issues"]
        org = str(payload.get("org") or "fixture-org")
        project = str(payload.get("project") or "fixture-project")
        return [
            {**issue, "_org": org, "_project": project}
            for issue in issues
            if isinstance(issue, dict)
        ]
    if isinstance(payload, list):
        return [i for i in payload if isinstance(i, dict)]
    raise SentryClientError("sentry fixture must be a list or {issues:[...]}")


def _auth_token() -> str:
    token = (
        os.environ.get("COMPASS_SENTRY_AUTH_TOKEN")
        or os.environ.get("SENTRY_AUTH_TOKEN")
        or ""
    ).strip()
    if not token:
        raise SentryClientError(
            "live sentry requires COMPASS_SENTRY_AUTH_TOKEN or SENTRY_AUTH_TOKEN"
        )
    return token


def fetch_live_issues(
    *,
    org: str,
    project: str,
    issue_id: str | None = None,
    window_hours: int = 24,
    transport: HttpTransport | None = None,
    api_base: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch issues via Sentry HTTP API (read-only). https only."""
    require_sentry_live_enabled()
    base = (api_base or os.environ.get("COMPASS_SENTRY_API_BASE") or DEFAULT_API).rstrip("/")
    if not base.startswith("https://"):
        raise SentryClientError("COMPASS_SENTRY_API_BASE must be https://")
    token = _auth_token()
    http = transport or UrllibTransport()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if issue_id:
        url = f"{base}/issues/{quote(str(issue_id), safe='')}/"
        resp = http.request("GET", url, headers=headers, timeout=30.0)
        if resp.status >= 400:
            raise SentryClientError(f"sentry issue fetch failed: HTTP {resp.status}")
        try:
            issue = json.loads(resp.body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise SentryClientError("invalid sentry issue JSON") from exc
        if not isinstance(issue, dict):
            raise SentryClientError("sentry issue response must be an object")
        issue["_org"] = org
        issue["_project"] = project
        return [issue]

    # Project issues list (bounded query window is advisory metadata for callers).
    _ = window_hours
    url = (
        f"{base}/projects/{quote(org, safe='')}/"
        f"{quote(project, safe='')}/issues/?query=is:unresolved&limit=25"
    )
    resp = http.request("GET", url, headers=headers, timeout=30.0)
    if resp.status >= 400:
        raise SentryClientError(f"sentry issues list failed: HTTP {resp.status}")
    try:
        issues = json.loads(resp.body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise SentryClientError("invalid sentry issues JSON") from exc
    if not isinstance(issues, list):
        raise SentryClientError("sentry issues response must be a list")
    out: list[dict[str, Any]] = []
    for issue in issues:
        if isinstance(issue, dict):
            issue = dict(issue)
            issue["_org"] = org
            issue["_project"] = project
            out.append(issue)
    return out
