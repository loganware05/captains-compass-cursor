"""Injectable HTTP transport for NorthStar live adapters (stdlib only)."""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from orchestrator.integrations.events import redact_secrets


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes


@runtime_checkable
class HttpTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float = 30.0,
    ) -> HttpResponse:
        ...


def _normalize_headers(headers: dict[str, str] | None) -> dict[str, str]:
    return {str(k).lower(): str(v) for k, v in (headers or {}).items()}


class UrllibTransport:
    """Production HTTP transport. Never construct in CI unit tests."""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float = 30.0,
    ) -> HttpResponse:
        req = urllib.request.Request(
            url,
            data=body,
            headers=headers or {},
            method=method.upper(),
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw_headers = {str(k).lower(): str(v) for k, v in resp.headers.items()}
                return HttpResponse(status=int(resp.status), headers=raw_headers, body=resp.read())
        except urllib.error.HTTPError as exc:
            raw_headers = {str(k).lower(): str(v) for k, v in (exc.headers or {}).items()}
            return HttpResponse(status=int(exc.code), headers=raw_headers, body=exc.read() or b"")


class RecordingTransport:
    """CI double: map (method, url_prefix) → HttpResponse; record calls; no network."""

    def __init__(
        self,
        responses: dict[tuple[str, str], HttpResponse] | None = None,
        *,
        default: HttpResponse | None = None,
    ) -> None:
        self._responses = dict(responses or {})
        self._default = default or HttpResponse(status=200, headers={}, body=b"{}")
        self.calls: list[dict[str, Any]] = []

    def add_response(self, method: str, url_prefix: str, response: HttpResponse) -> None:
        self._responses[(method.upper(), url_prefix)] = response

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
        timeout: float = 30.0,
    ) -> HttpResponse:
        method_u = method.upper()
        headers_norm = _normalize_headers(headers)
        self.calls.append(
            {
                "method": method_u,
                "url": url,
                "headers": redact_secrets(headers_norm),
                "body": body,
                "timeout": timeout,
            }
        )
        matched: HttpResponse | None = None
        # Longest prefix wins for overlapping stubs.
        best = -1
        for (m, prefix), resp in self._responses.items():
            if m == method_u and url.startswith(prefix) and len(prefix) > best:
                matched = resp
                best = len(prefix)
        return matched if matched is not None else self._default
