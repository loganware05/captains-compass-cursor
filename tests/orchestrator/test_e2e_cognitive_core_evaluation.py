"""E2E Cognitive Core evaluation harness tests."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-e2e-tests"

from orchestrator.e2e.enabled import missing_gates, require_e2e_gates
from orchestrator.e2e.service import E2EServiceError, run_cognitive_core_e2e
from orchestrator.schemas.validate import ValidationError, validate_document

GATES = {
    "COMPASS_BRAIN_ENABLED": "1",
    "COMPASS_ASSESS_ENABLED": "1",
    "COMPASS_CYCLE_ENABLED": "1",
    "COMPASS_ROUTE_ENABLED": "1",
    "COMPASS_REA_ENABLED": "1",
    "COMPASS_TRAIN_BRIDGE_ENABLED": "1",
    "COMPASS_TRAIN_BRIDGE_FIXTURE": "1",
}


def _mk_fixture_dir(prefix: str) -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(_FIXTURE_ROOT)))


def _seed_repo(repo: Path) -> None:
    (repo / "VERSION").write_text("1.67.0\n", encoding="utf-8")
    for name in (
        "AGENTS.md",
        "PROJECT_CONTEXT.md",
        "DECISIONS.md",
        "PROGRESS.md",
        "TESTING.md",
        "IMPLEMENTATION_PLAN.md",
    ):
        (repo / name).write_text(
            f"# {name}\n\nCognitive Core e2e fixture. Status APPROVED.\n",
            encoding="utf-8",
        )
    (repo / "DECISIONS.md").write_text(
        "# Decisions\n\n"
        "## ADR-077: Cognitive Core C1 Source of Truth (v1.60.0)\n\n"
        "- Status: Accepted\n"
        "- Brain sync snapshots cite repository SHA; never grants authority.\n\n"
        "## ADR-079: Cognitive Core C2 Memory Retrieval (v1.61.0)\n\n"
        "- Status: Accepted\n"
        "- Gold-set evidence-linked retrieval; COMPASS_BRAIN_ENABLED gate.\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git init failed: {proc.stderr or proc.stdout}")
    subprocess.run(
        ["git", "config", "user.email", "e2e@test.local"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "E2E Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "commit", "-m", "seed"],
        cwd=repo,
        check=True,
        capture_output=True,
    )


class GateTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            for key in GATES:
                os.environ.pop(key, None)
            self.assertTrue(missing_gates())
            with self.assertRaises(PermissionError):
                require_e2e_gates()

    def test_all_gates(self) -> None:
        with mock.patch.dict(os.environ, GATES):
            self.assertEqual(missing_gates(), [])
            require_e2e_gates()


class SchemaTests(unittest.TestCase):
    def test_authority_locked(self) -> None:
        doc = {
            "schema_version": "1",
            "report_id": "e2e-cc-test",
            "mode": "hermetic",
            "repository_sha": "abc",
            "northstar_version": "1.67.0",
            "plan_id": "e2e-cognitive-core-evaluation",
            "stages": [
                {
                    "id": "c1-brain-sync",
                    "milestone": "C1",
                    "status": "pass",
                    "summary": "ok",
                    "details": {},
                }
            ],
            "baselines": {
                "brain_goldset_rate": 0.5,
                "brain_goldset_target": 0.9,
                "assess_backtest_pass_rate": 1.0,
                "route_eval_case_count": 3,
                "cycle_authority_locked": True,
                "rea_claim_kinds_ok": True,
                "train_auto_uploaded": False,
            },
            "warnings": [],
            "overall_status": "warn",
            "evidence_path": None,
            "notes": "test",
            "approved_for_execution": False,
            "authority_mutation": False,
            "auto_uploaded": False,
            "generated_at": "2026-10-20T00:00:00Z",
        }
        validate_document(doc, "e2e-cognitive-core-report.schema.json")
        bad = dict(doc)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "e2e-cognitive-core-report.schema.json")


class RunnerTests(unittest.TestCase):
    def test_hermetic_run(self) -> None:
        # Assess/cycle need a real Skill registry — use control repo like C3 tests.
        evidence = _mk_fixture_dir("e2e-evidence-")
        try:
            with mock.patch.dict(os.environ, GATES):
                report = run_cognitive_core_e2e(
                    ROOT,
                    mode="hermetic",
                    evidence_dir=evidence,
                    write_evidence=True,
                )
            self.assertIn(report["overall_status"], {"pass", "warn"})
            self.assertFalse(report["approved_for_execution"])
            self.assertFalse(report["authority_mutation"])
            self.assertFalse(report["auto_uploaded"])
            self.assertEqual(len(report["stages"]), 7)
            milestones = [s["milestone"] for s in report["stages"]]
            self.assertEqual(milestones, ["C1", "C2", "C3", "C4", "C5", "C6", "C7"])
            self.assertTrue(report["baselines"]["cycle_authority_locked"])
            self.assertFalse(report["baselines"]["train_auto_uploaded"])
            self.assertTrue(evidence.is_dir())
            self.assertTrue((evidence / "SUMMARY.md").is_file())
            validate_document(report, "e2e-cognitive-core-report.schema.json")
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_cli_fail_closed(self) -> None:
        env = os.environ.copy()
        for key in GATES:
            env.pop(key, None)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-cognitive-core-e2e.sh"), "--repo-root", str(ROOT)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_", proc.stderr)

    def test_cli_enable_gates_smoke(self) -> None:
        evidence = _mk_fixture_dir("e2e-cli-ev-")
        try:
            env = os.environ.copy()
            for key in GATES:
                env.pop(key, None)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-cognitive-core-e2e.sh"),
                    "--repo-root",
                    str(ROOT),
                    "--enable-gates",
                    "--evidence-dir",
                    str(evidence),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertIn(proc.returncode, {0}, msg=proc.stderr + proc.stdout[-2000:])
            report = json.loads(proc.stdout)
            self.assertIn(report["overall_status"], {"pass", "warn"})
        finally:
            shutil.rmtree(evidence, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
