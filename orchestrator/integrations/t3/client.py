"""HTTPS JSON client for live T3 thread ops (allowlisted; injectable transport)."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import quote

from orchestrator.integrations.t3.enabled import require_t3_exec_live_enabled
from orchestrator.integrations.transport import HttpTransport, UrllibTransport

# NorthStar-owned HTTPS allowlist (maps to T3 MCP tools: orchestrator_capabilities,
# t3_thread_launch, t3_thread_read, t3_thread_interrupt). A bridge/proxy implements
# these routes; CI uses RecordingTransport — never hit the network in unit tests.
DEFAULT_API_ENV = "COMPASS_T3_API_BASE"
DEFAULT_TOKEN_ENV = "COMPASS_T3_AUTH_TOKEN"

ALLOWED_OPS = frozenset({"capabilities", "start", "status", "collect", "cancel"})


class T3ClientError(ValueError):
    """Raised when live T3 HTTP calls fail."""


def _api_base(api_base: str | None = None) -> str:
    base = (api_base or os.environ.get(DEFAULT_API_ENV) or "").strip().rstrip("/")
    if not base:
        raise T3ClientError(f"live T3 requires {DEFAULT_API_ENV} (https://...)")
    if not base.startswith("https://"):
        raise T3ClientError(f"{DEFAULT_API_ENV} must be https://")
    return base


def _auth_token() -> str:
    token = (os.environ.get(DEFAULT_TOKEN_ENV) or "").strip()
    if not token:
        raise T3ClientError(f"live T3 requires {DEFAULT_TOKEN_ENV}")
    return token


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _decode_json(body: bytes) -> Any:
    try:
        return json.loads(body.decode("utf-8") or "null")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise T3ClientError("invalid T3 JSON response") from exc


def _require_object(payload: Any, *, what: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise T3ClientError(f"{what} response must be an object")
    return payload


class T3LiveClient:
    """Allowlisted HTTPS client for T3 live execution ops."""

    def __init__(
        self,
        *,
        transport: HttpTransport | None = None,
        api_base: str | None = None,
        token: str | None = None,
    ) -> None:
        require_t3_exec_live_enabled()
        self._base = _api_base(api_base)
        self._token = token if token is not None else _auth_token()
        self._http = transport or UrllibTransport()

    def capabilities(self) -> dict[str, Any]:
        url = f"{self._base}/v1/capabilities"
        resp = self._http.request("GET", url, headers=_headers(self._token), timeout=30.0)
        if resp.status >= 400:
            raise T3ClientError(f"t3 capabilities failed: HTTP {resp.status}")
        return _require_object(_decode_json(resp.body), what="capabilities")

    def start_thread(
        self,
        *,
        title: str,
        message: str,
        client_request_id: str,
        provider: str = "",
        model: str = "",
    ) -> dict[str, Any]:
        url = f"{self._base}/v1/threads"
        payload: dict[str, Any] = {
            "title": title,
            "message": message,
            "clientRequestId": client_request_id,
            "tool": "t3_thread_launch",
        }
        if provider:
            payload["provider"] = provider
        if model:
            payload["model"] = model
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        resp = self._http.request(
            "POST", url, headers=_headers(self._token), body=body, timeout=60.0
        )
        if resp.status >= 400:
            raise T3ClientError(f"t3 start failed: HTTP {resp.status}")
        return _require_object(_decode_json(resp.body), what="start")

    def read_thread(self, thread_id: str, *, view: str = "messages") -> dict[str, Any]:
        tid = quote(str(thread_id), safe="")
        url = f"{self._base}/v1/threads/{tid}?view={quote(view, safe='')}"
        resp = self._http.request("GET", url, headers=_headers(self._token), timeout=30.0)
        if resp.status >= 400:
            raise T3ClientError(f"t3 status/collect failed: HTTP {resp.status}")
        return _require_object(_decode_json(resp.body), what="thread read")

    def interrupt_thread(self, thread_id: str, *, reason: str = "cancel") -> dict[str, Any]:
        tid = quote(str(thread_id), safe="")
        url = f"{self._base}/v1/threads/{tid}/interrupt"
        body = json.dumps(
            {"reason": reason, "tool": "t3_thread_interrupt", "stop": True},
            separators=(",", ":"),
        ).encode("utf-8")
        resp = self._http.request(
            "POST", url, headers=_headers(self._token), body=body, timeout=30.0
        )
        if resp.status >= 400:
            raise T3ClientError(f"t3 cancel failed: HTTP {resp.status}")
        return _require_object(_decode_json(resp.body), what="interrupt")
