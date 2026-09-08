"""M21 NorthStar branding, events, state machine, adapters, and routine."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.branding import (
    get_branding_registry,
    is_legacy_product_name,
    legacy_alias_received,
    normalize_product_name,
)
from orchestrator.integrations.adapters.cursor import CursorAdapter
from orchestrator.integrations.adapters.github import GitHubAdapter
from orchestrator.integrations.adapters.linear import LinearAdapter
from orchestrator.integrations.adapters.slack import SlackAdapter
from orchestrator.integrations.contracts import M21_INTEGRATION_AGENT_ID
from orchestrator.integrations.events import (
    IdempotencyStore,
    normalize_event,
    redact_secrets,
)
from orchestrator.integrations.routine import (
    NorthStarRoutineError,
    reconcile_northstar_run,
    run_northstar_routine,
)
from orchestrator.integrations.state_machine import (
    StateTransitionError,
    new_run,
    transition_run,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "northstar"


class BrandingTests(unittest.TestCase):
    def test_registry_shape(self) -> None:
        reg = get_branding_registry()
        self.assertEqual(reg["canonical_name"], "NorthStar")
        self.assertEqual(reg["canonical_slug"], "northstar")
        self.assertEqual(reg["compatibility_version"], 1)
        self.assertIn("Captain's Compass", reg["legacy_names"])

    def test_legacy_normalization(self) -> None:
        for name in (
            "Captain's Compass",
            "Captains Compass",
            "Captain Compass",
            "captains-compass",
            "captain-compass",
        ):
            self.assertTrue(is_legacy_product_name(name), name)
            self.assertEqual(normalize_product_name(name), "NorthStar")
            self.assertIsNotNone(legacy_alias_received(name))

    def test_canonical_passthrough(self) -> None:
        self.assertEqual(normalize_product_name("NorthStar"), "NorthStar")
        self.assertIsNone(legacy_alias_received("NorthStar"))


class EventTests(unittest.TestCase):
    def test_normalize_event_contract(self) -> None:
        event = normalize_event(
            provider="slack",
            event_type="objective",
            event_id="e1",
            actor={"provider_id": "U1", "verified_role": "collaborator"},
            product_name_received="Captain's Compass",
            payload={"text": "hi"},
        )
        self.assertEqual(event["product"]["name"], "NorthStar")
        self.assertEqual(event["product"]["legacy_alias_received"], "Captain's Compass")
        self.assertEqual(event["references"]["cursor_agent"], M21_INTEGRATION_AGENT_ID)
        self.assertEqual(len(event["idempotency_key"]), 64)

    def test_idempotency_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = IdempotencyStore(Path(tmp) / "idem.json")
            self.assertTrue(store.remember("e1", "k1"))
            self.assertFalse(store.remember("e1", "k1"))
            store2 = IdempotencyStore(Path(tmp) / "idem.json")
            self.assertTrue(store2.seen("e1", "k1"))

    def test_redaction(self) -> None:
        redacted = redact_secrets({"token": "secret", "ok": 1, "api_key": "x"})
        self.assertEqual(redacted["token"], "[REDACTED]")
        self.assertEqual(redacted["api_key"], "[REDACTED]")
        self.assertEqual(redacted["ok"], 1)


class StateMachineTests(unittest.TestCase):
    def test_happy_path_edges(self) -> None:
        event = normalize_event(provider="github", event_type="objective", event_id="g1")
        run = new_run(run_id="r1", origin_event=event, plan_id="p")
        for state in (
            "RECONCILING",
            "PLAN_PROPOSED",
            "AWAITING_CAPTAIN_APPROVAL",
            "DISPATCHED",
            "IN_PROGRESS",
            "VALIDATING",
            "REVIEW_READY",
            "AWAITING_MERGE",
            "COMPLETED",
        ):
            run = transition_run(run, state)
        self.assertEqual(run["state"], "COMPLETED")
        self.assertEqual(len(run["transitions"]), 10)

    def test_illegal_transition(self) -> None:
        event = normalize_event(provider="github", event_type="objective", event_id="g2")
        run = new_run(run_id="r2", origin_event=event)
        with self.assertRaises(StateTransitionError):
            transition_run(run, "COMPLETED")


class AdapterTests(unittest.TestCase):
    def test_slack_requires_mention(self) -> None:
        slack = SlackAdapter()
        with self.assertRaises(ValueError):
            slack.normalize_event(
                {"channel": "northstar", "text": "hello", "user_id": "U1"}
            )

    def test_slack_legacy_mention(self) -> None:
        slack = SlackAdapter()
        event = slack.normalize_event(
            {
                "channel": "northstar",
                "text": "@CaptainCompass do the thing",
                "mentions": ["CaptainCompass"],
                "user_id": "U1",
                "ts": "1.0",
            }
        )
        self.assertEqual(event["product"]["name"], "NorthStar")
        self.assertEqual(event["product"]["legacy_alias_received"], "Captain's Compass")

    def test_captain_identity_not_spoofable(self) -> None:
        gh = GitHubAdapter()
        actor = gh.verify_identity(
            {"provider_id": "random", "verified_role": "captain"}
        )
        self.assertEqual(actor["verified_role"], "collaborator")

    def test_cursor_rejects_wrong_agent(self) -> None:
        cursor = CursorAdapter()
        with self.assertRaises(StateTransitionError):
            cursor.accept_checkpoint(
                {"event_id": "c1", "agent_id": "bc-other", "checkpoint": "x"}
            )

    def test_linear_fallback_when_disconnected(self) -> None:
        linear = LinearAdapter(connected=False)
        result = linear.create_or_update_work_item({"run_id": "r", "state": "RECEIVED"})
        self.assertEqual(result["fallback"], "github")


class RoutineTests(unittest.TestCase):
    def test_stops_for_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_northstar_routine(
                Path(tmp),
                raw_event={
                    "event_id": "obj-1",
                    "channel": "northstar",
                    "text": "@NorthStar ship M21",
                    "mentions": ["NorthStar"],
                    "user_id": "U1",
                    "ts": "10.1",
                },
                provider="slack",
                approve=False,
            )
            self.assertEqual(report["state"], "AWAITING_CAPTAIN_APPROVAL")
            self.assertEqual(report["product"], "NorthStar")
            self.assertFalse(report.get("duplicate"))

    def test_duplicate_replay_has_no_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw = {
                "event_id": "obj-dup",
                "channel": "northstar",
                "text": "@NorthStar ship M21",
                "mentions": ["NorthStar"],
                "user_id": "U1",
                "ts": "10.2",
            }
            first = run_northstar_routine(
                Path(tmp), raw_event=raw, provider="slack", run_id="run-dup"
            )
            second = run_northstar_routine(
                Path(tmp), raw_event=raw, provider="slack", run_id="run-dup"
            )
            self.assertFalse(first.get("duplicate"))
            self.assertTrue(second.get("duplicate"))

    def test_no_dispatch_before_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_northstar_routine(
                Path(tmp),
                raw_event={
                    "event_id": "obj-2",
                    "channel": "northstar",
                    "text": "@NorthStar x",
                    "mentions": ["NorthStar"],
                    "user_id": "U1",
                    "ts": "11",
                },
                provider="slack",
                approve=False,
            )
            run = json.loads(
                (Path(tmp) / ".agent" / "evidence" / report["run_id"] / "run.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertFalse(run.get("plan_approved"))
            self.assertIsNone(run.get("work_packet"))

    def test_fixture_reaches_review_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_northstar_routine(
                Path(tmp),
                raw_event={
                    "event_id": "obj-3",
                    "channel": "northstar",
                    "text": "@NorthStar finish",
                    "mentions": ["NorthStar"],
                    "user_id": "U1",
                    "ts": "12",
                },
                provider="slack",
                approve=True,
                advance_to_review=True,
                run_id="run-review",
            )
            self.assertEqual(report["state"], "REVIEW_READY")
            self.assertTrue(Path(report["evidence_dir"]).is_dir())
            reconcile = reconcile_northstar_run(
                Path(report["evidence_dir"]) / "run.json"
            )
            self.assertTrue(reconcile["ok"])
            self.assertEqual(reconcile["authority"]["engineering"], "github")

    def test_missing_github_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(NorthStarRoutineError):
                run_northstar_routine(
                    Path(tmp),
                    raw_event={
                        "event_id": "obj-4",
                        "channel": "northstar",
                        "text": "@NorthStar x",
                        "mentions": ["NorthStar"],
                        "user_id": "U1",
                        "ts": "13",
                    },
                    provider="slack",
                    connected={"github": False, "slack": True, "linear": True, "cursor": True},
                )

    def test_wrong_agent_blocks(self) -> None:
        cursor = CursorAdapter()
        with self.assertRaises(StateTransitionError) as ctx:
            cursor.accept_checkpoint(
                {
                    "event_id": "bad",
                    "agent_id": "bc-05d4594d-fac7-4378-b595-c20e3c006045",
                    "checkpoint": "x",
                }
            )
        self.assertIn("BLOCKED_AGENT_IDENTITY", str(ctx.exception))

    def test_fixture_files_load(self) -> None:
        for name in ("slack-objective.json", "github-intake.json", "linear-issue.json"):
            path = FIXTURES / name
            self.assertTrue(path.is_file(), name)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("event_type", data)


if __name__ == "__main__":
    unittest.main()
