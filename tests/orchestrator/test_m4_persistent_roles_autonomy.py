"""M4 persistent-role promotion and bounded Level 3 weight apply tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.agents.proficiency import (
    build_proficiency_record,
    write_proficiency_record,
)
from orchestrator.agents.promote import (
    PromotionProposeError,
    build_persistent_role_proposal,
    write_persistent_role_proposal,
)
from orchestrator.assembler.affinity import resolve_reference_profile
from orchestrator.assembler.manifest import build_manifest_for_task
from orchestrator.matcher.score import (
    DEFAULT_WEIGHTS,
    WEIGHTS,
    get_weights,
    load_weights,
    rank_skills,
)
from orchestrator.routing.apply import ApplyError, apply_routing_proposal
from orchestrator.routing.propose import build_routing_proposal, load_experiences
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
EXPERIENCE_FIXTURE = ROOT / "tests" / "fixtures" / "experience" / "contact-counter.json"


class WeightsLoaderTests(unittest.TestCase):
    def test_default_weights_match_historical(self) -> None:
        self.assertEqual(DEFAULT_WEIGHTS, dict(WEIGHTS))
        self.assertEqual(get_weights(), DEFAULT_WEIGHTS)
        loaded = load_weights(ROOT / "orchestrator" / "matcher" / "weights.json")
        self.assertEqual(loaded, DEFAULT_WEIGHTS)

    def test_rankings_stable_under_default_weights(self) -> None:
        skills = [
            {
                "id": "capability-planning",
                "kind": "skill",
                "lifecycle_stage": "AVAILABLE_SKILL",
                "capabilities_provided": ["capability-planning"],
                "compatible_stacks": ["any"],
                "agent_affinity": ["architecture-agent"],
            },
            {
                "id": "testing-validation",
                "kind": "skill",
                "lifecycle_stage": "AVAILABLE_SKILL",
                "capabilities_provided": ["testing-validation"],
                "compatible_stacks": ["any"],
                "agent_affinity": ["test-engineer"],
            },
        ]
        a = [r.skill_id for r in rank_skills(skills, ["capability-planning"])]
        b = [r.skill_id for r in rank_skills(skills, ["capability-planning"])]
        self.assertEqual(a, b)


class PersistentRoleTests(unittest.TestCase):
    def test_propose_writes_staging_not_cursor_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            record = build_proficiency_record(
                agent_id="compass-evaluator",
                classifications=["evaluation", "arbitration"],
                proficiency_level="proficient",
                experience_ids=["exp-test-1"],
                skills_trained=["compass-evaluator"],
                captain_approved=True,
            )
            write_proficiency_record(repo, record)
            proposal = build_persistent_role_proposal(record)
            path = write_persistent_role_proposal(repo, proposal, record)
            self.assertTrue(path.is_file())
            written = json.loads(path.read_text(encoding="utf-8"))
            validate_document(written, "persistent-role-promotion.schema.json")
            staging_md = repo / written["staging_paths"]["agent_markdown"]
            staging_profile = repo / written["staging_paths"]["reference_profile"]
            self.assertTrue(staging_md.is_file())
            self.assertTrue(staging_profile.is_file())
            self.assertFalse((repo / ".cursor" / "agents" / "compass-evaluator.md").exists())

    def test_gates_reject_developing(self) -> None:
        record = build_proficiency_record(
            agent_id="compass-evaluator",
            classifications=["evaluation"],
            proficiency_level="developing",
            experience_ids=["exp-1"],
            captain_approved=True,
        )
        with self.assertRaises(PromotionProposeError):
            build_persistent_role_proposal(record)


class AssemblerAffinityTests(unittest.TestCase):
    def test_prefers_approved_proficient_agent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            # Mirror a live reference profile path expected by affinity resolver
            profile_dir = repo / "orchestrator" / "reference-profiles"
            profile_dir.mkdir(parents=True)
            (profile_dir / "compass-evaluator.json").write_text(
                json.dumps({"id": "compass-evaluator"}), encoding="utf-8"
            )
            record = build_proficiency_record(
                agent_id="compass-evaluator",
                classifications=["evaluation", "arbitration"],
                proficiency_level="expert",
                experience_ids=["exp-1"],
                captain_approved=True,
            )
            write_proficiency_record(repo, record)
            chosen, notes = resolve_reference_profile(
                {"id": "task-validation"}, repo
            )
            self.assertEqual(chosen, "compass-evaluator")
            self.assertTrue(
                any(n.get("factor") == "persistent_role_preference" for n in notes)
            )


class BoundedApplyTests(unittest.TestCase):
    def test_rejects_without_captain_flag(self) -> None:
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        proposal = build_routing_proposal(experiences)
        self.assertFalse(proposal.get("captain_approved"))
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            prop_path = repo / "proposal.json"
            prop_path.write_text(json.dumps(proposal), encoding="utf-8")
            weights = repo / "weights.json"
            weights.write_text(json.dumps(DEFAULT_WEIGHTS), encoding="utf-8")
            with self.assertRaises(ApplyError):
                apply_routing_proposal(
                    repo,
                    prop_path,
                    weights_path=weights,
                    run_eval_gate=False,
                )

    def test_applies_with_captain_flag_and_budget(self) -> None:
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        proposal = build_routing_proposal(experiences)
        proposal["captain_approved"] = True
        # Tiny intentional delta still valid
        proposal["matcher_weight_suggestions"] = {
            **DEFAULT_WEIGHTS,
            "capability_overlap": 0.44,
            "stack_match": 0.21,
        }
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            prop_path = repo / "proposal.json"
            prop_path.write_text(json.dumps(proposal), encoding="utf-8")
            weights = repo / "weights.json"
            weights.write_text(json.dumps(DEFAULT_WEIGHTS), encoding="utf-8")
            budget = repo / "budget.md"
            budget.write_text(
                "- Maximum weight-apply operations per plan: 3\n"
                "- Weight-apply operations used: 0\n",
                encoding="utf-8",
            )
            result = apply_routing_proposal(
                repo,
                prop_path,
                budget_path=budget,
                weights_path=weights,
                run_eval_gate=False,
            )
            applied = json.loads(weights.read_text(encoding="utf-8"))
            self.assertEqual(applied["capability_overlap"], 0.44)
            self.assertTrue(Path(result["audit_path"]).is_file())
            self.assertIn("Weight-apply operations used: 1", budget.read_text(encoding="utf-8"))


class ManifestAffinityIntegrationTests(unittest.TestCase):
    def test_manifest_includes_affinity_notes(self) -> None:
        skills = [
            {
                "id": "testing-validation",
                "kind": "skill",
                "lifecycle_stage": "AVAILABLE_SKILL",
                "capabilities_provided": ["testing-validation"],
                "compatible_stacks": ["any"],
                "agent_affinity": ["test-engineer", "compass-evaluator"],
            }
        ]
        manifest = build_manifest_for_task(
            {
                "id": "task-validation",
                "required_capabilities": ["testing-validation"],
            },
            skills,
            stacks=["any"],
            security_sensitive=False,
            plan_id="m4-test",
            repo_root=None,
        )
        self.assertEqual(manifest["reference_profile"], "test-engineer")
        factors = [item.get("factor") for item in manifest.get("scoring_breakdown") or []]
        self.assertIn("reference_profile_default", factors)


if __name__ == "__main__":
    unittest.main()
