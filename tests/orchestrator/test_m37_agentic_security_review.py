"""M37 — Agentic-equivalent fail-closed hook detectors in security specialist."""

from __future__ import annotations

import unittest
from pathlib import Path

from orchestrator.review.specialists import (
    compose_specialist_candidates,
    emit_security_candidates,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "code-review"


class FailClosedHookDetectorTests(unittest.TestCase):
    def test_plan_self_serve_fixture_emits_medium(self) -> None:
        diff = (FIXTURES / "hook-plan-self-serve.diff").read_text(encoding="utf-8")
        detection = {
            "changed_paths": [".cursor/hooks/plan-approval-check.sh"],
            "domains": ["security", "hooks"],
            "intent": {"excerpt": "Install NorthStar hooks", "non_goals": []},
        }
        findings = emit_security_candidates(
            detection=detection, context_pack={"diff": diff}
        )
        by_id = {f["id"]: f for f in findings}
        self.assertIn("sec-hook-plan-self-serve", by_id)
        self.assertEqual(by_id["sec-hook-plan-self-serve"]["severity"], "medium")
        self.assertEqual(by_id["sec-hook-plan-self-serve"]["category"], "fail-closed-control")
        self.assertIn("COMPASS_CAPTAIN_APPROVE", by_id["sec-hook-plan-self-serve"]["detail"])

    def test_protected_branch_bypass_fixture_emits_mediums(self) -> None:
        diff = (FIXTURES / "hook-protected-branch-bypass.diff").read_text(
            encoding="utf-8"
        )
        detection = {
            "changed_paths": [".cursor/hooks/protected-branch.sh"],
            "domains": ["security", "hooks"],
            "intent": {"excerpt": "", "non_goals": []},
        }
        findings = emit_security_candidates(
            detection=detection, context_pack={"diff": diff}
        )
        ids = {f["id"] for f in findings}
        self.assertIn("sec-hook-checkout-shortcircuit", ids)
        self.assertIn("sec-hook-push-refspec-gap", ids)
        self.assertIn("sec-hook-git-c-gap", ids)
        for fid in (
            "sec-hook-checkout-shortcircuit",
            "sec-hook-push-refspec-gap",
            "sec-hook-git-c-gap",
        ):
            row = next(f for f in findings if f["id"] == fid)
            self.assertEqual(row["severity"], "medium")
            self.assertEqual(row["skill"], "security-review")

    def test_hardened_m36_hooks_do_not_self_serve_or_shortcircuit(self) -> None:
        """Current control hooks after M36 should not trip the vulnerable patterns."""
        plan = (ROOT / ".cursor" / "hooks" / "plan-approval-check.sh").read_text(
            encoding="utf-8"
        )
        protected = (ROOT / ".cursor" / "hooks" / "protected-branch.sh").read_text(
            encoding="utf-8"
        )
        # Synthesize an "add everything" diff of the hardened scripts
        plan_diff = "diff --git a/.cursor/hooks/plan-approval-check.sh b/.cursor/hooks/plan-approval-check.sh\n" + "\n".join(
            f"+{line}" for line in plan.splitlines()
        )
        prot_diff = "diff --git a/.cursor/hooks/protected-branch.sh b/.cursor/hooks/protected-branch.sh\n" + "\n".join(
            f"+{line}" for line in protected.splitlines()
        )
        plan_findings = emit_security_candidates(
            detection={"changed_paths": [".cursor/hooks/plan-approval-check.sh"]},
            context_pack={"diff": plan_diff},
        )
        prot_findings = emit_security_candidates(
            detection={"changed_paths": [".cursor/hooks/protected-branch.sh"]},
            context_pack={"diff": prot_diff},
        )
        self.assertNotIn(
            "sec-hook-plan-self-serve", {f["id"] for f in plan_findings}
        )
        prot_ids = {f["id"] for f in prot_findings}
        self.assertNotIn("sec-hook-checkout-shortcircuit", prot_ids)
        self.assertNotIn("sec-hook-push-refspec-gap", prot_ids)
        self.assertNotIn("sec-hook-git-c-gap", prot_ids)

    def test_compose_includes_security_skill_for_hook_diff(self) -> None:
        diff = (FIXTURES / "hook-plan-self-serve.diff").read_text(encoding="utf-8")
        candidates, skills, source = compose_specialist_candidates(
            detection={
                "changed_paths": [".cursor/hooks/plan-approval-check.sh"],
                "intent": {},
            },
            context_pack={"diff": diff},
        )
        self.assertEqual(source, "specialists")
        self.assertIn("security-review", skills)
        self.assertIn("sec-hook-plan-self-serve", {c["id"] for c in candidates})


if __name__ == "__main__":
    unittest.main()
