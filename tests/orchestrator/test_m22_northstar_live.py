"""M22 NorthStar live ops: transport, ingress, allowlist, fail-closed authority."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from orchestrator.integrations.adapters.cursor import CursorAdapter
from orchestrator.integrations.adapters.github import GitHubAdapter
from orchestrator.integrations.adapters.linear import LinearAdapter
from orchestrator.integrations.adapters.live import build_northstar_adapters
from orchestrator.integrations.adapters.slack import SlackAdapter
from orchestrator.integrations.contracts import M21_INTEGRATION_AGENT_ID
from orchestrator.integrations.events import redact_secrets
from orchestrator.integrations.ingress.github_webhook import map_github_delivery
from orchestrator.integrations.ingress.server import serve_ingress
from orchestrator.integrations.ingress.signatures import verify_github_signature
from orchestrator.integrations.product_allowlist import (
    DEFAULT_PRODUCT_REPOSITORY,
    PRODUCT_DISPATCH_ALLOWLIST,
    require_allowed_repository,
)
from orchestrator.integrations.routine import NorthStarRoutineError, run_northstar_routine
from orchestrator.integrations.state_machine import StateTransitionError, mark_plan_approved, new_run, transition_run
from orchestrator.integrations.transport import HttpResponse, RecordingTransport

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "northstar"
SANDBOX = "loganware05/captain-compass-sandbox"


class _LiveCaptainEnv(unittest.TestCase):
    """Live-mode tests must explicitly allowlist the fixture captain id."""

    def setUp(self) -> None:
        self._prev_captains = os.environ.get("NORTHSTAR_CAPTAIN_GITHUB_IDS")
        os.environ["NORTHSTAR_CAPTAIN_GITHUB_IDS"] = "captain-github"

    def tearDown(self) -> None:
        if self._prev_captains is None:
            os.environ.pop("NORTHSTAR_CAPTAIN_GITHUB_IDS", None)
        else:
            os.environ["NORTHSTAR_CAPTAIN_GITHUB_IDS"] = self._prev_captains


def _sign(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return "sha256=" + digest


class TransportTests(unittest.TestCase):
    def test_recording_transport_records_and_returns(self) -> None:
        transport = RecordingTransport(
            {
                ("GET", "https://api.github.com/rate"): HttpResponse(
                    status=200, headers={"content-type": "application/json"}, body=b'{"ok":true}'
                )
            }
        )
        resp = transport.request(
            "GET",
            "https://api.github.com/rate_limit",
            headers={"Authorization": "Bearer secret-token"},
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.body, b'{"ok":true}')
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.calls[0]["headers"]["authorization"], "[REDACTED]")

    def test_live_github_adapter_uses_transport_shape(self) -> None:
        transport = RecordingTransport(
            {
                ("POST", "https://api.github.com/repos/"): HttpResponse(
                    status=201, headers={}, body=b'{"number":7}'
                )
            }
        )
        os.environ["NORTHSTAR_GITHUB_TOKEN"] = "test-gh-token"
        try:
            gh = GitHubAdapter(
                mode="live",
                transport=transport,
                product_repository=SANDBOX,
                connected=True,
            )
            item = gh.create_or_update_work_item(
                {"run_id": "r-live", "state": "AWAITING_CAPTAIN_APPROVAL", "plan_id": "p"}
            )
            self.assertEqual(item["remote"]["number"], 7)
            self.assertTrue(transport.calls)
            self.assertTrue(transport.calls[0]["url"].startswith("https://api.github.com/repos/"))
        finally:
            os.environ.pop("NORTHSTAR_GITHUB_TOKEN", None)


class SignatureTests(unittest.TestCase):
    def test_valid_hmac(self) -> None:
        body = b'{"ok":true}'
        secret = "whsec"
        sig = _sign(body, secret)
        self.assertTrue(verify_github_signature(body=body, signature_header=sig, secret=secret))

    def test_wrong_secret(self) -> None:
        body = b'{"ok":true}'
        sig = _sign(body, "right")
        self.assertFalse(verify_github_signature(body=body, signature_header=sig, secret="wrong"))

    def test_missing_prefix(self) -> None:
        body = b"{}"
        digest = hmac.new(b"s", body, hashlib.sha256).hexdigest()
        self.assertFalse(
            verify_github_signature(body=body, signature_header=digest, secret="s")
        )

    def test_tampered_body(self) -> None:
        body = b'{"a":1}'
        sig = _sign(body, "s")
        self.assertFalse(verify_github_signature(body=b'{"a":2}', signature_header=sig, secret="s"))


class AllowlistTests(unittest.TestCase):
    def test_sandbox_allowed(self) -> None:
        self.assertEqual(require_allowed_repository(SANDBOX), SANDBOX)
        self.assertIn(DEFAULT_PRODUCT_REPOSITORY, PRODUCT_DISPATCH_ALLOWLIST)

    def test_control_blocked(self) -> None:
        with self.assertRaises(NorthStarRoutineError) as ctx:
            require_allowed_repository("loganware05/captains-compass-cursor")
        self.assertIn("BLOCKED_SCOPE", str(ctx.exception))

    def test_work_packet_non_sandbox_blocked(self) -> None:
        cursor = CursorAdapter(mode="live", transport=RecordingTransport(), product_repository=SANDBOX)
        event = {
            "event_id": "e1",
            "provider": "github",
            "project": {"repository": "evil/other"},
            "payload": {},
        }
        run = new_run(run_id="r1", origin_event=event, plan_id="p")
        run = transition_run(run, "RECONCILING")
        run = transition_run(run, "PLAN_PROPOSED")
        run = transition_run(run, "AWAITING_CAPTAIN_APPROVAL")
        run = mark_plan_approved(
            run,
            plan_id="p",
            plan_digest="d" * 64,
            captain_actor={"provider_id": "captain-github", "verified_role": "captain"},
            github_approval_ref="github:issue-comment:1",
        )
        # product_repository forces sandbox into packet; override to prove reject path:
        cursor.product_repository = "evil/other"
        with self.assertRaises(StateTransitionError) as ctx:
            cursor.build_work_packet(run)
        self.assertIn("BLOCKED_SCOPE", str(ctx.exception))


class LiveGitHubAdapterTests(_LiveCaptainEnv):
    def test_intake_normalize_allowlisted(self) -> None:
        gh = GitHubAdapter(mode="live", transport=RecordingTransport(), product_repository=SANDBOX)
        event = gh.normalize_event(
            {
                "event_id": "d1",
                "event_type": "objective",
                "repository": SANDBOX,
                "label": "northstar",
                "intake": True,
                "title": "x",
                "actor_id": "captain-github",
            }
        )
        self.assertEqual(event["project"]["repository"], SANDBOX)

    def test_approval_matching_digest(self) -> None:
        gh = GitHubAdapter(mode="fixtures")
        run = new_run(
            run_id="r-appr",
            origin_event={"event_id": "e", "provider": "github", "project": {"repository": SANDBOX}},
            plan_id="p",
        )
        run = transition_run(run, "RECONCILING")
        run = transition_run(run, "PLAN_PROPOSED")
        run = transition_run(run, "AWAITING_CAPTAIN_APPROVAL")
        digest = "a" * 64
        run["plan_digest"] = digest
        updated = gh.record_canonical_approval(
            run,
            plan_id="p",
            plan_digest=digest,
            actor_id="captain-github",
            approval_ref="github:issue-comment:9",
        )
        self.assertTrue(updated["plan_approved"])
        self.assertTrue(gh.verify_plan_digest(updated, digest))

    def test_approval_wrong_digest(self) -> None:
        gh = GitHubAdapter()
        run = new_run(run_id="r-bad", origin_event={"event_id": "e"}, plan_id="p")
        run = transition_run(run, "RECONCILING")
        run = transition_run(run, "PLAN_PROPOSED")
        run = transition_run(run, "AWAITING_CAPTAIN_APPROVAL")
        run["plan_digest"] = "b" * 64
        with self.assertRaises(StateTransitionError) as ctx:
            gh.record_canonical_approval(
                run,
                plan_id="p",
                plan_digest="c" * 64,
                actor_id="captain-github",
                approval_ref="github:issue-comment:9",
            )
        self.assertIn("BLOCKED_APPROVAL", str(ctx.exception))

    def test_non_captain_cannot_approve(self) -> None:
        gh = GitHubAdapter()
        run = new_run(run_id="r-nc", origin_event={"event_id": "e"}, plan_id="p")
        run = transition_run(run, "RECONCILING")
        run = transition_run(run, "PLAN_PROPOSED")
        run = transition_run(run, "AWAITING_CAPTAIN_APPROVAL")
        run["plan_digest"] = "d" * 64
        with self.assertRaises(StateTransitionError):
            gh.record_canonical_approval(
                run,
                plan_id="p",
                plan_digest="d" * 64,
                actor_id="random-user",
                approval_ref="github:issue-comment:9",
            )


class AuthorityTests(unittest.TestCase):
    def test_slack_intent_not_authoritative(self) -> None:
        slack = SlackAdapter()
        intent = slack.record_approval_intent({"run_id": "r"}, actor_id="captain-slack")
        self.assertFalse(intent["authoritative"])
        self.assertTrue(intent["requires_github_approval"])

    def test_linear_never_sets_plan_approved(self) -> None:
        linear = LinearAdapter()
        run = {"run_id": "r", "state": "AWAITING_CAPTAIN_APPROVAL", "plan_approved": False}
        linear.create_or_update_work_item(run)
        self.assertFalse(run.get("plan_approved"))
        intent = linear.record_approval_intent(run, actor_id="captain-linear")
        self.assertFalse(intent["authoritative"])

    def test_missing_github_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(NorthStarRoutineError):
                run_northstar_routine(
                    Path(tmp),
                    raw_event={
                        "event_id": "obj-m22",
                        "channel": "northstar",
                        "text": "@NorthStar x",
                        "mentions": ["NorthStar"],
                        "user_id": "U1",
                        "ts": "1",
                    },
                    provider="slack",
                    connected={"github": False, "slack": True, "linear": True, "cursor": True},
                )


class IngressTests(unittest.TestCase):
    def _start(self, tmp: Path, *, mode: str, secret: str = "test-secret"):
        os.environ["NORTHSTAR_GITHUB_TOKEN"] = "test-gh-token"
        os.environ["NORTHSTAR_LINEAR_API_KEY"] = "test-linear"
        os.environ["NORTHSTAR_SLACK_BOT_TOKEN"] = "test-slack"
        transport = RecordingTransport()

        def runner(*args, **kwargs):
            kwargs.setdefault("transport", transport)
            kwargs.setdefault("connected", {
                "github": True,
                "linear": True,
                "slack": False,
                "cursor": True,
            })
            return run_northstar_routine(*args, **kwargs)

        server = serve_ingress(
            repo_root=tmp,
            host="127.0.0.1",
            port=0,
            mode=mode,
            product_repository=SANDBOX,
            webhook_secret=secret,
            routine_runner=runner,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address[:2]
        return server, f"http://{host}:{port}"

    def tearDown(self) -> None:
        for key in (
            "NORTHSTAR_GITHUB_TOKEN",
            "NORTHSTAR_LINEAR_API_KEY",
            "NORTHSTAR_SLACK_BOT_TOKEN",
        ):
            os.environ.pop(key, None)

    def test_healthz(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            server, base = self._start(Path(tmp), mode="fixtures")
            try:
                with urllib.request.urlopen(base + "/healthz") as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(data["ok"])
                self.assertEqual(data["product"], "NorthStar")
                self.assertEqual(data["mode"], "fixtures")
            finally:
                server.shutdown()
                server.server_close()

    def test_bad_signature_401(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            server, base = self._start(Path(tmp), mode="live")
            try:
                body = (FIXTURES / "github-webhook-issues-opened.json").read_bytes()
                req = urllib.request.Request(
                    base + "/webhooks/github",
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-Hub-Signature-256": "sha256=deadbeef",
                        "X-GitHub-Delivery": "del-bad",
                        "X-GitHub-Event": "issues",
                    },
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(req)
                self.assertEqual(ctx.exception.code, 401)
            finally:
                server.shutdown()
                server.server_close()

    def test_good_signature_intake(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            secret = "test-secret"
            server, base = self._start(Path(tmp), mode="live", secret=secret)
            try:
                body = (FIXTURES / "github-webhook-issues-opened.json").read_bytes()
                req = urllib.request.Request(
                    base + "/webhooks/github",
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-Hub-Signature-256": _sign(body, secret),
                        "X-GitHub-Delivery": "del-good-1",
                        "X-GitHub-Event": "issues",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(data["ok"])
                self.assertFalse(data.get("duplicate"))
                self.assertEqual(data.get("state"), "AWAITING_CAPTAIN_APPROVAL")
            finally:
                server.shutdown()
                server.server_close()

    def test_duplicate_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            secret = "test-secret"
            server, base = self._start(Path(tmp), mode="live", secret=secret)
            try:
                body = (FIXTURES / "github-webhook-issues-opened.json").read_bytes()
                headers = {
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": _sign(body, secret),
                    "X-GitHub-Delivery": "del-dup-1",
                    "X-GitHub-Event": "issues",
                }
                req1 = urllib.request.Request(base + "/webhooks/github", data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req1) as resp:
                    first = json.loads(resp.read().decode("utf-8"))
                req2 = urllib.request.Request(base + "/webhooks/github", data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req2) as resp:
                    second = json.loads(resp.read().decode("utf-8"))
                self.assertFalse(first.get("duplicate"))
                self.assertTrue(second.get("duplicate"))
            finally:
                server.shutdown()
                server.server_close()

    def test_non_allowlisted_repo_403(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            secret = "test-secret"
            server, base = self._start(Path(tmp), mode="live", secret=secret)
            try:
                payload = {
                    "action": "opened",
                    "issue": {"number": 1, "title": "x", "body": "y", "labels": [{"name": "northstar"}]},
                    "repository": {"full_name": "loganware05/captains-compass-cursor"},
                    "sender": {"login": "captain-github"},
                }
                body = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    base + "/webhooks/github",
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-Hub-Signature-256": _sign(body, secret),
                        "X-GitHub-Delivery": "del-scope",
                        "X-GitHub-Event": "issues",
                    },
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(req)
                self.assertEqual(ctx.exception.code, 403)
            finally:
                server.shutdown()
                server.server_close()

    def test_fixture_mode_webhook_503(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            server, base = self._start(Path(tmp), mode="fixtures")
            try:
                body = b"{}"
                req = urllib.request.Request(
                    base + "/webhooks/github",
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(req)
                self.assertEqual(ctx.exception.code, 503)
            finally:
                server.shutdown()
                server.server_close()

    def test_map_approval_comment(self) -> None:
        payload = json.loads(
            (FIXTURES / "github-webhook-issue-comment-approve.json").read_text(encoding="utf-8")
        )
        raw = map_github_delivery(
            event_name="issue_comment",
            delivery_id="del-appr",
            payload=payload,
        )
        assert raw is not None
        self.assertEqual(raw["event_type"], "approval")
        self.assertEqual(len(raw["plan_digest"]), 64)


class RoutineLiveModeTests(_LiveCaptainEnv):
    def tearDown(self) -> None:
        for key in (
            "NORTHSTAR_GITHUB_TOKEN",
            "NORTHSTAR_LINEAR_API_KEY",
            "NORTHSTAR_SLACK_BOT_TOKEN",
        ):
            os.environ.pop(key, None)

    def test_fixtures_default_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_northstar_routine(
                Path(tmp),
                raw_event={
                    "event_id": "m22-fix",
                    "channel": "northstar",
                    "text": "@NorthStar ship",
                    "mentions": ["NorthStar"],
                    "user_id": "U1",
                    "ts": "22",
                },
                provider="slack",
                approve=False,
            )
            self.assertEqual(report["state"], "AWAITING_CAPTAIN_APPROVAL")
            self.assertEqual(report.get("mode"), "fixtures")

    def test_live_approve_shortcut_refused(self) -> None:
        os.environ["NORTHSTAR_GITHUB_TOKEN"] = "t"
        os.environ["NORTHSTAR_LINEAR_API_KEY"] = "t"
        transport = RecordingTransport()
        with tempfile.TemporaryDirectory() as tmp:
            report = run_northstar_routine(
                Path(tmp),
                raw_event={
                    "event_id": "m22-live-no-approve",
                    "event_type": "objective",
                    "repository": SANDBOX,
                    "label": "northstar",
                    "intake": True,
                    "title": "live",
                    "actor_id": "captain-github",
                },
                provider="github",
                mode="live",
                product_repository=SANDBOX,
                transport=transport,
                approve=True,
                connected={"github": True, "linear": True, "slack": False, "cursor": True},
            )
            self.assertEqual(report["state"], "AWAITING_CAPTAIN_APPROVAL")
            self.assertIn("refuses --approve", report["message"])

    def test_live_approval_delivery_dispatches(self) -> None:
        os.environ["NORTHSTAR_GITHUB_TOKEN"] = "t"
        os.environ["NORTHSTAR_LINEAR_API_KEY"] = "t"
        transport = RecordingTransport()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            intake = run_northstar_routine(
                root,
                raw_event={
                    "event_id": "m22-live-intake",
                    "event_type": "objective",
                    "repository": SANDBOX,
                    "label": "northstar",
                    "intake": True,
                    "title": "live dispatch",
                    "actor_id": "captain-github",
                },
                provider="github",
                mode="live",
                product_repository=SANDBOX,
                transport=transport,
                approve=False,
                connected={"github": True, "linear": True, "slack": False, "cursor": True},
                run_id="run-live-appr",
            )
            digest = intake["plan_digest"]
            approval = {
                "event_type": "approval",
                "delivery_id": "del-live-appr",
                "repository": SANDBOX,
                "issue": "42",
                "plan_digest": digest,
                "approval_ref": "github:issue-comment:del-live-appr",
                "actor_id": "captain-github",
                "title": "live dispatch",
            }
            report = run_northstar_routine(
                root,
                raw_event=approval,
                provider="github",
                mode="live",
                product_repository=SANDBOX,
                transport=transport,
                live_approval=approval,
                connected={"github": True, "linear": True, "slack": False, "cursor": True},
                run_id="run-live-appr",
            )
            self.assertEqual(report["state"], "IN_PROGRESS")
            self.assertTrue(report["work_packet"]["repository"] == SANDBOX)

    def test_secrets_redacted(self) -> None:
        redacted = redact_secrets(
            {
                "webhook_secret": "abc",
                "X-Hub-Signature-256": "sha256=abc",
                "NORTHSTAR_GITHUB_TOKEN": "tok",
                "ok": 1,
            }
        )
        self.assertEqual(redacted["webhook_secret"], "[REDACTED]")
        self.assertEqual(redacted["X-Hub-Signature-256"], "[REDACTED]")
        self.assertEqual(redacted["NORTHSTAR_GITHUB_TOKEN"], "[REDACTED]")
        self.assertEqual(redacted["ok"], 1)

    def test_wrong_agent_still_blocked(self) -> None:
        cursor = CursorAdapter(
            mode="live", transport=RecordingTransport(), product_repository=SANDBOX
        )
        with self.assertRaises(StateTransitionError) as ctx:
            cursor.accept_checkpoint(
                {"event_id": "c", "agent_id": "bc-wrong", "checkpoint": "x"}
            )
        self.assertIn("BLOCKED_AGENT_IDENTITY", str(ctx.exception))
        self.assertEqual(cursor.allowed_agent_id, M21_INTEGRATION_AGENT_ID)

    def test_factory_builds_live_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            built = build_northstar_adapters(
                mode="live",
                store_dir=Path(tmp),
                connected={"github": True, "linear": True, "slack": True, "cursor": True},
                transport=RecordingTransport(),
                product_repository=SANDBOX,
            )
            self.assertEqual(built["github"].mode, "live")
            self.assertEqual(built["github"].healthcheck()["mode"], "live")
            self.assertEqual(built["linear"].healthcheck()["mode"], "live")

    def test_empty_live_approval_digest_blocked(self) -> None:
        os.environ["NORTHSTAR_GITHUB_TOKEN"] = "t"
        os.environ["NORTHSTAR_LINEAR_API_KEY"] = "t"
        transport = RecordingTransport()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(NorthStarRoutineError) as ctx:
                run_northstar_routine(
                    Path(tmp),
                    raw_event={
                        "event_id": "m22-empty-digest",
                        "event_type": "approval",
                        "repository": SANDBOX,
                        "issue": "1",
                        "actor_id": "captain-github",
                    },
                    provider="github",
                    mode="live",
                    product_repository=SANDBOX,
                    transport=transport,
                    live_approval={
                        "event_type": "approval",
                        "plan_digest": "",
                        "actor_id": "captain-github",
                        "repository": SANDBOX,
                        "issue": "1",
                        "delivery_id": "d-empty",
                    },
                    connected={"github": True, "linear": True, "slack": False, "cursor": True},
                )
            self.assertIn("64-hex plan_digest", str(ctx.exception))

    def test_fixture_captain_not_trusted_without_env(self) -> None:
        os.environ.pop("NORTHSTAR_CAPTAIN_GITHUB_IDS", None)
        os.environ["NORTHSTAR_GITHUB_TOKEN"] = "t"
        os.environ["NORTHSTAR_LINEAR_API_KEY"] = "t"
        transport = RecordingTransport()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Direct adapter construction in live mode must not include fixture id.
            gh = GitHubAdapter(
                mode="live",
                transport=transport,
                product_repository=SANDBOX,
                store_dir=root / "gh",
            )
            self.assertNotIn("captain-github", gh.captain_ids)
            with self.assertRaises(NorthStarRoutineError) as ctx:
                run_northstar_routine(
                    root,
                    raw_event={
                        "event_id": "m22-no-fixture-captain",
                        "event_type": "approval",
                        "repository": SANDBOX,
                        "issue": "9",
                        "actor_id": "captain-github",
                    },
                    provider="github",
                    mode="live",
                    product_repository=SANDBOX,
                    transport=transport,
                    live_approval={
                        "event_type": "approval",
                        "plan_digest": "a" * 64,
                        "actor_id": "captain-github",
                        "repository": SANDBOX,
                        "issue": "9",
                        "delivery_id": "d-fix",
                    },
                    connected={"github": True, "linear": True, "slack": False, "cursor": True},
                )
            self.assertIn("not a verified Captain", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
