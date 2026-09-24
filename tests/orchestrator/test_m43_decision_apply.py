"""M43 DecisionProvider ranking apply — hermetic unit + resolve integration tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.matcher.score import RankedSkill
from orchestrator.providers.decision.apply import (
    DEFAULT_CONF_MIN,
    DEFAULT_NOUL_MIN,
    apply_skill_rankings,
    decision_apply_enabled,
    decision_conf_min,
    decision_noul_min,
    extract_apply_gates,
    pad_with_matcher,
)
from orchestrator.providers.decision.shadow import (
    EVIDENCE_ROOT_M43,
    run_decision_provider_pass,
)
from orchestrator.providers.decision.types import RankedSuggestion, SkillSuggestionResult
from orchestrator.resolver.resolve import resolve_capabilities, resolve_to_dict

ROOT = Path(__file__).resolve().parents[2]


def _high_conf_result(**overrides) -> SkillSuggestionResult:
    base = SkillSuggestionResult(
        provider="file",
        model_id="jev-1.13.0",
        ranked=[
            RankedSuggestion("react-engineering", 0.82, confidence=0.71),
            RankedSuggestion("accessibility-review", 0.61, confidence=0.55),
            RankedSuggestion("testing-validation", 0.44, confidence=0.40),
        ],
        suggested_skill_id="react-engineering",
        abstain=False,
        raw_answers={
            "needs_skill": {"type": "noul", "noul": 0.91},
            "which_skill": {
                "type": "choice",
                "choice": "react-engineering",
                "confidence": 0.71,
            },
        },
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


class ApplyEnvTests(unittest.TestCase):
    def test_apply_default_off(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_DECISION_APPLY", None)
            self.assertFalse(decision_apply_enabled())

    def test_threshold_defaults(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_DECISION_NOUL_MIN", None)
            os.environ.pop("COMPASS_DECISION_CONF_MIN", None)
            self.assertEqual(decision_noul_min(), DEFAULT_NOUL_MIN)
            self.assertEqual(decision_conf_min(), DEFAULT_CONF_MIN)

    def test_threshold_env_override(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"COMPASS_DECISION_NOUL_MIN": "0.8", "COMPASS_DECISION_CONF_MIN": "0.5"},
        ):
            self.assertEqual(decision_noul_min(), 0.8)
            self.assertEqual(decision_conf_min(), 0.5)


class ApplyPolicyTests(unittest.TestCase):
    def test_pad_with_matcher(self) -> None:
        eligible = {"a", "b", "c", "d"}
        out = pad_with_matcher(["b"], ["a", "b", "c"], eligible_ids=eligible, top_n=3)
        self.assertEqual(out, ["b", "a", "c"])

    def test_apply_high_confidence_reorders(self) -> None:
        matcher = ["testing-validation", "react-engineering", "accessibility-review"]
        eligible = set(matcher)
        result = _high_conf_result()
        decision = apply_skill_rankings(
            matcher, result, eligible_ids=eligible, top_n=3
        )
        self.assertTrue(decision.applied)
        self.assertEqual(decision.recommended_skill_ids[0], "react-engineering")
        self.assertEqual(set(decision.recommended_skill_ids), set(matcher))
        self.assertTrue(all(sid in eligible for sid in decision.recommended_skill_ids))

    def test_low_noul_fail_closed(self) -> None:
        matcher = ["testing-validation", "react-engineering"]
        result = _high_conf_result(
            raw_answers={
                "needs_skill": {"type": "noul", "noul": 0.5},
                "which_skill": {"type": "choice", "confidence": 0.9},
            }
        )
        decision = apply_skill_rankings(
            matcher, result, eligible_ids=set(matcher), top_n=2
        )
        self.assertFalse(decision.applied)
        self.assertEqual(decision.recommended_skill_ids, matcher)
        self.assertIn("noul_below_floor", decision.reason)

    def test_low_confidence_fail_closed(self) -> None:
        matcher = ["testing-validation", "react-engineering"]
        result = _high_conf_result(
            raw_answers={
                "needs_skill": {"type": "noul", "noul": 0.95},
                "which_skill": {"type": "choice", "confidence": 0.4},
            }
        )
        decision = apply_skill_rankings(
            matcher, result, eligible_ids=set(matcher), top_n=2
        )
        self.assertFalse(decision.applied)
        self.assertIn("confidence_below_floor", decision.reason)

    def test_abstain_fail_closed(self) -> None:
        matcher = ["a", "b"]
        result = SkillSuggestionResult(
            provider="file",
            model_id="jev-1.13.0",
            abstain=True,
            abstain_reason="no fit",
        )
        decision = apply_skill_rankings(
            matcher, result, eligible_ids=set(matcher), top_n=2
        )
        self.assertFalse(decision.applied)
        self.assertEqual(decision.recommended_skill_ids, matcher)

    def test_stub_fail_closed(self) -> None:
        matcher = ["a"]
        result = SkillSuggestionResult(provider="stub", model_id=None, abstain=True)
        decision = apply_skill_rankings(
            matcher, result, eligible_ids={"a"}, top_n=1
        )
        self.assertFalse(decision.applied)
        self.assertEqual(decision.reason, "stub_provider")

    def test_oor_ids_dropped_then_pad(self) -> None:
        matcher = ["react-engineering", "testing-validation"]
        eligible = set(matcher)
        result = _high_conf_result(
            ranked=[
                RankedSuggestion("evil-skill", 0.99, confidence=0.99),
                RankedSuggestion("react-engineering", 0.82, confidence=0.71),
            ],
            suggested_skill_id="evil-skill",
        )
        decision = apply_skill_rankings(
            matcher, result, eligible_ids=eligible, top_n=2
        )
        self.assertNotIn("evil-skill", decision.recommended_skill_ids)
        self.assertTrue(all(sid in eligible for sid in decision.recommended_skill_ids))

    def test_identical_to_matcher_not_marked_applied(self) -> None:
        matcher = ["react-engineering", "accessibility-review", "testing-validation"]
        result = _high_conf_result()
        decision = apply_skill_rankings(
            matcher, result, eligible_ids=set(matcher), top_n=3
        )
        self.assertEqual(decision.recommended_skill_ids, matcher)
        self.assertFalse(decision.applied)
        self.assertEqual(decision.reason, "identical_to_matcher")

    def test_extract_gates(self) -> None:
        noul, conf = extract_apply_gates(_high_conf_result())
        self.assertEqual(noul, 0.91)
        self.assertEqual(conf, 0.71)


class ApplyResolveIntegrationTests(unittest.TestCase):
    def test_default_apply_off_stable(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_DECISION_PROVIDER": "stub",
                "COMPASS_DECISION_SHADOW": "",
                "COMPASS_DECISION_APPLY": "",
            },
            clear=False,
        ):
            os.environ.pop("COMPASS_DECISION_APPLY", None)
            os.environ.pop("COMPASS_DECISION_SHADOW", None)
            first = resolve_to_dict(ROOT, "Build accessible forms with React")
            second = resolve_to_dict(ROOT, "Build accessible forms with React")
        self.assertEqual(first["recommended_skill_ids"], second["recommended_skill_ids"])
        self.assertNotIn("decision_shadow", first)

    def test_shadow_only_still_non_mutating(self) -> None:
        baseline = resolve_to_dict(ROOT, "Build accessible forms with React")
        baseline_ids = list(baseline["recommended_skill_ids"])
        env = {
            "COMPASS_DECISION_PROVIDER": "file",
            "COMPASS_DECISION_SHADOW": "1",
            "COMPASS_DECISION_APPLY": "",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            os.environ.pop("COMPASS_DECISION_APPLY", None)
            shadowed = resolve_capabilities(
                ROOT,
                "Build accessible forms with React",
                plan_id="m43-shadow-regression",
            )
        self.assertEqual(shadowed.recommended_skill_ids, baseline_ids)
        self.assertIsNotNone(shadowed.decision_shadow)
        assert shadowed.decision_shadow is not None
        self.assertFalse(shadowed.decision_shadow.get("applied"))
        evidence_path = ROOT / shadowed.decision_shadow["evidence_path"]
        if evidence_path.is_file():
            evidence_path.unlink(missing_ok=True)
            try:
                evidence_path.parent.rmdir()
            except OSError:
                pass

    def test_apply_file_may_change_rankings_and_writes_m43_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            # Copy is heavy; use ROOT registry via resolve but redirect evidence
            # by running the pass helper with a temp root for evidence writes.
            baseline = resolve_to_dict(ROOT, "Build accessible forms with React")
            matcher_ids = list(baseline["recommended_skill_ids"])
            eligible = [
                {"id": sid, "name": sid, "description": "accessible forms"}
                for sid in matcher_ids
            ]
            # Ensure react-engineering is eligible even if not in top_n matcher list
            if "react-engineering" not in {e["id"] for e in eligible}:
                eligible.append(
                    {
                        "id": "react-engineering",
                        "name": "React",
                        "description": "accessible forms",
                    }
                )
            if "accessibility-review" not in {e["id"] for e in eligible}:
                eligible.append(
                    {
                        "id": "accessibility-review",
                        "name": "A11y",
                        "description": "accessible forms",
                    }
                )
            ranked = [RankedSkill(sid, 1.0 - i * 0.1, []) for i, sid in enumerate(matcher_ids)]
            env = {
                "COMPASS_DECISION_PROVIDER": "file",
                "COMPASS_DECISION_APPLY": "1",
            }
            with mock.patch.dict(os.environ, env):
                final_ids, ref = run_decision_provider_pass(
                    repo,
                    objective="Build accessible forms with React",
                    eligible_skills=eligible,
                    matcher_ranked=ranked,
                    recommended_skill_ids=list(matcher_ids),
                    top_n=len(matcher_ids) or 5,
                    plan_id="m43-apply-test",
                )
            self.assertIsNotNone(ref)
            assert ref is not None
            self.assertTrue(str(ref["evidence_path"]).startswith(str(EVIDENCE_ROOT_M43)))
            evidence = repo / ref["evidence_path"]
            self.assertTrue(evidence.is_file())
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "northstar.decision_apply.v1")
            self.assertIn("COMPASS_DECISION_APPLY", payload["env"])
            # When fixture order differs from matcher, applied should be true.
            if final_ids != matcher_ids:
                self.assertTrue(ref["applied"])
                self.assertTrue(payload["applied"])
            self.assertTrue(all(sid in {e["id"] for e in eligible} for sid in final_ids))

    def test_apply_implies_shadow_without_shadow_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            eligible = [
                {"id": "react-engineering", "name": "React", "description": "accessible forms"},
                {"id": "testing-validation", "name": "Test", "description": "tests"},
            ]
            ranked = [
                RankedSkill("testing-validation", 0.9, []),
                RankedSkill("react-engineering", 0.5, []),
            ]
            matcher = ["testing-validation", "react-engineering"]
            with mock.patch.dict(
                os.environ,
                {
                    "COMPASS_DECISION_PROVIDER": "file",
                    "COMPASS_DECISION_APPLY": "1",
                    "COMPASS_DECISION_SHADOW": "",
                },
            ):
                os.environ.pop("COMPASS_DECISION_SHADOW", None)
                _final, ref = run_decision_provider_pass(
                    repo,
                    objective="Build accessible forms",
                    eligible_skills=eligible,
                    matcher_ranked=ranked,
                    recommended_skill_ids=matcher,
                    top_n=2,
                )
            self.assertIsNotNone(ref)
            assert ref is not None
            self.assertTrue((repo / ref["evidence_path"]).is_file())


class CiApplyUnsetTests(unittest.TestCase):
    def test_ci_workflow_does_not_enable_apply(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertNotIn("COMPASS_DECISION_APPLY", workflow)


if __name__ == "__main__":
    unittest.main()
