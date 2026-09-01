"""M17 Stage 3 bounded autonomy — context selection + decomposition hints."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.matcher.score import DEFAULT_WEIGHTS, WEIGHTS, get_weights
from orchestrator.planning.context_selection import (
    ContextSelectionError,
    apply_context_selection_proposal,
    build_context_selection_proposal,
    default_context_profile,
    fetch_plan_context_slices,
    load_active_context_profile,
    write_active_context_profile,
    write_context_selection_proposal,
)
from orchestrator.routing.apply import ApplyError, apply_routing_proposal
from orchestrator.routing.decomposition import build_decomposition_hints, merge_decomposition_hints
from orchestrator.routing.propose import build_routing_proposal, load_experiences

ROOT = Path(__file__).resolve().parents[2]
EXPERIENCE_FIXTURE = ROOT / "tests" / "fixtures" / "experience" / "contact-counter.json"


class ContextSelectionTests(unittest.TestCase):
    def test_default_profile_slices(self) -> None:
        profile = default_context_profile()
        self.assertTrue(profile["slices"]["knowledge"]["enabled"])
        self.assertEqual(profile["slices"]["knowledge"]["top_n"], 5)

    def test_propose_and_apply_context_selection(self) -> None:
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        proposal = build_context_selection_proposal(experiences)
        self.assertEqual(proposal["kind"], "context-selection-proposal")
        self.assertFalse(proposal["auto_apply"])
        self.assertFalse(proposal.get("captain_approved"))

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_context_selection_proposal(repo, proposal)
            self.assertTrue(path.is_file())
            with self.assertRaises(ContextSelectionError):
                apply_context_selection_proposal(repo, path)

            proposal["captain_approved"] = True
            path.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
            result = apply_context_selection_proposal(repo, path)
            active = load_active_context_profile(repo)
            self.assertEqual(active["profile_id"], "experience-tuned")
            self.assertIn("audit_path", result)

    def test_fetch_slices_respects_disabled_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            profile = default_context_profile()
            profile["slices"]["artifact"]["enabled"] = False
            slices = fetch_plan_context_slices(repo, "matcher routing", profile=profile)
            self.assertEqual(slices["artifact_context"], [])

    def test_active_profile_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            profile = default_context_profile()
            profile["slices"]["artifact"]["enabled"] = False
            write_active_context_profile(repo, profile)
            loaded = load_active_context_profile(repo)
            self.assertFalse(loaded["slices"]["artifact"]["enabled"])


class DecompositionHintsTests(unittest.TestCase):
    def test_build_hints_from_success_experiences(self) -> None:
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        hints = build_decomposition_hints(experiences)
        self.assertTrue(hints)
        factors = {h["matcher_factor"] for h in hints}
        self.assertIn("capability_overlap", factors)

    def test_merge_hints_bounded(self) -> None:
        merged = merge_decomposition_hints(
            DEFAULT_WEIGHTS,
            [{"matcher_factor": "capability_overlap", "weight_delta": 0.5}],
        )
        self.assertLessEqual(
            merged["capability_overlap"] - DEFAULT_WEIGHTS["capability_overlap"],
            0.03,
        )

    def test_routing_proposal_includes_decomposition_hints(self) -> None:
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        proposal = build_routing_proposal(experiences)
        self.assertIn("decomposition_hints", proposal)
        self.assertGreater(
            proposal["matcher_weight_suggestions"]["capability_overlap"],
            WEIGHTS["capability_overlap"],
        )

    def test_apply_routing_with_hints(self) -> None:
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        proposal = build_routing_proposal(experiences)
        proposal["captain_approved"] = True
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            weights_path = repo / "weights.json"
            prop_path = repo / "proposal.json"
            prop_path.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
            before = dict(get_weights())
            result = apply_routing_proposal(
                repo,
                prop_path,
                weights_path=weights_path,
                run_eval_gate=False,
            )
            self.assertIn("audit_path", result)
            after = json.loads(weights_path.read_text(encoding="utf-8"))
            self.assertGreater(after["capability_overlap"], before["capability_overlap"])

    def test_apply_rejects_without_captain_flag(self) -> None:
        experiences = load_experiences([EXPERIENCE_FIXTURE])
        proposal = build_routing_proposal(experiences)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            prop_path = repo / "proposal.json"
            prop_path.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(ApplyError):
                apply_routing_proposal(repo, prop_path, run_eval_gate=False)


if __name__ == "__main__":
    unittest.main()
