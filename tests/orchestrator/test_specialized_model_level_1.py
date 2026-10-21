"""Specialized Model Level 1 on-device LoRA harness tests."""

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
_FIXTURE_ROOT = ROOT / ".agent" / "tmp-specialized-model-l1-tests"
SAMPLE_EXPORT = (
    ROOT / "tests" / "fixtures" / "specialized-model-gold" / "sample-export.json"
)

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.specialized.enabled import require_specialized_model_gate
from orchestrator.specialized.lora import (
    evaluate_lora,
    prepare_dataset,
    run_lora_pipeline,
    train_lora,
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
    def test_lora_run_locks(self) -> None:
        doc = {
            "schema_version": "1",
            "run_id": "sm1-test",
            "plan_id": "specialized-model-level-1",
            "level": 1,
            "phase": "evaluate",
            "repository_sha": "abc",
            "northstar_version": "1.70.0",
            "dataset_id": "smds-test",
            "dataset_path": None,
            "dry_run": True,
            "adapter_root": "tests/fixtures/specialized-model-lora/fixture-adapter",
            "train_metrics": None,
            "baseline_scores": {"retrieval_rate": 1.0},
            "adapter_scores": {"retrieval_rate": 1.0},
            "comparison": {"retrieval_delta": 0.0},
            "checklist": {
                "license_reviewed": True,
                "secrets_redacted_ack": True,
                "pii_reviewed": True,
                "provenance_recorded": True,
                "weights_outside_control_repo_ack": True,
                "holdout_retained": True,
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
        validate_document(doc, "specialized-model-lora-run.schema.json")
        for key in ("weights_committed", "auto_promoted", "approved_for_execution"):
            bad = dict(doc)
            bad[key] = True
            with self.assertRaises(ValidationError):
                validate_document(bad, "specialized-model-lora-run.schema.json")


class PipelineTests(unittest.TestCase):
    def test_prepare_train_evaluate_dry_run(self) -> None:
        evidence = _mk_dir("sm1-ev-")
        try:
            with mock.patch.dict(os.environ, GATES):
                dataset = prepare_dataset(
                    ROOT, export_path=SAMPLE_EXPORT
                )
                self.assertGreaterEqual(dataset["sample_count"], 1)
                self.assertTrue(dataset["permission_checklist"]["export_authorized"])
                path = Path(dataset["_path"])
                self.assertTrue(path.is_file())
                validate_document(
                    {k: v for k, v in dataset.items() if k != "_path"},
                    "specialized-model-dataset.schema.json",
                )

                train = train_lora(
                    ROOT, dataset_path=path, dry_run=True
                )
                self.assertTrue(train["dry_run"])
                self.assertFalse(train["weights_committed"])
                self.assertFalse(train["auto_promoted"])
                metrics_path = Path(train["adapter_root"]) / "train-metrics.json"
                self.assertTrue(metrics_path.is_file())

                report = evaluate_lora(
                    ROOT,
                    dataset_path=path,
                    adapter_root=Path(train["adapter_root"]),
                    dry_run=True,
                    evidence_dir=evidence,
                    write_evidence=True,
                    train_metrics=train.get("train_metrics"),
                )
            self.assertIn(report["overall_status"], {"pass", "warn"})
            self.assertEqual(report["level"], 1)
            self.assertFalse(report["weights_committed"])
            self.assertFalse(report["auto_promoted"])
            self.assertTrue(report["dry_run"])
            self.assertEqual(report["go_no_go"], "hold")  # dry-run → hold
            validate_document(report, "specialized-model-lora-run.schema.json")
            self.assertTrue((evidence / "SUMMARY.md").is_file())
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_pipeline_convenience(self) -> None:
        evidence = _mk_dir("sm1-pipe-")
        try:
            with mock.patch.dict(os.environ, GATES):
                report = run_lora_pipeline(
                    ROOT,
                    export_path=SAMPLE_EXPORT,
                    dry_run=True,
                    evidence_dir=evidence,
                    write_evidence=True,
                )
            self.assertFalse(report["weights_committed"])
            self.assertFalse(report["auto_promoted"])
            self.assertTrue(report["dataset_id"])
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_refuse_live_train_without_trainer(self) -> None:
        with mock.patch.dict(os.environ, GATES, clear=False):
            os.environ.pop("COMPASS_SPECIALIZED_LORA_TRAINER", None)
            os.environ.pop("COMPASS_SPECIALIZED_ADAPTER_ROOT", None)
            dataset = prepare_dataset(ROOT, export_path=SAMPLE_EXPORT)
            with self.assertRaises(SpecializedModelServiceError):
                train_lora(
                    ROOT,
                    dataset_path=Path(dataset["_path"]),
                    dry_run=False,
                    adapter_root=_mk_dir("sm1-out-"),  # outside? under .agent tmp
                )

    def test_cli_lora_fail_closed(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_SPECIALIZED_MODEL_ENABLED", None)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "run-specialized-model.sh"),
                "lora",
                "prepare",
                "--repo-root",
                str(ROOT),
                "--export-path",
                str(SAMPLE_EXPORT),
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
        evidence = _mk_dir("sm1-cli-")
        try:
            env = os.environ.copy()
            env.pop("COMPASS_SPECIALIZED_MODEL_ENABLED", None)
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-specialized-model.sh"),
                    "lora",
                    "pipeline",
                    "--repo-root",
                    str(ROOT),
                    "--enable-gates",
                    "--export-path",
                    str(SAMPLE_EXPORT),
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
        finally:
            shutil.rmtree(evidence, ignore_errors=True)

    def test_northstar_lora_help(self) -> None:
        help_out = subprocess.run(
            [str(ROOT / "scripts" / "northstar"), "help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        self.assertIn("specialized lora", help_out)


if __name__ == "__main__":
    unittest.main()
