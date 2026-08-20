"""Phase H Technology Intelligence provider boundary tests."""

from __future__ import annotations

import unittest

from orchestrator.plan_writer.build import CapabilityPlanArtifacts
from orchestrator.plan_writer.render import render_technology_intelligence_candidates
from orchestrator.providers.technology_intelligence.validate import (
    TechnologyIntelligenceValidationError,
    validate_ti_candidates,
)


def _sample_candidate() -> dict:
    return {
        "id": "external-pdf-lib",
        "version": "0.1.0",
        "kind": "candidate",
        "source": {
            "type": "external-candidate",
            "path": "github.com/example/pdf-lib",
            "provenance_url": "https://github.com/example/pdf-lib",
        },
        "capabilities_provided": ["pdf-parsing"],
        "approved_for_execution": False,
        "lifecycle_stage": "DISCOVERED",
        "discovery_signal": "github-star:42",
        "notes": "Fixture candidate for render tests",
    }


class ValidateTiCandidatesTests(unittest.TestCase):
    def test_accepts_valid_candidate(self) -> None:
        validate_ti_candidates([_sample_candidate()])

    def test_rejects_approved_for_execution_true(self) -> None:
        bad = _sample_candidate()
        bad["approved_for_execution"] = True
        with self.assertRaises(TechnologyIntelligenceValidationError):
            validate_ti_candidates([bad])

    def test_rejects_invalid_schema(self) -> None:
        with self.assertRaises(TechnologyIntelligenceValidationError):
            validate_ti_candidates([{"id": "incomplete"}])


class RenderTiCandidatesTests(unittest.TestCase):
    def test_empty_candidates_show_stub_message(self) -> None:
        artifacts = CapabilityPlanArtifacts(
            plan_id="ti-empty",
            objective="Build auth",
            resolve={},
            task_graph={"tasks": [], "execution_order": []},
            manifests={"manifests": []},
            technology_intelligence_candidates=[],
        )
        markdown = render_technology_intelligence_candidates(artifacts)
        self.assertIn("NOT APPROVED FOR EXECUTION", markdown)
        self.assertIn("provider: stub", markdown)

    def test_non_empty_candidates_render_table_not_approved(self) -> None:
        candidate = _sample_candidate()
        validate_ti_candidates([candidate])
        artifacts = CapabilityPlanArtifacts(
            plan_id="ti-table",
            objective="Parse PDF invoices",
            resolve={},
            task_graph={"tasks": [], "execution_order": []},
            manifests={"manifests": []},
            technology_intelligence_candidates=[candidate],
        )
        markdown = render_technology_intelligence_candidates(artifacts)
        self.assertIn("NOT APPROVED FOR EXECUTION", markdown)
        self.assertIn("external-pdf-lib", markdown)
        self.assertIn("github-star:42", markdown)
        self.assertIn("DISCOVERED", markdown)
        self.assertNotIn("provider: stub", markdown)


if __name__ == "__main__":
    unittest.main()
