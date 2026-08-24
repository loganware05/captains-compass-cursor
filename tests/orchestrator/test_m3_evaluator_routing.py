"""M3 evaluator, routing proposals, promotion ceiling, proficiency tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from orchestrator.agents.proficiency import (
    ProficiencyError,
    build_proficiency_record,
    write_proficiency_record,
)
from orchestrator.evaluator.record import record_evaluation
from orchestrator.matcher.score import WEIGHTS
from orchestrator.plan_writer.build import build_capability_plan
from orchestrator.plan_writer.render import render_capability_plan_sections
from orchestrator.promotion.advance import (
    CANDIDATE_CEILING,
    PromotionError,
    advance_lifecycle,
    load_candidate_json,
)
from orchestrator.routing.propose import (
    build_routing_proposal,
    load_experiences,
    write_routing_proposal,
)
from orchestrator.schemas.validate import validate_document

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


class EvaluationTests(unittest.TestCase):
    def test_record_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = record_evaluation(
                Path(tmp),
                plan_id="m3-test",
                objective="Compare A vs B",
                alternatives=[
                    {"id": "a", "label": "Option A", "score": 0.8},
                    {"id": "b", "label": "Option B", "score": 0.4},
                ],
                recommendation="Choose A",
                winner_alternative_id="a",
            )
            self.assertTrue(path.is_file())
            validate_document(
                __import__("json").loads(path.read_text(encoding="utf-8")),
                "evaluation.schema.json",
            )


class RoutingProposalTests(unittest.TestCase):
    def test_proposal_never_auto_applies(self) -> None:
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        proposal = build_routing_proposal(experiences)
        self.assertFalse(proposal["auto_apply"])
        self.assertEqual(proposal["matcher_weight_suggestions"], dict(WEIGHTS))
        self.assertFalse(proposal.get("captain_approved"))
        with tempfile.TemporaryDirectory() as tmp:
            path = write_routing_proposal(Path(tmp), proposal)
            self.assertTrue(path.is_file())

    def test_default_matcher_unchanged_by_proposal_build(self) -> None:
        before = dict(WEIGHTS)
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        build_routing_proposal(experiences)
        self.assertEqual(dict(WEIGHTS), before)


class PromotionCeilingTests(unittest.TestCase):
    def test_advances_to_sandbox_tested_with_evidence(self) -> None:
        candidate = load_candidate_json(FIXTURE_CANDIDATE)
        analyzed = advance_lifecycle(candidate, target_stage="ANALYZED")
        secured = advance_lifecycle(
            analyzed,
            target_stage="SECURITY_REVIEWED",
            evidence_paths=[".agent/evidence/security.md"],
        )
        self.assertEqual(secured["lifecycle_stage"], "SECURITY_REVIEWED")
        sandbox = advance_lifecycle(
            secured,
            target_stage="SANDBOX_TESTED",
            evidence_paths=[".agent/evidence/sandbox.md"],
        )
        self.assertEqual(sandbox["lifecycle_stage"], CANDIDATE_CEILING)
        self.assertFalse(sandbox["approved_for_execution"])

    def test_rejects_approved_stage(self) -> None:
        candidate = load_candidate_json(FIXTURE_CANDIDATE)
        with self.assertRaises(PromotionError):
            advance_lifecycle(candidate, target_stage="APPROVED")

    def test_security_requires_evidence(self) -> None:
        candidate = load_candidate_json(FIXTURE_CANDIDATE)
        analyzed = advance_lifecycle(candidate, target_stage="ANALYZED")
        with self.assertRaises(PromotionError):
            advance_lifecycle(analyzed, target_stage="SECURITY_REVIEWED")


class ProficiencyTests(unittest.TestCase):
    def test_writes_draft_without_captain_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            record = build_proficiency_record(
                agent_id="compass-evaluator",
                classifications=["evaluation"],
                proficiency_level="developing",
                skills_trained=["compass-evaluator"],
                captain_approved=False,
            )
            path = write_proficiency_record(Path(tmp), record)
            self.assertTrue(path.is_file())
            self.assertFalse(record["captain_approved"])

    def test_rejects_empty_classifications(self) -> None:
        with self.assertRaises(ProficiencyError):
            build_proficiency_record(agent_id="x", classifications=[])


class ExperienceSignalsPlanTests(unittest.TestCase):
    def test_plan_renders_experience_signals_without_changing_rankings(self) -> None:
        first = build_capability_plan(ROOT, "Build a React dashboard", plan_id="m3-sig-a")
        second = build_capability_plan(ROOT, "Build a React dashboard", plan_id="m3-sig-b")
        self.assertEqual(first.resolve["ranked_skills"], second.resolve["ranked_skills"])
        markdown = render_capability_plan_sections(first)
        self.assertIn("## Experience Signals", markdown)
        self.assertIn("Does not auto-adjust matcher weights", markdown)


if __name__ == "__main__":
    unittest.main()
