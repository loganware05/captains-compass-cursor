"""Factory and shared helpers for fixture/live NorthStar adapters."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from orchestrator.integrations.adapters.cursor import CursorAdapter
from orchestrator.integrations.adapters.github import GitHubAdapter
from orchestrator.integrations.adapters.linear import LinearAdapter
from orchestrator.integrations.adapters.slack import SlackAdapter
from orchestrator.integrations.product_allowlist import (
    DEFAULT_PRODUCT_REPOSITORY,
    require_allowed_repository,
)
from orchestrator.integrations.transport import HttpTransport, UrllibTransport


def _env_token(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def github_api(
    transport: HttpTransport,
    *,
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
    api_base: str = "https://api.github.com",
) -> Any:
    if not token:
        raise RuntimeError("BLOCKED_CONNECTION: NORTHSTAR_GITHUB_TOKEN missing")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "NorthStar-M22",
    }
    raw = None if body is None else json.dumps(body).encode("utf-8")
    resp = transport.request(method, f"{api_base}{path}", headers=headers, body=raw)
    if resp.status >= 400:
        raise RuntimeError(f"BLOCKED_CONNECTION: GitHub API {resp.status}")
    if not resp.body:
        return {}
    return json.loads(resp.body.decode("utf-8"))


def linear_graphql(
    transport: HttpTransport,
    *,
    query: str,
    variables: dict[str, Any] | None = None,
    api_key: str,
    api_url: str = "https://api.linear.app/graphql",
) -> Any:
    if not api_key:
        raise RuntimeError("BLOCKED_CONNECTION: NORTHSTAR_LINEAR_API_KEY missing")
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    payload = {"query": query, "variables": variables or {}}
    resp = transport.request(
        "POST",
        api_url,
        headers=headers,
        body=json.dumps(payload).encode("utf-8"),
    )
    if resp.status >= 400:
        raise RuntimeError(f"BLOCKED_CONNECTION: Linear API {resp.status}")
    return json.loads(resp.body.decode("utf-8"))


def slack_api(
    transport: HttpTransport,
    *,
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
    api_base: str = "https://slack.com/api",
) -> Any:
    if not token:
        raise RuntimeError("BLOCKED_CONNECTION: NORTHSTAR_SLACK_BOT_TOKEN missing")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    raw = None if body is None else json.dumps(body).encode("utf-8")
    resp = transport.request(method, f"{api_base}{path}", headers=headers, body=raw)
    if resp.status >= 400:
        raise RuntimeError(f"BLOCKED_CONNECTION: Slack API {resp.status}")
    data = json.loads(resp.body.decode("utf-8")) if resp.body else {}
    if isinstance(data, dict) and data.get("ok") is False:
        raise RuntimeError(f"BLOCKED_CONNECTION: Slack API error {data.get('error')!r}")
    return data


def build_northstar_adapters(
    *,
    mode: str,
    store_dir: Path,
    connected: dict[str, bool],
    transport: HttpTransport | None = None,
    product_repository: str = DEFAULT_PRODUCT_REPOSITORY,
) -> dict[str, Any]:
    """Construct the four NorthStar adapters for fixtures or live mode."""
    mode_n = (mode or "fixtures").strip().lower()
    if mode_n in {"fixture", "fixtures"}:
        mode_n = "fixtures"
    elif mode_n != "live":
        raise ValueError(f"unknown NorthStar mode: {mode!r}")

    # Factory always validates the product repository (sandbox-only).
    require_allowed_repository(product_repository)

    if mode_n == "live" and transport is None:
        transport = UrllibTransport()

    common_kw: dict[str, Any] = {
        "mode": mode_n,
        "transport": transport,
        "product_repository": product_repository,
    }

    github = GitHubAdapter(
        store_dir=store_dir / "github",
        connected=connected.get("github", True),
        **common_kw,
    )
    linear = LinearAdapter(
        store_dir=store_dir / "linear",
        connected=connected.get("linear", True),
        **common_kw,
    )
    slack = SlackAdapter(
        store_dir=store_dir / "slack",
        connected=connected.get("slack", True),
        **common_kw,
    )
    cursor = CursorAdapter(
        store_dir=store_dir / "cursor",
        connected=connected.get("cursor", True),
        **common_kw,
    )
    return {
        "github": github,
        "linear": linear,
        "slack": slack,
        "cursor": cursor,
        "mode": mode_n,
        "product_repository": product_repository,
        "transport": transport,
        "github_token": _env_token("NORTHSTAR_GITHUB_TOKEN"),
        "linear_api_key": _env_token("NORTHSTAR_LINEAR_API_KEY"),
        "slack_bot_token": _env_token("NORTHSTAR_SLACK_BOT_TOKEN"),
    }
