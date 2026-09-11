"""M25: agent router wakeability gates declared availability."""

from __future__ import annotations

import unittest

from orchestrator.routing.agent_router import (
    RouteObjective,
    effective_availability,
    load_registry,
    normalize_wakeability,
    route_agents,
    score_agent,
)

REPO = "loganware05/captain-compass-sandbox"


def _base_agent(**overrides):
    agent = {
        "id": "bc-wakeable-0001",
        "status": "active",
        "categories": ["design-system"],
        "repository_allowlist": [REPO],
        "skills_installed_scope": ["sandbox"],
        "skills": ["craft-tokens-design-system"],
        "availability": 1.0,
        "wakeability_status": "wakeable",
        "repository_familiarity": {REPO: 0.85},
        "category_success": {"design-system": 0.7},
        "historical_runs": 2,
        "autonomy_budget_ok": True,
    }
    agent.update(overrides)
    return agent


def _objective(**overrides) -> RouteObjective:
    data = {
        "title": "Exercise craft-tokens-design-system",
        "category": "design-system",
        "target_repository": REPO,
        "required_skills": ["craft-tokens-design-system"],
        "skill_scope": "sandbox",
        "context_agent_id": "bc-wakeable-0001",
    }
    data.update(overrides)
    return RouteObjective(**data)


class WakeabilityNormalizationTests(unittest.TestCase):
    def test_aliases(self) -> None:
        self.assertEqual(normalize_wakeability("running"), "wakeable")
        self.assertEqual(normalize_wakeability("EXPIRED"), "expired")
        self.assertEqual(normalize_wakeability(None), "unknown")

    def test_effective_availability_caps(self) -> None:
        self.assertEqual(effective_availability(1.0, "expired"), 0.0)
        self.assertEqual(effective_availability(1.0, "unreachable"), 0.0)
        self.assertEqual(effective_availability(1.0, "unknown"), 0.25)
        self.assertEqual(effective_availability(0.8, "wakeable"), 0.8)


class Ova17RegressionTests(unittest.TestCase):
    def test_expired_pin_with_declared_availability_one_is_ineligible(self) -> None:
        expired = _base_agent(
            id="bc-05d4594d-fac7-4378-b595-c20e3c006044",
            availability=1.0,
            wakeability_status="expired",
        )
        card = score_agent(expired, _objective())
        self.assertFalse(card.eligible)
        self.assertIn("effective_availability<=0", card.filter_failures)
        self.assertEqual(card.declared_availability, 1.0)
        self.assertEqual(card.effective_availability, 0.0)

    def test_wakeable_agent_remains_dispatch_ready(self) -> None:
        decision = route_agents([_base_agent()], _objective())
        self.assertEqual(decision.selected_agent_id, "bc-wakeable-0001")
        self.assertTrue(decision.dispatch_ready)
        self.assertEqual(decision.agents[0].wakeability_status, "wakeable")

    def test_live_probe_can_mark_unreachable(self) -> None:
        agent = _base_agent()
        agent.pop("wakeability_status", None)

        def probe(_agent):
            return "unreachable"

        card = score_agent(agent, _objective(), probe=probe)
        self.assertFalse(card.eligible)
        self.assertEqual(card.wakeability_source, "live_probe")
        self.assertEqual(card.effective_availability, 0.0)

    def test_route_prefers_wakeable_over_expired_high_declared(self) -> None:
        expired = _base_agent(
            id="bc-expired-high",
            availability=1.0,
            wakeability_status="expired",
            repository_familiarity={REPO: 0.99},
            category_success={"design-system": 0.99},
        )
        wakeable = _base_agent(
            id="bc-wakeable-mid",
            availability=0.7,
            wakeability_status="wakeable",
            repository_familiarity={REPO: 0.5},
            category_success={"design-system": 0.5},
        )
        decision = route_agents([expired, wakeable], _objective(context_agent_id=None))
        self.assertEqual(decision.selected_agent_id, "bc-wakeable-mid")
        self.assertTrue(decision.dispatch_ready)
        self.assertNotIn("bc-expired-high", decision.eligible_agent_ids)

    def test_load_registry_and_unknown_cap(self) -> None:
        agent = _base_agent(id="bc-unknown")
        agent.pop("wakeability_status", None)
        agents = load_registry({"agents": [agent]})
        card = score_agent(agents[0], _objective(context_agent_id=None))
        self.assertEqual(card.wakeability_status, "unknown")
        self.assertEqual(card.effective_availability, 0.25)
        self.assertTrue(card.eligible)


if __name__ == "__main__":
    unittest.main()
