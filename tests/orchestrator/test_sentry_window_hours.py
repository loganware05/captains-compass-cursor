"""Hermetic tests: Sentry window_hours lands in live Issues query."""

from __future__ import annotations

import json
import os
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlparse

from orchestrator.integrations.sentry.client import (
    SentryClientError,
    build_issues_list_query,
    fetch_live_issues,
    normalize_window_hours,
)
from orchestrator.integrations.transport import HttpResponse, RecordingTransport


class WindowQueryUnitTests(unittest.TestCase):
    def test_build_query_includes_last_seen(self) -> None:
        self.assertEqual(
            build_issues_list_query(24),
            "is:unresolved lastSeen:-24h",
        )
        self.assertEqual(
            build_issues_list_query(1),
            "is:unresolved lastSeen:-1h",
        )
        self.assertEqual(
            build_issues_list_query(168),
            "is:unresolved lastSeen:-168h",
        )

    def test_normalize_rejects_out_of_range(self) -> None:
        with self.assertRaises(SentryClientError):
            normalize_window_hours(0)
        with self.assertRaises(SentryClientError):
            normalize_window_hours(8761)
        with self.assertRaises(SentryClientError):
            normalize_window_hours("nope")  # type: ignore[arg-type]


class LiveFetchWindowTests(unittest.TestCase):
    def test_list_query_embeds_window_hours(self) -> None:
        body = json.dumps(
            [{"id": "1", "title": "boom", "shortId": "PROJ-1"}]
        ).encode("utf-8")
        transport = RecordingTransport(
            default=HttpResponse(status=200, headers={}, body=body)
        )
        env = {
            "COMPASS_SENTRY_INGEST_ENABLED": "1",
            "COMPASS_SENTRY_LIVE": "1",
            "COMPASS_SENTRY_AUTH_TOKEN": "test-token-not-real",
            "COMPASS_SENTRY_API_BASE": "https://sentry.io/api/0",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            issues = fetch_live_issues(
                org="acme",
                project="northstar",
                window_hours=48,
                transport=transport,
            )
        self.assertEqual(len(issues), 1)
        self.assertEqual(len(transport.calls), 1)
        url = transport.calls[0]["url"]
        parsed = urlparse(url)
        self.assertTrue(parsed.path.endswith("/projects/acme/northstar/issues/"))
        qs = parse_qs(parsed.query)
        self.assertEqual(qs.get("query"), ["is:unresolved lastSeen:-48h"])
        self.assertEqual(qs.get("limit"), ["25"])
        # Token must not appear in RecordingTransport.calls (redacted headers).
        headers = transport.calls[0]["headers"]
        joined = " ".join(f"{k}={v}" for k, v in headers.items())
        self.assertNotIn("test-token-not-real", joined)

    def test_issue_id_path_ignores_window(self) -> None:
        body = json.dumps({"id": "99", "title": "one"}).encode("utf-8")
        transport = RecordingTransport(
            default=HttpResponse(status=200, headers={}, body=body)
        )
        env = {
            "COMPASS_SENTRY_INGEST_ENABLED": "1",
            "COMPASS_SENTRY_LIVE": "1",
            "COMPASS_SENTRY_AUTH_TOKEN": "test-token-not-real",
            "COMPASS_SENTRY_API_BASE": "https://sentry.io/api/0",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            fetch_live_issues(
                org="acme",
                project="northstar",
                issue_id="99",
                window_hours=12,
                transport=transport,
            )
        url = transport.calls[0]["url"]
        self.assertIn("/issues/99/", url)
        self.assertNotIn("lastSeen", url)


if __name__ == "__main__":
    unittest.main()
