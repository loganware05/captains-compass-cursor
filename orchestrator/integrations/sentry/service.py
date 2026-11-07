"""Operator service for northstar sentry fetch|show|list."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from orchestrator.integrations.sentry.client import (
    SentryClientError,
    fetch_live_issues,
    load_fixture_issues,
)
from orchestrator.integrations.sentry.enabled import (
    require_sentry_ingest_enabled,
    sentry_live_enabled,
)
from orchestrator.integrations.sentry.normalize import normalize_issue
from orchestrator.integrations.sentry.store import (
    SentryStoreError,
    list_packets as store_list,
    load_packet,
    write_packet,
)
from orchestrator.integrations.transport import HttpTransport


class SentryServiceError(ValueError):
    """Operator-facing Sentry ingest errors."""


def fetch_incidents(
    repo_root: Path,
    *,
    org: str | None = None,
    project: str | None = None,
    issue_id: str | None = None,
    window_hours: int = 24,
    fixture_path: Path | None = None,
    force_live: bool = False,
    transport: HttpTransport | None = None,
) -> dict[str, Any]:
    """Fetch/normalize Sentry issues into evidence packets (read-only)."""
    require_sentry_ingest_enabled()
    repo_root = Path(repo_root)
    use_live = force_live or sentry_live_enabled()
    if use_live and fixture_path is None:
        org_n = (org or os.environ.get("COMPASS_SENTRY_ORG") or "").strip()
        project_n = (project or os.environ.get("COMPASS_SENTRY_PROJECT") or "").strip()
        if not org_n or not project_n:
            raise SentryServiceError(
                "live sentry requires --org/--project or "
                "COMPASS_SENTRY_ORG / COMPASS_SENTRY_PROJECT"
            )
        try:
            issues = fetch_live_issues(
                org=org_n,
                project=project_n,
                issue_id=issue_id,
                window_hours=window_hours,
                transport=transport,
            )
        except SentryClientError as exc:
            raise SentryServiceError(str(exc)) from exc
        mode = "live"
    else:
        try:
            issues = load_fixture_issues(fixture_path)
        except SentryClientError as exc:
            raise SentryServiceError(str(exc)) from exc
        mode = "fixture"
        if issue_id:
            issues = [
                i
                for i in issues
                if str(i.get("id") or i.get("shortId") or "") == str(issue_id)
            ]
            if not issues:
                raise SentryServiceError(f"fixture issue not found: {issue_id}")

    written: list[dict[str, Any]] = []
    for issue in issues:
        org_i = str(org or issue.get("_org") or "fixture-org")
        project_i = str(project or issue.get("_project") or "fixture-project")
        try:
            packet = normalize_issue(issue, org=org_i, project=project_i, mode=mode)
            write_packet(repo_root, packet)
        except (ValueError, SentryStoreError) as exc:
            raise SentryServiceError(str(exc)) from exc
        written.append(packet)

    return {
        "status": "fetched",
        "mode": mode,
        "count": len(written),
        "packet_ids": [p["packet_id"] for p in written],
        "packets": written,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "write_to_sentry": False,
    }


def show_packet(repo_root: Path, packet_id: str) -> dict[str, Any]:
    require_sentry_ingest_enabled()
    try:
        return load_packet(repo_root, packet_id)
    except SentryStoreError as exc:
        raise SentryServiceError(str(exc)) from exc


def list_packets(repo_root: Path) -> dict[str, Any]:
    require_sentry_ingest_enabled()
    docs = store_list(repo_root)
    return {
        "count": len(docs),
        "packets": [
            {
                "packet_id": d["packet_id"],
                "issue_id": d["issue_id"],
                "title": d["title"],
                "severity": d["severity"],
                "mode": d["mode"],
                "retrieved_at": d["retrieved_at"],
            }
            for d in docs
        ],
        "approved_for_execution": False,
        "authority_mutation": False,
        "write_to_sentry": False,
    }
