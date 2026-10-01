"""M47 Behavior Pattern Learning — hermetic proposal-only tests."""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from orchestrator.behavior.enabled import (
    behavior_learn_enabled,
    require_behavior_learn_enabled,
)
from orchestrator.behavior.ledger import build_behavior_evaluation, write_behavior_evaluation
from orchestrator.behavior.patterns.detect import detect_patterns, patterns_with_candidates
from orchestrator.behavior.patterns.quality import min_occurrence, polarity_for_signal
from orchestrator.behavior.patterns.service import (
    export_patterns_csv,
    list_learned_patterns,
    scan_and_persist,
    show_pattern,
)
from orchestrator.behavior.patterns.store import build_candidate, build_pattern, load_pattern
from orchestrator.behavior.signals import normalize_signals
from orchestrator.schemas.validate import ValidationError, validate_document


def _write_eval(
    repo: Path,
    *,
    evaluation_id: str,
    agent: str = "implementation-agent",
    skill_ids: list[str] | None = None,
    signals: dict[str, float] | None = None,
    abstain: bool = False,
) -> None:
    packet = {
        "execution_id": f"run-{evaluation_id}",
        "task_id": "t1",
        "plan_id": "p1",
        "agent": agent,
        "model": "coding-strong",
        "skill_ids": skill_ids if skill_ids is not None else ["testing-validation"],
        "repository_sha": "abc",
        "northstar_version": "1.47.0",
        "outcome": "success",
        "objective": "demo",
        "diff_meta": {},
        "evidence": [],
        "content_hash": f"hash-{evaluation_id}",
        "schema_version": "1",
    }
    record = build_behavior_evaluation(
        packet,
        signals=normalize_signals(signals or {"rework_required": 0.85}),
        provider="stub",
        model_id=None,
        evaluation_id=evaluation_id,
        abstain=abstain,
        abstain_reason="test" if abstain else "",
    )
    write_behavior_evaluation(repo, record)


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_BEHAVIOR_LEARN_ENABLED", None)
            self.assertFalse(behavior_learn_enabled())
            with self.assertRaises(PermissionError):
                require_behavior_learn_enabled()

    def test_enabled_truthy(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BEHAVIOR_LEARN_ENABLED": "1"}):
            self.assertTrue(behavior_learn_enabled())


class QualityTests(unittest.TestCase):
    def test_min_occurrence_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE", None)
            self.assertEqual(min_occurrence(), 3)

    def test_min_occurrence_override(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE": "2"}):
            self.assertEqual(min_occurrence(), 2)

    def test_polarity(self) -> None:
        self.assertEqual(polarity_for_signal("praise"), "positive")
        self.assertEqual(polarity_for_signal("rework_required"), "negative")


class SchemaTests(unittest.TestCase):
    def test_pattern_and_candidate_validate(self) -> None:
        pattern = build_pattern(
            signal="rework_required",
            polarity="negative",
            agent="implementation-agent",
            skill_id="testing-validation",
            evidence_evaluation_ids=["beval-a", "beval-b", "beval-c"],
            scores=[0.8, 0.9, 0.85],
            threshold=0.7,
            min_occurrence=3,
        )
        validate_document(pattern, "behavior-pattern.schema.json")
        self.assertFalse(pattern["authority_mutation"])
        candidate = build_candidate(pattern)
        validate_document(candidate, "behavior-candidate.schema.json")
        self.assertFalse(candidate["approved_for_execution"])
        self.assertFalse(candidate["authority_mutation"])
        self.assertTrue(candidate["candidate_id"].startswith("bcand-"))

    def test_authority_locks(self) -> None:
        pattern = build_pattern(
            signal="praise",
            polarity="positive",
            agent="a",
            skill_id="s",
            evidence_evaluation_ids=["beval-1"],
            scores=[0.9],
            threshold=0.7,
            min_occurrence=1,
        )
        pattern["authority_mutation"] = True
        with self.assertRaises(ValidationError):
            validate_document(pattern, "behavior-pattern.schema.json")
        candidate = build_candidate(pattern)
        candidate["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(candidate, "behavior-candidate.schema.json")


class DetectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m47-"))
        (self.tmp / ".agent" / "evaluations" / "behavior").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_requires_min_occurrence(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_LEARN_ENABLED": "1",
                "COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE": "3",
            },
        ):
            for i in range(2):
                _write_eval(self.tmp, evaluation_id=f"beval-few-{i}")
            self.assertEqual(detect_patterns(self.tmp), [])
            _write_eval(self.tmp, evaluation_id="beval-few-2")
            patterns = detect_patterns(self.tmp)
            self.assertEqual(len(patterns), 1)
            self.assertEqual(patterns[0]["occurrence_count"], 3)
            self.assertEqual(patterns[0]["signal"], "rework_required")
            self.assertEqual(patterns[0]["polarity"], "negative")
            self.assertEqual(patterns[0]["agent"], "implementation-agent")
            self.assertEqual(patterns[0]["skill_id"], "testing-validation")

    def test_excludes_abstain(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_LEARN_ENABLED": "1",
                "COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE": "3",
            },
        ):
            for i in range(2):
                _write_eval(self.tmp, evaluation_id=f"beval-ok-{i}")
            _write_eval(self.tmp, evaluation_id="beval-abs", abstain=True)
            self.assertEqual(detect_patterns(self.tmp), [])

    def test_below_threshold_excluded(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_LEARN_ENABLED": "1",
                "COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE": "2",
            },
        ):
            _write_eval(
                self.tmp,
                evaluation_id="beval-low-1",
                signals={"rework_required": 0.2},
            )
            _write_eval(
                self.tmp,
                evaluation_id="beval-low-2",
                signals={"rework_required": 0.2},
            )
            self.assertEqual(detect_patterns(self.tmp), [])

    def test_positive_polarity_for_praise(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_LEARN_ENABLED": "1",
                "COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE": "2",
            },
        ):
            for i in range(2):
                _write_eval(
                    self.tmp,
                    evaluation_id=f"beval-praise-{i}",
                    signals={"praise": 0.9},
                )
            patterns = detect_patterns(self.tmp)
            self.assertEqual(len(patterns), 1)
            self.assertEqual(patterns[0]["polarity"], "positive")
            self.assertEqual(patterns[0]["signal"], "praise")

    def test_groups_by_agent_and_skill(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_LEARN_ENABLED": "1",
                "COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE": "2",
            },
        ):
            for i in range(2):
                _write_eval(
                    self.tmp,
                    evaluation_id=f"beval-a-{i}",
                    agent="agent-a",
                    skill_ids=["skill-x"],
                )
            for i in range(2):
                _write_eval(
                    self.tmp,
                    evaluation_id=f"beval-b-{i}",
                    agent="agent-b",
                    skill_ids=["skill-x"],
                )
            patterns = detect_patterns(self.tmp)
            self.assertEqual(len(patterns), 2)
            agents = {p["agent"] for p in patterns}
            self.assertEqual(agents, {"agent-a", "agent-b"})


class ServiceAndCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m47-svc-"))
        (self.tmp / ".agent" / "evaluations" / "behavior").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scan_persist_list_show_export(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_LEARN_ENABLED": "1",
                "COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE": "3",
            },
        ):
            for i in range(3):
                _write_eval(self.tmp, evaluation_id=f"beval-scan-{i}")
            result = scan_and_persist(self.tmp)
            self.assertEqual(result["pattern_count"], 1)
            self.assertEqual(result["candidate_count"], 1)
            listed = list_learned_patterns(self.tmp)
            self.assertEqual(listed["count"], 1)
            pid = listed["patterns"][0]["pattern_id"]
            shown = show_pattern(self.tmp, pid)
            self.assertEqual(shown["pattern"]["pattern_id"], pid)
            self.assertEqual(len(shown["candidates"]), 1)
            self.assertFalse(shown["candidates"][0]["approved_for_execution"])
            # Idempotent overwrite (stable candidate id)
            again = scan_and_persist(self.tmp)
            self.assertEqual(again["pattern_count"], 1)
            dest = self.tmp / "out.csv"
            export_patterns_csv(self.tmp, dest)
            with dest.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["pattern_id"], pid)

    def test_scan_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_BEHAVIOR_LEARN_ENABLED", None)
            with self.assertRaises(PermissionError):
                scan_and_persist(self.tmp)

    def test_cli_requires_enable_flag(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_BEHAVIOR_LEARN_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "northstar"), "learn", "scan", "--repo", str(self.tmp)],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("COMPASS_BEHAVIOR_LEARN_ENABLED", proc.stderr)

    def test_cli_scan_happy_path(self) -> None:
        for i in range(3):
            _write_eval(self.tmp, evaluation_id=f"beval-cli-{i}")
        env = os.environ.copy()
        env["COMPASS_BEHAVIOR_LEARN_ENABLED"] = "1"
        env["COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE"] = "3"
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "northstar"), "learn", "scan", "--repo", str(self.tmp)],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["pattern_count"], 1)

    def test_no_routing_or_skill_mutation(self) -> None:
        routing = ROOT / ".agent" / "routing" / "proposals"
        before = {p.name for p in routing.glob("*")} if routing.is_dir() else set()
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_LEARN_ENABLED": "1",
                "COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE": "2",
            },
        ):
            for i in range(2):
                _write_eval(self.tmp, evaluation_id=f"beval-iso-{i}")
            pairs = patterns_with_candidates(self.tmp)
            self.assertTrue(pairs)
            for pattern, candidate in pairs:
                self.assertFalse(pattern["authority_mutation"])
                self.assertFalse(candidate["approved_for_execution"])
                self.assertFalse(candidate["authority_mutation"])
            scan_and_persist(self.tmp)
            listed = list_learned_patterns(self.tmp)
            loaded = load_pattern(self.tmp, listed["patterns"][0]["pattern_id"])
            self.assertIn("rework_required", loaded["signal"])
        after = {p.name for p in routing.glob("*")} if routing.is_dir() else set()
        self.assertEqual(before, after)
        self.assertTrue(
            (self.tmp / ".agent" / "evaluations" / "behavior" / "patterns").is_dir()
        )


if __name__ == "__main__":
    unittest.main()
