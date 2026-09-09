"""Issue #50 / NorthStar M4 bridge tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.agents.proficiency import (
    build_proficiency_record,
    write_proficiency_record,
)
from orchestrator.integrations.m4_bridge import (
    apply_approved_routing_proposal,
    list_pending_routing_proposals,
    notion_research_context,
    propose_persistent_roles,
    run_m4_bridge,
)
from orchestrator.integrations.routine import run_northstar_routine
from orchestrator.routing.apply import ApplyError

ROOT = Path(__file__).resolve().parents[2]


class M4BridgeUnitTests(unittest.TestCase):
    def test_propose_roles_staging_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            record = build_proficiency_record(
                agent_id="compass-evaluator",
                proficiency_level="proficient",
                experience_ids=["exp-1"],
                classifications=["evaluation"],
                captain_approved=True,
            )
            write_proficiency_record(repo, record)
            result = propose_persistent_roles(repo)
            self.assertEqual(result["proposed_count"], 1)
            proposal_path = Path(result["proposed"][0]["proposal_path"])
            self.assertTrue(proposal_path.is_file())
            staging_agent = repo / ".agent" / "agents" / "promotions" / "staging" / "compass-evaluator" / "agent.md"
            self.assertTrue(staging_agent.is_file())
            self.assertFalse((repo / ".cursor" / "agents" / "compass-evaluator.md").exists())

    def test_surface_routing_and_refuse_silent_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            proposals = repo / ".agent" / "routing" / "proposals"
            proposals.mkdir(parents=True)
            path = proposals / "rp-1.json"
            path.write_text(
                json.dumps(
                    {
                        "kind": "routing-proposal",
                        "proposal_id": "rp-1",
                        "captain_approved": True,
                        "auto_apply": False,
                        "matcher_weight_suggestions": {},
                    }
                ),
                encoding="utf-8",
            )
            surface = list_pending_routing_proposals(repo)
            self.assertEqual(surface["count"], 1)
            with self.assertRaises(ApplyError):
                apply_approved_routing_proposal(repo, path, allow_apply=False)

    def test_notion_fixtures_and_live_skip(self) -> None:
        fixtures = notion_research_context(ROOT, mode="fixtures")
        self.assertFalse(fixtures["authoritative"])
        self.assertGreaterEqual(fixtures["count"], 1)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            live_missing = notion_research_context(repo, mode="live")
            self.assertTrue(live_missing.get("skipped"))
            self.assertEqual(live_missing.get("reason"), "notion_allowlist_missing")

            allowlist = repo / ".agent" / "knowledge" / "notion-allowlist.txt"
            allowlist.parent.mkdir(parents=True)
            page_id = "3cae6a901c4381fd8482e9158ac9e6cc"
            allowlist.write_text(f"{page_id}\n", encoding="utf-8")
            live_empty = notion_research_context(repo, mode="live")
            self.assertTrue(live_empty.get("skipped"))
            self.assertEqual(live_empty.get("reason"), "notion_live_cache_missing")

            cache = repo / ".agent" / "knowledge" / "external" / "notion-live"
            cache.mkdir(parents=True)
            (cache / f"{page_id}.md").write_text("# research\n", encoding="utf-8")
            live_ok = notion_research_context(repo, mode="live")
            self.assertFalse(live_ok.get("skipped"))
            self.assertEqual(live_ok.get("count"), 1)
            self.assertEqual(live_ok["items"][0]["page_id"], page_id)


class M4BridgeRoutineTests(unittest.TestCase):
    def test_bridge_after_review_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            record = build_proficiency_record(
                agent_id="compass-evaluator",
                proficiency_level="expert",
                experience_ids=["exp-bridge"],
                classifications=["evaluation"],
                captain_approved=True,
            )
            write_proficiency_record(repo, record)
            # Copy notion fixture into temp repo for fixture mode
            notion_dir = repo / "tests" / "fixtures" / "notion"
            notion_dir.mkdir(parents=True)
            (notion_dir / "note.md").write_text("research", encoding="utf-8")

            report = run_northstar_routine(
                repo,
                raw_event={
                    "event_id": "obj-bridge",
                    "channel": "northstar",
                    "text": "@NorthStar bridge m4",
                    "mentions": ["NorthStar"],
                    "user_id": "U1",
                    "ts": "42",
                },
                provider="slack",
                approve=True,
                advance_to_review=True,
                propose_roles=True,
                surface_routing=True,
                notion_mode="fixtures",
                run_id="run-bridge",
            )
            self.assertEqual(report["state"], "REVIEW_READY")
            bridge = report.get("m4_bridge") or {}
            self.assertEqual(bridge.get("kind"), "northstar-m4-bridge")
            self.assertEqual((bridge.get("roles") or {}).get("proposed_count"), 1)
            self.assertIn("routing", bridge)
            self.assertEqual((bridge.get("notion") or {}).get("mode"), "fixtures")
            self.assertFalse((bridge.get("notion") or {}).get("authoritative", True))
            evidence = Path(report["evidence_dir"])
            self.assertTrue((evidence / "m4-bridge.json").is_file())
            self.assertTrue((evidence / "notion-summary-mirror.json").is_file())

    def test_bridge_refuses_before_review_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = {"run_id": "r", "state": "IN_PROGRESS", "workstreams": []}
            with self.assertRaises(ValueError):
                run_m4_bridge(Path(tmp), run, propose_roles=True)


if __name__ == "__main__":
    unittest.main()
