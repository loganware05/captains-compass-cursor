"""M26: Cursor Cloud wakeability probe adapter."""

from __future__ import annotations

import unittest

from orchestrator.routing.agent_router import RouteObjective, route_agents, score_agent
from orchestrator.routing.cloud_wakeability_probe import (
    annotate_registry_with_cloud_snapshot,
    build_cloud_wakeability_probe,
    index_cloud_agents,
    map_cloud_lifecycle_to_wakeability,
)

REPO = "loganware05/captain-compass-sandbox"


def _registry_agent(agent_id: str, **overrides):
    agent = {
        "id": agent_id,
        "status": "active",
        "categories": ["design-system"],
        "repository_allowlist": [REPO],
        "skills_installed_scope": ["sandbox"],
        "skills": ["craft-tokens-design-system"],
        "availability": 1.0,
        "repository_familiarity": {REPO: 0.8},
        "category_success": {"design-system": 0.7},
        "historical_runs": 1,
        "autonomy_budget_ok": True,
    }
    agent.update(overrides)
    return agent


def _objective() -> RouteObjective:
    return RouteObjective(
        title="Exercise craft-tokens-design-system",
        category="design-system",
        target_repository=REPO,
        required_skills=["craft-tokens-design-system"],
        skill_scope="sandbox",
    )


class CloudLifecycleMappingTests(unittest.TestCase):
    def test_idle_and_running_are_wakeable(self) -> None:
        self.assertEqual(map_cloud_lifecycle_to_wakeability("IDLE"), "wakeable")
        self.assertEqual(map_cloud_lifecycle_to_wakeability("RUNNING"), "wakeable")

    def test_expired_and_archived_fail_closed(self) -> None:
        self.assertEqual(map_cloud_lifecycle_to_wakeability("EXPIRED"), "expired")
        self.assertEqual(
            map_cloud_lifecycle_to_wakeability("RUNNING", is_archived=True),
            "expired",
        )
        self.assertEqual(
            map_cloud_lifecycle_to_wakeability("IDLE", is_killed=True),
            "expired",
        )

    def test_error_is_unreachable(self) -> None:
        self.assertEqual(map_cloud_lifecycle_to_wakeability("ERROR"), "unreachable")


class CloudProbeRoutingTests(unittest.TestCase):
    def test_probe_marks_missing_snapshot_unknown(self) -> None:
        probe = build_cloud_wakeability_probe([])
        card = score_agent(_registry_agent("bc-missing"), _objective(), probe=probe, prefer_probe=True)
        self.assertEqual(card.wakeability_status, "unknown")
        self.assertEqual(card.wakeability_source, "live_probe")
        self.assertEqual(card.effective_availability, 0.25)

    def test_probe_prefers_live_expired_over_declared_availability(self) -> None:
        cloud = [
            {
                "bcId": "bc-05d4594d-fac7-4378-b595-c20e3c006044",
                "status": "EXPIRED",
                "isArchived": False,
                "isKilled": False,
            }
        ]
        probe = build_cloud_wakeability_probe(cloud)
        card = score_agent(
            _registry_agent(
                "bc-05d4594d-fac7-4378-b595-c20e3c006044",
                wakeability_status="wakeable",  # stale registry claim
            ),
            _objective(),
            probe=probe,
            prefer_probe=True,
        )
        self.assertFalse(card.eligible)
        self.assertEqual(card.wakeability_status, "expired")
        self.assertEqual(card.effective_availability, 0.0)

    def test_route_selects_idle_cloud_agent_over_expired_pin(self) -> None:
        expired = _registry_agent("bc-expired-pin")
        wakeable = _registry_agent("bc-idle-live", availability=0.7)
        cloud = [
            {"bcId": "bc-expired-pin", "status": "EXPIRED"},
            {"bcId": "bc-idle-live", "status": "IDLE"},
        ]
        probe = build_cloud_wakeability_probe(cloud)
        decision = route_agents(
            [expired, wakeable], _objective(), probe=probe, prefer_probe=True
        )
        self.assertEqual(decision.selected_agent_id, "bc-idle-live")
        self.assertTrue(decision.dispatch_ready)

    def test_index_and_annotate_registry(self) -> None:
        cloud = [{"bcId": "bc-a", "status": "IDLE"}]
        index = index_cloud_agents(cloud)
        self.assertIn("bc-a", index)
        annotated = annotate_registry_with_cloud_snapshot(
            [_registry_agent("bc-a"), _registry_agent("bc-b")],
            cloud,
        )
        self.assertEqual(annotated[0]["cloud_status"], "wakeable")
        self.assertEqual(annotated[1]["cloud_status"], "unknown")


if __name__ == "__main__":
    unittest.main()
