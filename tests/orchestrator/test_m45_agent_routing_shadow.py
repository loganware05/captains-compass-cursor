"""M45 DecisionProvider agent routing shadow — hermetic tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.providers.decision.agent_routing_shadow import (
    EVIDENCE_ROOT_REL,
    maybe_run_agent_routing_shadow,
)
from orchestrator.providers.decision.file_provider import (
    FileDecisionProvider,
    decision_agent_routing_shadow_enabled,
)
from orchestrator.providers.decision.types import (
    AgentRoutingRequest,
    EligibleAgentSummary,
)
from orchestrator.routing.agent_router import RouteObjective, route_agents

ROOT = Path(__file__).resolve().parents[2]


def _agents() -> list[dict]:
    return [
        {
            "id": "agent-cloud-reviewer",
            "name": "Cloud Reviewer",
            "status": "active",
            "availability": 1.0,
            "wakeability_status": "wakeable",
            "categories": ["review"],
            "repository_allowlist": ["*"],
            "skills_installed_scope": ["sandbox", "any"],
            "description": "Reviews wakeability and cloud agent pins",
        },
        {
            "id": "agent-generalist",
            "name": "Generalist",
            "status": "active",
            "availability": 0.8,
            "wakeability_status": "wakeable",
            "categories": ["review", "general"],
            "repository_allowlist": ["*"],
            "skills_installed_scope": ["any"],
            "description": "General execution",
        },
        {
            "id": "agent-expired",
            "name": "Expired",
            "status": "active",
            "availability": 1.0,
            "wakeability_status": "expired",
            "categories": ["review"],
            "repository_allowlist": ["*"],
            "skills_installed_scope": ["any"],
            "description": "Expired pin",
        },
    ]


def _objective() -> RouteObjective:
    return RouteObjective(
        title="Investigate wakeability routing for cloud agents",
        category="review",
        target_repository="captains-compass-cursor",
        required_skills=[],
        skill_scope="sandbox",
    )


class AgentRoutingEnvTests(unittest.TestCase):
    def test_default_off(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_DECISION_AGENT_ROUTING_SHADOW", None)
            self.assertFalse(decision_agent_routing_shadow_enabled())


class FileAgentRoutingTests(unittest.TestCase):
    def test_wakeability_fixture(self) -> None:
        provider = FileDecisionProvider()
        request = AgentRoutingRequest(
            objective_title="Investigate wakeability routing",
            objective_category="review",
            target_repository="captains-compass-cursor",
            eligible_agents=[
                EligibleAgentSummary(
                    agent_id="agent-cloud-reviewer",
                    name="Cloud Reviewer",
                    description="review",
                ),
                EligibleAgentSummary(
                    agent_id="agent-generalist",
                    name="Generalist",
                    description="general",
                ),
            ],
            roster_hash="abc",
        )
        result = provider.suggest_agents(request)
        self.assertFalse(result.abstain)
        self.assertEqual(result.suggested_agent_id, "agent-cloud-reviewer")


class AgentRoutingShadowIntegrationTests(unittest.TestCase):
    def test_shadow_eligible_only_and_does_not_mutate_selection(self) -> None:
        agents = _agents()
        decision = route_agents(agents, _objective())
        self.assertIn("agent-cloud-reviewer", decision.eligible_agent_ids)
        self.assertNotIn("agent-expired", decision.eligible_agent_ids)
        baseline_selected = decision.selected_agent_id
        baseline_ready = decision.dispatch_ready

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with mock.patch.dict(
                os.environ,
                {
                    "COMPASS_DECISION_PROVIDER": "file",
                    "COMPASS_DECISION_AGENT_ROUTING_SHADOW": "1",
                },
            ):
                ref = maybe_run_agent_routing_shadow(
                    repo,
                    decision=decision,
                    agents=agents,
                    plan_id="m45-test",
                )
            self.assertIsNotNone(ref)
            assert ref is not None
            self.assertFalse(ref["applied"])
            evidence = repo / ref["evidence_path"]
            self.assertTrue(evidence.is_file())
            self.assertTrue(str(ref["evidence_path"]).startswith(str(EVIDENCE_ROOT_REL)))
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "northstar.decision_agent_routing.v1")
            self.assertFalse(payload["applied"])
            self.assertEqual(
                payload["baseline"]["eligible_agent_ids"], decision.eligible_agent_ids
            )
            self.assertNotIn("agent-expired", payload["baseline"]["eligible_agent_ids"])
            # Routing decision object unchanged
            self.assertEqual(decision.selected_agent_id, baseline_selected)
            self.assertEqual(decision.dispatch_ready, baseline_ready)

    def test_default_route_unchanged_without_shadow(self) -> None:
        agents = _agents()
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_DECISION_PROVIDER": "stub",
                "COMPASS_DECISION_AGENT_ROUTING_SHADOW": "",
            },
            clear=False,
        ):
            os.environ.pop("COMPASS_DECISION_AGENT_ROUTING_SHADOW", None)
            first = route_agents(agents, _objective())
            second = route_agents(agents, _objective())
        self.assertEqual(first.selected_agent_id, second.selected_agent_id)
        self.assertEqual(first.dispatch_ready, second.dispatch_ready)
        self.assertEqual(first.eligible_agent_ids, second.eligible_agent_ids)


class CiAgentRoutingShadowUnsetTests(unittest.TestCase):
    def test_ci_workflow_does_not_enable_agent_routing_shadow(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertNotIn("COMPASS_DECISION_AGENT_ROUTING_SHADOW", workflow)


if __name__ == "__main__":
    unittest.main()
