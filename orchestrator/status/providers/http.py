"""Opt-in OpenRouter-compatible HTTP StatusProvider (M52). Never used in CI."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable

from orchestrator.providers.decision.state import redact_text

DEFAULT_HTTP_URL = "https://openrouter.ai/api/v1/chat/completions"
HttpPost = Callable[[str, dict[str, str], bytes, float], bytes]


class HttpStatusProviderError(ValueError):
    """Raised when the live status provider cannot run safely."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise urllib.error.HTTPError(
            req.full_url, code, f"redirect refused to {newurl}", headers, fp
        )


def _default_http_post(
    url: str, headers: dict[str, str], body: bytes, timeout: float
) -> bytes:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    opener = urllib.request.build_opener(_NoRedirect())
    with opener.open(request, timeout=timeout) as response:
        return response.read()


class HttpStatusProvider:
    """Chat-completions StatusProvider. Fail closed on network/auth/schema errors."""

    name = "http"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        url: str = DEFAULT_HTTP_URL,
        timeout: float = 30.0,
        http_post: HttpPost | None = None,
    ) -> None:
        if not api_key.strip():
            raise HttpStatusProviderError(
                "live status provider requires OPENROUTER_API_KEY or "
                "COMPASS_STATUS_API_KEY"
            )
        if not model.strip():
            raise HttpStatusProviderError(
                "live status provider requires COMPASS_STATUS_MODEL"
            )
        if not url.startswith("https://"):
            raise HttpStatusProviderError(
                "COMPASS_STATUS_HTTP_URL must be an https:// endpoint"
            )
        self.model = model.strip()
        self._api_key = api_key.strip()
        self._url = url.rstrip("/")
        self._timeout = timeout
        self._http_post = http_post or _default_http_post

    @classmethod
    def from_env(cls, *, http_post: HttpPost | None = None) -> "HttpStatusProvider":
        key = (
            os.environ.get("COMPASS_STATUS_API_KEY", "").strip()
            or os.environ.get("OPENROUTER_API_KEY", "").strip()
        )
        model = os.environ.get("COMPASS_STATUS_MODEL", "").strip()
        url = os.environ.get("COMPASS_STATUS_HTTP_URL", DEFAULT_HTTP_URL).strip()
        raw_timeout = os.environ.get("COMPASS_STATUS_HTTP_TIMEOUT", "30").strip() or "30"
        try:
            timeout = float(raw_timeout)
        except ValueError as exc:
            raise HttpStatusProviderError(
                f"invalid COMPASS_STATUS_HTTP_TIMEOUT: {raw_timeout!r}"
            ) from exc
        return cls(
            api_key=key,
            model=model,
            url=url or DEFAULT_HTTP_URL,
            timeout=timeout,
            http_post=http_post,
        )

    def explain(self, snapshot: dict[str, Any]) -> str:
        findings = snapshot.get("findings") or []
        compact = {
            "northstar_version": snapshot.get("northstar_version"),
            "repository_sha": snapshot.get("repository_sha"),
            "skill_count_fs": snapshot.get("skill_count_fs"),
            "skill_count_docs": snapshot.get("skill_count_docs"),
            "active_plan_id": snapshot.get("active_plan_id"),
            "plan_status": snapshot.get("plan_status"),
            "findings": [
                {
                    "kind": f.get("kind"),
                    "severity": f.get("severity"),
                    "claim_kind": f.get("claim_kind"),
                    "summary": f.get("summary"),
                }
                for f in findings
                if isinstance(f, dict)
            ],
        }
        system = (
            "You are the NorthStar Project Overseer. Explain repository status "
            "from the provided snapshot JSON. Label claims as observed, "
            "documented, external, or proposed. Do not approve plans, promote "
            "Skills/Policies, or claim authority. Keep the answer concise."
        )
        user = (
            "Snapshot JSON:\n"
            + json.dumps(compact, sort_keys=True)
            + "\n\nWrite a short Overseer explanation."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/loganware05/captains-compass-cursor",
            "X-Title": "NorthStar Project Overseer",
        }
        try:
            raw = self._http_post(self._url, headers, body, self._timeout)
            doc = json.loads(raw.decode("utf-8"))
        except (
            OSError,
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            json.JSONDecodeError,
            UnicodeDecodeError,
        ) as exc:
            raise HttpStatusProviderError(
                f"live status provider request failed: {exc}"
            ) from exc
        try:
            text = doc["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise HttpStatusProviderError(
                "live status provider returned unexpected response shape"
            ) from exc
        if not isinstance(text, str) or not text.strip():
            raise HttpStatusProviderError(
                "live status provider returned empty explanation"
            )
        return redact_text(text.strip())
