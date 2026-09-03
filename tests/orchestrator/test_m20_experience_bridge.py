"""M20 experience bridge + Captain-gated improvement apply tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.learning.apply_improvement import (
    ImprovementApplyError,
    apply_skill_improvement_proposal,
)
from orchestrator.learning.experience_bridge import (
    ExperienceBridgeError,
    bridge_learning_run_to_experiences,
    promote_proven_from_bridge,
)
from orchestrator.learning.loop import run_skill_learning_loop
from orchestrator.promotion.advance import count_successful_experiences_for_skill
from orchestrator.telemetry.record import record_workstream

ROOT = Path(__file__).resolve().parents[2]


class M20ExperienceBridgeTests(unittest.TestCase):
    def test_bridge_records_experiences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report = run_skill_learning_loop(
                repo,
                objective="accessible react forms",
                source="fixtures",
                top_n=1,
                control_root=ROOT,
                record_experiences=True,
            )
            bridge = report.get("experience_bridge") or {}
            self.assertEqual(bridge.get("kind"), "skill-learning-experience-bridge")
            self.assertGreaterEqual(bridge.get("count") or 0, 1)
            exp_path = Path(bridge["records"][0]["experience"])
            self.assertTrue(exp_path.is_file())
            exp = json.loads(exp_path.read_text(encoding="utf-8"))
            self.assertEqual(exp["outcome"], "success")
            self.assertIn("skill-learning-loop", exp["skills_used"])

    def test_bridge_rejects_non_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nope.json"
            path.write_text(json.dumps({"kind": "other"}), encoding="utf-8")
            with self.assertRaises(ExperienceBridgeError):
                bridge_learning_run_to_experiences(Path(tmp), path)

    def test_proven_requires_captain_and_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            report = run_skill_learning_loop(
                repo,
                objective="accessible react forms",
                source="fixtures",
                top_n=1,
                control_root=ROOT,
                record_experiences=True,
            )
            entry = report["results"][0]
            staging = Path(entry["harness"]["staging_candidate"])
            slug = str(entry.get("target_skill_slug") or entry.get("skill_slug"))
            with self.assertRaises(ExperienceBridgeError):
                promote_proven_from_bridge(
                    repo,
                    candidate_path=staging,
                    skill_slug=slug,
                    evidence_paths=["e.md"],
                    captain_approved=False,
                )
            with self.assertRaises(ExperienceBridgeError):
                promote_proven_from_bridge(
                    repo,
                    candidate_path=staging,
                    skill_slug=slug,
                    evidence_paths=["e.md"],
                    captain_approved=True,
                )
            record_workstream(
                repo,
                plan_id="extra-success",
                outcome="success",
                skills=[slug],
                source_instance="control-test",
            )
            self.assertGreaterEqual(
                count_successful_experiences_for_skill(repo, slug), 2
            )
            proven = promote_proven_from_bridge(
                repo,
                candidate_path=staging,
                skill_slug=slug,
                evidence_paths=["e.md"],
                captain_approved=True,
            )
            staged = json.loads(Path(proven).read_text(encoding="utf-8"))
            self.assertEqual(staged["lifecycle_stage"], "PROVEN_SKILL")
            self.assertIs(staged["approved_for_execution"], False)


class M20ImprovementApplyTests(unittest.TestCase):
    def _temp_control_with_skill(self, tmp: Path, slug: str = "react-engineering") -> Path:
        src = ROOT / ".cursor" / "skills" / slug / "SKILL.md"
        dest = tmp / ".cursor" / "skills" / slug
        dest.mkdir(parents=True)
        dest.joinpath("SKILL.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        dest.joinpath("capability.yaml").write_text(
            f"id: {slug}\nversion: \"1.0.0\"\nkind: skill\n"
            "source:\n  type: compass-skill\n"
            f"  path: .cursor/skills/{slug}/SKILL.md\n"
            "lifecycle_stage: AVAILABLE_SKILL\ncapabilities_provided:\n  - demo\n",
            encoding="utf-8",
        )
        return tmp

    def test_apply_requires_captain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            proposal = repo / "proposal.json"
            proposal.write_text(
                json.dumps(
                    {
                        "kind": "skill-improvement-proposal",
                        "target_skill_slug": "react-engineering",
                        "candidate_id": "c1",
                        "approved_for_execution": False,
                        "auto_apply": False,
                        "suggested_changes": [{"source_notes": "lesson"}],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ImprovementApplyError):
                apply_skill_improvement_proposal(
                    repo, proposal, captain_approved=False, control_root=ROOT
                )

    def test_apply_writes_draft_not_live_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            control = self._temp_control_with_skill(Path(tmp) / "control")
            repo = Path(tmp) / "repo"
            repo.mkdir()
            original = (
                control / ".cursor" / "skills" / "react-engineering" / "SKILL.md"
            ).read_text(encoding="utf-8")
            proposal = repo / "proposal.json"
            proposal.write_text(
                json.dumps(
                    {
                        "kind": "skill-improvement-proposal",
                        "target_skill_slug": "react-engineering",
                        "candidate_id": "github-stars-demo",
                        "approved_for_execution": False,
                        "auto_apply": False,
                        "star_category": "frontend-ui",
                        "similarity": 0.5,
                        "suggested_changes": [{"source_notes": "Fold accessible form patterns."}],
                    }
                ),
                encoding="utf-8",
            )
            result = apply_skill_improvement_proposal(
                repo,
                proposal,
                captain_approved=True,
                apply_live=False,
                control_root=control,
            )
            self.assertFalse(result["live_written"])
            draft = Path(result["draft_skill_md"])
            self.assertTrue(draft.is_file())
            self.assertIn("Learned from categorized Stars", draft.read_text(encoding="utf-8"))
            live = (control / ".cursor" / "skills" / "react-engineering" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(live, original)

    def test_apply_live_appends_with_captain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            control = self._temp_control_with_skill(Path(tmp) / "control")
            repo = Path(tmp) / "repo"
            repo.mkdir()
            proposal = repo / "proposal.json"
            proposal.write_text(
                json.dumps(
                    {
                        "kind": "skill-improvement-proposal",
                        "target_skill_slug": "react-engineering",
                        "candidate_id": "c-live",
                        "approved_for_execution": False,
                        "auto_apply": False,
                        "suggested_changes": [{"source_notes": "live lesson"}],
                    }
                ),
                encoding="utf-8",
            )
            result = apply_skill_improvement_proposal(
                repo,
                proposal,
                captain_approved=True,
                apply_live=True,
                control_root=control,
            )
            self.assertTrue(result["live_written"])
            live = (
                control / ".cursor" / "skills" / "react-engineering" / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn("compass-learned-from-stars:begin", live)
            self.assertIn("live lesson", live)

    def test_refuse_excluded_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            control = self._temp_control_with_skill(
                Path(tmp) / "control", slug="security-review"
            )
            repo = Path(tmp) / "repo"
            repo.mkdir()
            proposal = repo / "proposal.json"
            proposal.write_text(
                json.dumps(
                    {
                        "kind": "skill-improvement-proposal",
                        "target_skill_slug": "security-review",
                        "candidate_id": "c1",
                        "approved_for_execution": False,
                        "auto_apply": False,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ImprovementApplyError):
                apply_skill_improvement_proposal(
                    repo,
                    proposal,
                    captain_approved=True,
                    apply_live=True,
                    control_root=control,
                )


if __name__ == "__main__":
    unittest.main()
