"""M41 DecisionProvider — stub/file/jev + shadow skill suggestion."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.providers.decision import StubDecisionProvider
from orchestrator.providers.decision.file_provider import (
    FileDecisionProvider,
    decision_shadow_enabled,
    select_decision_provider,
)
from orchestrator.providers.decision.jev_provider import JevDecisionProvider, resolve_pinned_model_id
from orchestrator.providers.decision.shadow import (
    disagreement_list,
    maybe_run_decision_shadow,
    write_shadow_evidence,
)
from orchestrator.providers.decision.state import assert_state_safe, build_compact_state, redact_text
from orchestrator.providers.decision.types import (
    PINNED_JEV_MODEL_ID,
    RankedSuggestion,
    SkillSuggestionRequest,
    SkillSuggestionResult,
    EligibleSkillSummary,
)
from orchestrator.matcher.score import RankedSkill
from orchestrator.resolver.resolve import resolve_capabilities, resolve_to_dict


class StateRedactionTests(unittest.TestCase):
    def test_redact_secret_shaped_text(self) -> None:
        text = redact_text("Authorization: Bearer abcdefghijklmnop and api_key=supersecret")
        self.assertIn("[REDACTED]", text)
        self.assertNotIn("supersecret", text)

    def test_forbidden_keys_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            assert_state_safe({"objective": "x", "diff": "+++ secret"})

    def test_nested_forbidden_keys_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            assert_state_safe(
                {"objective": "ok", "eligible_skills": [{"diff": "+++ bad"}]}
            )
    def test_build_compact_state_hashes_roster(self) -> None:
        skills = [
            {"id": "b-skill", "name": "B", "description": "beta"},
            {"id": "a-skill", "name": "A", "description": "alpha"},
        ]
        _obj, summaries, roster_hash, state = build_compact_state("do the thing", skills)
        self.assertEqual([s.skill_id for s in summaries], ["a-skill", "b-skill"])
        self.assertEqual(len(roster_hash), 64)
        self.assertEqual(state["roster_hash"], roster_hash)


class SelectorTests(unittest.TestCase):
    def test_default_is_stub(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_DECISION_PROVIDER", None)
            provider = select_decision_provider(ROOT)
            self.assertIsInstance(provider, StubDecisionProvider)

    def test_unknown_provider_fails_closed_to_stub(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_DECISION_PROVIDER": "not-a-real-backend"}):
            provider = select_decision_provider(ROOT)
            self.assertIsInstance(provider, StubDecisionProvider)

    def test_file_provider(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_DECISION_PROVIDER": "file"}):
            provider = select_decision_provider(ROOT)
            self.assertIsInstance(provider, FileDecisionProvider)

    def test_shadow_flag(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_DECISION_SHADOW": "1"}):
            self.assertTrue(decision_shadow_enabled())
        with mock.patch.dict(os.environ, {"COMPASS_DECISION_SHADOW": "0"}):
            self.assertFalse(decision_shadow_enabled())


class FileProviderTests(unittest.TestCase):
    def test_accessible_forms_fixture(self) -> None:
        provider = FileDecisionProvider()
        summaries = [
            EligibleSkillSummary("react-engineering", "React", "forms"),
            EligibleSkillSummary("accessibility-review", "A11y", "review"),
            EligibleSkillSummary("testing-validation", "Test", "tests"),
        ]
        request = SkillSuggestionRequest(
            objective="Build accessible forms in React",
            eligible_skills=summaries,
            roster_hash="abc",
        )
        result = provider.suggest_skills(request)
        self.assertFalse(result.abstain)
        self.assertEqual(result.suggested_skill_id, "react-engineering")
        self.assertEqual(result.ranked[0].skill_id, "react-engineering")

    def test_no_fit_fixture(self) -> None:
        provider = FileDecisionProvider()
        request = SkillSuggestionRequest(
            objective="no skill should match this gibberish xyzzy-plugh today",
            eligible_skills=[EligibleSkillSummary("react-engineering", "React", "ui")],
            roster_hash="abc",
        )
        result = provider.suggest_skills(request)
        self.assertTrue(result.abstain)
        self.assertIsNone(result.suggested_skill_id)


class JevProviderTests(unittest.TestCase):
    def test_refuses_alias_model_ids(self) -> None:
        with self.assertRaises(ValueError):
            resolve_pinned_model_id("jev-latest")
        with self.assertRaises(ValueError):
            resolve_pinned_model_id("jev-preview")
        with self.assertRaises(ValueError):
            resolve_pinned_model_id("jev_latest")
        with self.assertRaises(ValueError):
            resolve_pinned_model_id("jev-1.99.0")

    def test_empty_model_id_refused(self) -> None:
        with self.assertRaises(ValueError):
            resolve_pinned_model_id("")

    def test_out_of_roster_choice_abstains(self) -> None:
        def fake_post(url: str, headers: dict, body: bytes, timeout: float) -> bytes:
            del url, headers, timeout
            payload = json.loads(body.decode("utf-8"))
            if "which_skill" in payload["questions"]:
                return json.dumps(
                    {
                        "model": PINNED_JEV_MODEL_ID,
                        "answers": {
                            "needs_skill": {"type": "noul", "noul": 0.95},
                            "which_skill": {
                                "type": "choice",
                                "choice": "evil-injected-skill",
                                "probabilities": {
                                    "evil-injected-skill": 0.9,
                                    "react-engineering": 0.1,
                                },
                                "confidence": 0.8,
                            },
                        },
                        "usage": {"input_tokens": 1, "output_tokens": 1},
                    }
                ).encode("utf-8")
            raise AssertionError("recheck should not run after out_of_roster")

        provider = JevDecisionProvider(
            api_key="test-key",
            model_id=PINNED_JEV_MODEL_ID,
            http_post=fake_post,
        )
        request = SkillSuggestionRequest(
            objective="accessible React forms",
            eligible_skills=[EligibleSkillSummary("react-engineering", "React", "forms")],
            roster_hash="hash",
        )
        result = provider.suggest_skills(request)
        self.assertTrue(result.abstain)
        self.assertEqual(result.abstain_reason, "out_of_roster")
        self.assertIsNone(result.suggested_skill_id)

    def test_two_pass_with_injected_http(self) -> None:
        calls: list[dict] = []

        def fake_post(url: str, headers: dict, body: bytes, timeout: float) -> bytes:
            del url, headers, timeout
            payload = json.loads(body.decode("utf-8"))
            calls.append(payload)
            self.assertEqual(payload["model"], PINNED_JEV_MODEL_ID)
            if "which_skill" in payload["questions"]:
                return json.dumps(
                    {
                        "model": PINNED_JEV_MODEL_ID,
                        "answers": {
                            "needs_skill": {"type": "noul", "noul": 0.92},
                            "which_skill": {
                                "type": "choice",
                                "choice": "react-engineering",
                                "probabilities": {
                                    "react-engineering": 0.7,
                                    "accessibility-review": 0.2,
                                    "none": 0.1,
                                },
                                "confidence": 0.6,
                            },
                        },
                        "usage": {"input_tokens": 10, "output_tokens": 2},
                    }
                ).encode("utf-8")
            return json.dumps(
                {
                    "model": PINNED_JEV_MODEL_ID,
                    "answers": {
                        "which_of_shortlist": {
                            "type": "choice",
                            "choice": "react-engineering",
                            "probabilities": {
                                "react-engineering": 0.8,
                                "accessibility-review": 0.15,
                                "none": 0.05,
                            },
                            "confidence": 0.7,
                        },
                        "top_fits": {"type": "noul", "noul": 0.88},
                    },
                    "usage": {"input_tokens": 12, "output_tokens": 3},
                }
            ).encode("utf-8")

        provider = JevDecisionProvider(
            api_key="test-key",
            model_id=PINNED_JEV_MODEL_ID,
            http_post=fake_post,
        )
        request = SkillSuggestionRequest(
            objective="accessible React forms",
            eligible_skills=[
                EligibleSkillSummary("react-engineering", "React", "forms"),
                EligibleSkillSummary("accessibility-review", "A11y", "a11y"),
            ],
            roster_hash="hash",
        )
        result = provider.suggest_skills(request)
        self.assertEqual(len(calls), 2)
        self.assertFalse(result.abstain)
        self.assertEqual(result.suggested_skill_id, "react-engineering")
        self.assertEqual(result.input_tokens, 22)

    def test_base_url_must_be_typesafe(self) -> None:
        provider = JevDecisionProvider(
            api_key="test-key",
            model_id=PINNED_JEV_MODEL_ID,
            base_url="https://evil.example/v1",
            http_post=lambda *a, **k: b"{}",
        )
        request = SkillSuggestionRequest(
            objective="x",
            eligible_skills=[EligibleSkillSummary("react-engineering", "React", "ui")],
            roster_hash="h",
        )
        result = provider.suggest_skills(request)
        self.assertTrue(result.abstain)
        self.assertIn("BASE_URL", (result.error or "").upper() + result.abstain_reason.upper())

    def test_error_abstains(self) -> None:
        def boom(*_args, **_kwargs):
            raise OSError("network down")

        provider = JevDecisionProvider(
            api_key="test-key",
            model_id=PINNED_JEV_MODEL_ID,
            http_post=boom,
        )
        request = SkillSuggestionRequest(
            objective="x",
            eligible_skills=[EligibleSkillSummary("react-engineering", "React", "ui")],
            roster_hash="h",
        )
        result = provider.suggest_skills(request)
        self.assertTrue(result.abstain)
        self.assertIsNotNone(result.error)


class ShadowTests(unittest.TestCase):
    def test_disagreement_list(self) -> None:
        diffs = disagreement_list(["a", "b"], ["a", "c"])
        self.assertEqual(diffs, [{"rank": 2, "matcher": "b", "provider": "c"}])

    def test_shadow_writes_evidence_only_and_does_not_mutate_rankings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            baseline = ["react-engineering", "testing-validation"]
            env = {
                "COMPASS_DECISION_PROVIDER": "file",
                "COMPASS_DECISION_SHADOW": "1",
            }
            with mock.patch.dict(os.environ, env):
                # Seed a minimal registry-like eligible list for file fixture.
                eligible = [
                    {
                        "id": "react-engineering",
                        "name": "React",
                        "description": "accessible forms",
                    },
                    {
                        "id": "accessibility-review",
                        "name": "A11y",
                        "description": "review",
                    },
                    {
                        "id": "testing-validation",
                        "name": "Test",
                        "description": "tests",
                    },
                ]
                ranked = [
                    RankedSkill("react-engineering", 0.9, []),
                    RankedSkill("testing-validation", 0.5, []),
                ]
                ref = maybe_run_decision_shadow(
                    repo,
                    objective="Build accessible forms",
                    eligible_skills=eligible,
                    matcher_ranked=ranked,
                    recommended_skill_ids=list(baseline),
                    top_n=2,
                    plan_id="m41-test",
                )
            self.assertIsNotNone(ref)
            assert ref is not None
            self.assertFalse(ref["applied"])
            evidence = repo / ref["evidence_path"]
            self.assertTrue(evidence.is_file())
            plans_dupes = list((repo / ".agent" / "plans").rglob("decision-shadow.json")) if (repo / ".agent" / "plans").exists() else []
            self.assertEqual(plans_dupes, [])
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            self.assertEqual(payload["matcher_ranking"], baseline)
            self.assertFalse(payload["applied"])
            # Original list unchanged
            self.assertEqual(baseline, ["react-engineering", "testing-validation"])


class ResolveShadowIntegrationTests(unittest.TestCase):
    def test_default_resolve_has_no_shadow_and_stable_rankings(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"COMPASS_DECISION_PROVIDER": "stub", "COMPASS_DECISION_SHADOW": ""},
            clear=False,
        ):
            os.environ.pop("COMPASS_DECISION_SHADOW", None)
            first = resolve_to_dict(ROOT, "Build accessible forms with React")
            second = resolve_to_dict(ROOT, "Build accessible forms with React")
        self.assertNotIn("decision_shadow", first)
        self.assertEqual(first["recommended_skill_ids"], second["recommended_skill_ids"])

    def test_shadow_file_does_not_change_recommended_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            # Minimal registry so resolve can load skills from ROOT via patching
            # is heavy; instead call maybe_run + compare to ROOT baseline resolve.
            baseline = resolve_to_dict(ROOT, "Build accessible forms with React")
            baseline_ids = list(baseline["recommended_skill_ids"])
            env = {
                "COMPASS_DECISION_PROVIDER": "file",
                "COMPASS_DECISION_SHADOW": "1",
            }
            with mock.patch.dict(os.environ, env):
                # Use ROOT registry but redirect evidence writes via a wrapper:
                shadowed = resolve_capabilities(
                    ROOT,
                    "Build accessible forms with React",
                    plan_id="m41-jev-decision-service",
                )
            self.assertEqual(shadowed.recommended_skill_ids, baseline_ids)
            self.assertIsNotNone(shadowed.decision_shadow)
            assert shadowed.decision_shadow is not None
            self.assertFalse(shadowed.decision_shadow.get("applied"))
            evidence_path = ROOT / shadowed.decision_shadow["evidence_path"]
            self.assertTrue(evidence_path.is_file())
            payload = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "northstar.decision_shadow.v1")
            self.assertEqual(payload["matcher_ranking"], baseline_ids)
            # Cleanup evidence written into the control repo during the test.
            evidence_path.unlink(missing_ok=True)
            try:
                evidence_path.parent.rmdir()
            except OSError:
                pass
            del repo


class EvalHarnessTests(unittest.TestCase):
    def test_file_provider_eval_report_metrics(self) -> None:
        from orchestrator.providers.decision.eval import (
            evaluate_file_provider,
            write_eval_report,
        )

        report = evaluate_file_provider()
        self.assertEqual(report["schema"], "northstar.decision_eval.v1")
        metrics = report["metrics"]
        for key in (
            "wrong_skill_loads",
            "unnecessary_skill_loads",
            "missed_useful_skills",
            "disagreement_rate",
            "latency_ms",
            "cost_usd",
        ):
            self.assertIn(key, metrics)
        self.assertEqual(metrics["latency_ms"], 0)
        self.assertEqual(metrics["cost_usd"], 0)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_eval_report(Path(tmp), report)
            self.assertTrue(path.is_file())
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["metrics"]["latency_ms"], 0)


class Ws0SkillSlugTests(unittest.TestCase):
    def test_skugs_include_former_drift_skills(self) -> None:
        from orchestrator.registry.compiler import SKILL_SLUGS

        self.assertIn("code-reviewer", SKILL_SLUGS)
        self.assertIn("northstar-connected-routine", SKILL_SLUGS)


if __name__ == "__main__":
    unittest.main()
