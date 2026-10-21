"""Specialized Model Level 2 rented GPU QLoRA harness tests."""

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
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-specialized-model-l2-tests"
SAMPLE_DATASET = (
    ROOT / "tests" / "fixtures" / "specialized-model-gpu" / "sample-dataset.json"
)

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.specialized.enabled import require_specialized_model_gate
from orchestrator.specialized.gpu import (
    evaluate_gpu,
    prepare_gpu_job,
    run_gpu_pipeline,
    submit_gpu_job,
)
from orchestrator.specialized.service import SpecializedModelServiceError

GATES = {"COMPASS_SPECIALIZED_MODEL_ENABLED": "1"}


def _mk_dir(prefix: str) -> Path:
    _FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(_FIXTURE_ROOT)))


class GateTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_SPECIALIZED_MODEL_ENABLED", None)
            with self.assertRaises(PermissionError):
                require_specialized_model_gate()


class SchemaTests(unittest.TestCase):
    def test_gpu_run_locks(self) -> None:
        doc = {
            "schema_version": "1",
            "run_id": "sm2-test",
            "plan_id": "specialized-model-level-2",
            "level": 2,
            "phase": "evaluate",
            "repository_sha": "abc",
            "northstar_version": "1.71.0",
            "job_id": "smgpu-test",
            "job_path": None,
            "dataset_id": "smds-test",
            "dry_run": True,
            "cost_acknowledged": True,
            "adapter_root": "tests/fixtures/specialized-model-gpu/fixture-adapter",
            "train_metrics": None,
            "baseline_scores": {"retrieval_rate": 1.0},
            "level1_scores": {"retrieval_rate": 1.0},
            "adapter_scores": {"retrieval_rate": 1.0},
            "comparison": {"retrieval_delta_vs_l0": 0.0},
            "checklist": {
                "license_reviewed": True,
                "secrets_redacted_ack": True,
                "pii_reviewed": True,
                "provenance_recorded": True,
                "weights_outside_control_repo_ack": True,
                "holdout_retained": True,
                "cost_acknowledged": True,
            },
            "warnings": [],
            "overall_status": "pass",
            "go_no_go": "hold",
            "evidence_path": None,
            "notes": "test",
            "weights_committed": False,
            "auto_promoted": False,
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": "2026-10-21T00:00:00Z",
        }
        validate_document(doc, "specialized-model-gpu-run.schema.json")
        for key in ("weights_committed", "auto_promoted", "approved_for_execution"):
            bad = dict(doc)
            bad[key] = True
            with self.assertRaises(ValidationError):
                validate_document(bad, "specialized-model-gpu-run.schema.json")


class PipelineTests(unittest.TestCase):
    def test_prepare_submit_evaluate_dry_run(self) -> None:
        evidence = _mk_dir("sm2-ev-")
        try:
            with mock.patch.dict(os.environ, GATES):
                job = prepare_gpu_job(ROOT, dataset_path=SAMPLE_DATASET)
                self.assertEqual(job["level"], 2)
                self.assertTrue(job["qlora"])
                path = Path(job["_path"])
                self.assertTrue(path.is_file())
                validate_document(
                    {k: v for k, v in job.items() if k != "_path"},
                    "specialized-model-gpu-job.schema.json",
                )

                submit = submit_gpu_job(
                    ROOT, job_path=path, dry_run=True, cost_ack=False
                )
                self.assertTrue(submit["dry_run"])
                self.assertFalse(submit["weights_committed"])
                self.assertFalse(submit["auto_promoted"])

                report = evaluate_gpu(
                    ROOT,
                    job_path=path,
                    dataset_path=SAMPLE_DATASET,
                    adapter_root=Path(submit["adapter_root"]),
                    dry_run=True,
                    evidence_dir=evidence,
                    write_evidence=True,
                    train_metrics=submit.get("train_metrics"),
                )
            self.assertIn(report["overall_status"], {"pass", "warn"})
            self.assertEqual(report["level"], 2)
            self.assertFalse(report["weights_committed"])
            self.assertFalse(report["auto_promoted"])
            self.assertEqual(report["go_no_go"], "hold")
            validate_document(report, "specialized-model-gpu-run.schema.json")
            self.assertTrue((evidence / "SUMMARY.md").is_file())
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_cost_ack_required_for_live_submit(self) -> None:
        with mock.patch.dict(os.environ, GATES, clear=False):
            os.environ.pop("COMPASS_SPECIALIZED_GPU_RUNNER", None)
            os.environ.pop("COMPASS_SPECIALIZED_ADAPTER_ROOT", None)
            job = prepare_gpu_job(ROOT, dataset_path=SAMPLE_DATASET)
            with self.assertRaises(SpecializedModelServiceError) as ctx:
                submit_gpu_job(
                    ROOT,
                    job_path=Path(job["_path"]),
                    dry_run=False,
                    cost_ack=False,
                    adapter_root=_mk_dir("sm2-out-"),
                )
            self.assertIn("cost-ack", str(ctx.exception))

    def test_pipeline_convenience(self) -> None:
        evidence = _mk_dir("sm2-pipe-")
        try:
            with mock.patch.dict(os.environ, GATES):
                report = run_gpu_pipeline(
                    ROOT,
                    dataset_path=SAMPLE_DATASET,
                    dry_run=True,
                    evidence_dir=evidence,
                    write_evidence=True,
                )
            self.assertFalse(report["weights_committed"])
            self.assertFalse(report["auto_promoted"])
            self.assertTrue(report["job_id"])
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_cli_gpu_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_SPECIALIZED_MODEL_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-specialized-model.sh"),
                "gpu",
                "prepare",
                "--repo-root",
                str(ROOT),
                "--dataset",
                str(SAMPLE_DATASET),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_SPECIALIZED_MODEL_ENABLED", proc.stderr)

    def test_cli_pipeline_dry_run(self) -> None:
        evidence = _mk_dir("sm2-cli-")
        try:
            env = os.environ.copy()
            env.pop("COMPASS_SPECIALIZED_MODEL_ENABLED", None)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-specialized-model.sh"),
                    "gpu",
                    "pipeline",
                    "--repo-root",
                    str(ROOT),
                    "--enable-gates",
                    "--dataset",
                    str(SAMPLE_DATASET),
                    "--dry-run",
                    "--evidence-dir",
                    str(evidence),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr + proc.stdout[-2000:])
            report = json.loads(proc.stdout)
            self.assertFalse(report["weights_committed"])
            self.assertFalse(report["auto_promoted"])
            self.assertTrue(report["cost_acknowledged"])
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_northstar_gpu_help(self) -> None:
        help_out = subprocess.run(
            [str(ROOT / "scripts" / "northstar"), "help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        self.assertIn("specialized gpu", help_out)


if __name__ == "__main__":
    unittest.main()
