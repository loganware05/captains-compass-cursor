"""N4 cross-stack benchmark — hermetic tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.benchmark.n4.enabled import n4_enabled
from orchestrator.benchmark.n4.metrics import primary_efficiency, summarize_arm
from orchestrator.benchmark.n4.service import N4ServiceError, run_n4_benchmark
from orchestrator.benchmark.n4.tasks import load_task_pack, seeded_order
from orchestrator.schemas.validate import ValidationError, validate_document


class GateTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_N4_BENCHMARK_ENABLED", None)
            self.assertFalse(n4_enabled())
            with self.assertRaises(PermissionError):
                run_n4_benchmark(Path("."), persist=False)


class TaskPackTests(unittest.TestCase):
    def test_load_pack_size_and_seed_determinism(self) -> None:
        tasks = load_task_pack()
        self.assertGreaterEqual(len(tasks), 12)
        held = [t for t in tasks if t.get("held_out")]
        self.assertGreaterEqual(len(held), 2)
        a = [t["task_id"] for t in seeded_order(tasks, 20261026)]
        b = [t["task_id"] for t in seeded_order(tasks, 20261026)]
        c = [t["task_id"] for t in seeded_order(tasks, 99)]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class SchemaLockTests(unittest.TestCase):
    def test_authority_locks(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_N4_BENCHMARK_ENABLED": "1"}):
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                (repo / "VERSION").write_text("1.75.0\n", encoding="utf-8")
                report = run_n4_benchmark(repo, mode="hermetic", persist=False)
        validate_document(report, "n4-benchmark-report.schema.json")
        self.assertFalse(report["approved_for_execution"])
        self.assertFalse(report["authority_mutation"])
        self.assertFalse(report["auto_applied"])
        self.assertFalse(report["policy_promoted"])
        self.assertFalse(report["security_regression"])
        bad = dict(report)
        bad["policy_promoted"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "n4-benchmark-report.schema.json")


class RunnerTests(unittest.TestCase):
    def test_hermetic_compare_persists(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_N4_BENCHMARK_ENABLED": "1"}):
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                (repo / "VERSION").write_text("1.75.0\n", encoding="utf-8")
                report = run_n4_benchmark(
                    repo, mode="hermetic", seed=20261026, persist=True
                )
                self.assertEqual(report["mode"], "hermetic")
                self.assertEqual(report["task_count"], 15)
                self.assertIn("accepted_per_cost", report["primary_outcome"]["name"])
                path = Path(report["evidence_path"])
                self.assertTrue(path.is_file())
                latest = (
                    repo
                    / ".agent"
                    / "evidence"
                    / "n4-cross-stack-benchmark"
                    / "LATEST_hermetic.json"
                )
                self.assertTrue(latest.is_file())

    def test_live_requires_stack_roots(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_N4_BENCHMARK_ENABLED": "1"}, clear=False):
            os.environ.pop("COMPASS_N4_STACK_ROOTS", None)
            os.environ.pop("COMPASS_N4_LIVE_IMPLEMENT", None)
            with self.assertRaises(N4ServiceError):
                run_n4_benchmark(Path("."), mode="live", persist=False)

    def test_primary_efficiency(self) -> None:
        arm = summarize_arm(
            [
                {
                    "accepted": True,
                    "inference_cost_units": 1.0,
                    "engineering_cost_units": 1.0,
                    "latency_ms": 10.0,
                    "retries": 0.0,
                    "first_pass_test_rate": 1.0,
                    "skill_reuse_rate": 0.5,
                    "retrieval_precision": 0.5,
                    "review_precision": 0.5,
                }
            ]
        )
        self.assertEqual(primary_efficiency(arm), 0.5)


if __name__ == "__main__":
    unittest.main()
