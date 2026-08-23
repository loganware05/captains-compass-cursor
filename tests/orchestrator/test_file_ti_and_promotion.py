"""File TI provider and candidate promotion tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_technology_intelligence_candidates
from orchestrator.promotion.advance import (
    advance_to_analyzed,
    write_skill_sidecar_draft,
    write_staging_candidate,
)
from orchestrator.providers.technology_intelligence.file_provider import (
    FileTechnologyIntelligenceProvider,
    select_ti_provider,
)
from orchestrator.providers.technology_intelligence import StubTechnologyIntelligenceProvider
from orchestrator.training.from_experience import train_skill_from_experience

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_CANDIDATE = (
    ROOT
    / "orchestrator"
    / "providers"
    / "technology_intelligence"
    / "fixtures"
    / "stars-redacted-accessible-forms.json"
)
EXPERIENCE_FIXTURE = ROOT / "tests" / "fixtures" / "experience" / "contact-counter.json"


class FileTiProviderTests(unittest.TestCase):
    def test_file_provider_loads_redacted_stars_fixtures(self) -> None:
        provider = FileTechnologyIntelligenceProvider()
        candidates = provider.discover_candidates("accessible forms", {})
        self.assertGreaterEqual(len(candidates), 2)
        ids = {c.id for c in candidates}
        self.assertIn("stars-redacted-accessible-forms", ids)
        for candidate in candidates:
            payload = candidate.to_dict()
            self.assertFalse(payload["approved_for_execution"])

    def test_select_provider_defaults_to_stub(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_TI_PROVIDER", None)
            provider = select_ti_provider()
        self.assertIsInstance(provider, StubTechnologyIntelligenceProvider)

    def test_plan_writer_file_provider_renders_candidates(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_TI_PROVIDER": "file"}):
            artifacts = build_capability_plan(
                ROOT,
                "Build accessible React forms",
                plan_id="test-file-ti",
            )
            markdown = render_technology_intelligence_candidates(artifacts)
        self.assertIn("NOT APPROVED FOR EXECUTION", markdown)
        self.assertIn("stars-redacted-accessible-forms", markdown)
        self.assertIn("Provider: `file`", markdown)


class PromotionTests(unittest.TestCase):
    def test_advance_to_analyzed(self) -> None:
        from orchestrator.promotion.advance import load_candidate_json

        candidate = load_candidate_json(FIXTURE_CANDIDATE)
        promoted = advance_to_analyzed(candidate)
        self.assertEqual(promoted["lifecycle_stage"], "ANALYZED")
        self.assertFalse(promoted["approved_for_execution"])

    def test_rejects_approved_for_execution(self) -> None:
        bad = {
            "id": "x",
            "version": "0.1.0",
            "kind": "candidate",
            "source": {"type": "external-candidate", "path": "x"},
            "capabilities_provided": ["x"],
            "approved_for_execution": True,
            "lifecycle_stage": "DISCOVERED",
        }
        with self.assertRaises(Exception):
            advance_to_analyzed(bad)

    def test_writes_staging_and_skill_draft(self) -> None:
        from orchestrator.promotion.advance import load_candidate_json

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            candidate = load_candidate_json(FIXTURE_CANDIDATE)
            staging = write_staging_candidate(repo, candidate)
            self.assertTrue(staging.is_file())
            draft = write_skill_sidecar_draft(repo, candidate, "accessible-forms-patterns")
            self.assertTrue(draft.is_file())
            self.assertIn("captain_approval_required", draft.read_text(encoding="utf-8"))


class ExperienceTrainingTests(unittest.TestCase):
    def test_trains_draft_from_fixture_experience(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp)
            paths = train_skill_from_experience(
                control,
                EXPERIENCE_FIXTURE,
                skill_slug="react-engineering-from-experience",
            )
            self.assertTrue(paths["skill_md"].is_file())
            self.assertTrue(paths["capability_yaml"].is_file())
            body = paths["skill_md"].read_text(encoding="utf-8")
            self.assertIn("exp-fixture-contact-counter", body)


if __name__ == "__main__":
    unittest.main()
