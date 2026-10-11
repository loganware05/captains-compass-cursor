"""M50 Policy / Instruction Promotion Lifecycle — hermetic tests."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
PEVAL_FIXTURE = ROOT / "tests" / "fixtures" / "behavior" / "policy" / "peval-pass.json"

from orchestrator.behavior.enabled import (
    policy_apply_enabled,
    policy_promote_enabled,
    require_policy_promote_enabled,
)
from orchestrator.behavior.instructions.composer import compose_prompt_bundle
from orchestrator.behavior.instructions.store import build_instruction, write_instruction
from orchestrator.behavior.ledger import build_behavior_evaluation, write_behavior_evaluation
from orchestrator.behavior.policy.service import (
    PolicyServiceError,
    create_from_instruction,
    export_policies_csv,
    list_registry,
    materialize,
    promote,
)
from orchestrator.behavior.policy.shadow import run_shadow
from orchestrator.behavior.policy.store import list_policies, load_policy
from orchestrator.schemas.validate import ValidationError, validate_document


def _seed_instruction(repo: Path, *, title: str = "prefer-evidence") -> str:
    instr = build_instruction(
        title=title,
        body="Prefer evidence from tests/ over assertion.",
        scope="proposal",
        agent="implementation-agent",
        skill_id="testing-validation",
        approval_state="candidate",
    )
    write_instruction(repo, instr)
    return str(instr["instruction_id"])


def _seed_peval(repo: Path) -> str:
    dest = (
        repo
        / ".agent"
        / "evaluations"
        / "behavior"
        / "prompt-eval"
        / "peval-fixture-pass.json"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(PEVAL_FIXTURE, dest)
    return "peval-fixture-pass"


def _seed_success_evals(repo: Path, *, policy_id: str, n: int = 2) -> list[str]:
    ids: list[str] = []
    for i in range(n):
        packet = {
            "execution_id": f"exec-m50-{i}",
            "task_id": f"task-m50-{i}",
            "agent": "implementation-agent",
            "skill_ids": ["testing-validation"],
            "outcome": "success",
            "objective": "m50 proven gate",
            "repository_sha": "abc",
            "northstar_version": "1.55.0",
            "evidence": [{"kind": "policy_ref", "policy_id": policy_id}],
        }
        record = build_behavior_evaluation(
            packet,
            signals={"praise": 0.9},
            provider="stub",
            model_id="stub",
            prompt_bundle_hash="sha256:candidate",
            evaluation_id=f"beval-m50-{i:04d}",
        )
        write_behavior_evaluation(repo, record)
        ids.append(record["evaluation_id"])
    return ids


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_POLICY_PROMOTE_ENABLED", None)
            os.environ.pop("COMPASS_POLICY_APPLY_ENABLED", None)
            self.assertFalse(policy_promote_enabled())
            self.assertFalse(policy_apply_enabled())
            with self.assertRaises(PermissionError):
                require_policy_promote_enabled()

    def test_enabled_truthy(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_POLICY_PROMOTE_ENABLED": "1",
                "COMPASS_POLICY_APPLY_ENABLED": "1",
            },
        ):
            self.assertTrue(policy_promote_enabled())
            self.assertTrue(policy_apply_enabled())


class SchemaTests(unittest.TestCase):
    def test_policy_schema_locks(self) -> None:
        policy = {
            "policy_id": "pol-test",
            "instruction_ids": ["instr-a"],
            "lifecycle_state": "candidate",
            "schema_version": "1",
            "created_at": "2026-10-11T00:00:00Z",
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(policy, "behavior-policy.schema.json")
        bad = dict(policy)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "behavior-policy.schema.json")

    def test_shadow_applied_must_be_false(self) -> None:
        report = {
            "shadow_id": "pshadow-test",
            "policy_id": "pol-test",
            "baseline_hash": "sha256:a",
            "candidate_hash": "sha256:b",
            "would_have_changed": True,
            "applied": False,
            "schema_version": "1",
            "created_at": "2026-10-11T00:00:00Z",
            "approved_for_execution": False,
            "authority_mutation": False,
        }
        validate_document(report, "shadow-report.schema.json")
        bad = dict(report)
        bad["applied"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "shadow-report.schema.json")


class LifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m50-"))
        (self.tmp / "VERSION").write_text("1.55.0\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_illegal_transition(self) -> None:
        iid = _seed_instruction(self.tmp)
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_PROMOTE_ENABLED": "1"}):
            created = create_from_instruction(self.tmp, iid)
            pid = created["policy"]["policy_id"]
            with self.assertRaises(PolicyServiceError):
                promote(self.tmp, to_state="active", policy_id=pid, captain_approved=True)

    def test_sandbox_requires_peval_pass(self) -> None:
        iid = _seed_instruction(self.tmp)
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_PROMOTE_ENABLED": "1"}):
            created = create_from_instruction(self.tmp, iid)
            pid = created["policy"]["policy_id"]
            with self.assertRaises(PolicyServiceError):
                promote(
                    self.tmp,
                    to_state="sandbox_evaluated",
                    policy_id=pid,
                    prompt_eval_report_id="missing",
                )

    def test_full_lifecycle_to_proven(self) -> None:
        iid = _seed_instruction(self.tmp)
        report_id = _seed_peval(self.tmp)
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_PROMOTE_ENABLED": "1"}):
            created = create_from_instruction(self.tmp, iid)
            pid = created["policy"]["policy_id"]
            promote(
                self.tmp,
                to_state="sandbox_evaluated",
                policy_id=pid,
                prompt_eval_report_id=report_id,
            )
            promote(self.tmp, to_state="shadowed", policy_id=pid)
            policy = load_policy(self.tmp, pid)
            self.assertEqual(policy["lifecycle_state"], "shadowed")
            self.assertTrue(policy.get("shadow_report_id"))
            promote(
                self.tmp,
                to_state="approved",
                policy_id=pid,
                captain_approved=True,
            )
            promote(
                self.tmp,
                to_state="active",
                policy_id=pid,
                captain_approved=True,
            )
            _seed_success_evals(self.tmp, policy_id=pid, n=2)
            result = promote(
                self.tmp,
                to_state="proven",
                policy_id=pid,
                captain_approved=True,
            )
            self.assertEqual(result["policy"]["lifecycle_state"], "proven")
            self.assertFalse(result["policy"]["approved_for_execution"])
            self.assertFalse(result["event"]["authority_mutation"])

    def test_active_requires_captain(self) -> None:
        iid = _seed_instruction(self.tmp)
        report_id = _seed_peval(self.tmp)
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_PROMOTE_ENABLED": "1"}):
            pid = create_from_instruction(self.tmp, iid)["policy"]["policy_id"]
            promote(
                self.tmp,
                to_state="sandbox_evaluated",
                policy_id=pid,
                prompt_eval_report_id=report_id,
            )
            promote(self.tmp, to_state="shadowed", policy_id=pid)
            with self.assertRaises(PolicyServiceError):
                promote(self.tmp, to_state="approved", policy_id=pid)

    def test_shadow_applied_false(self) -> None:
        iid = _seed_instruction(self.tmp)
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_PROMOTE_ENABLED": "1"}):
            pid = create_from_instruction(self.tmp, iid)["policy"]["policy_id"]
            report = run_shadow(self.tmp, pid)
            self.assertFalse(report["applied"])
            self.assertIn("shadow_id", report)

    def test_compose_active_gated(self) -> None:
        iid = _seed_instruction(self.tmp)
        report_id = _seed_peval(self.tmp)
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_PROMOTE_ENABLED": "1"}):
            pid = create_from_instruction(self.tmp, iid)["policy"]["policy_id"]
            promote(
                self.tmp,
                to_state="sandbox_evaluated",
                policy_id=pid,
                prompt_eval_report_id=report_id,
            )
            promote(self.tmp, to_state="shadowed", policy_id=pid)
            promote(
                self.tmp, to_state="approved", policy_id=pid, captain_approved=True
            )
            promote(
                self.tmp, to_state="active", policy_id=pid, captain_approved=True
            )
        # Without apply flag, active proposal bodies are excluded from proposals path
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_POLICY_APPLY_ENABLED", None)
            baseline = compose_prompt_bundle(
                self.tmp,
                agent="implementation-agent",
                skill_id="testing-validation",
                persist=False,
                include_proposals=True,
                include_active=False,
            )
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_APPLY_ENABLED": "1"}):
            active = compose_prompt_bundle(
                self.tmp,
                agent="implementation-agent",
                skill_id="testing-validation",
                persist=False,
                include_proposals=True,
                include_active=True,
            )
        self.assertNotEqual(
            baseline["prompt_bundle_hash"], active["prompt_bundle_hash"]
        )
        self.assertTrue(
            any("Prefer evidence from tests/" in t for t in active["instructions"])
        )

    def test_materialize_proposal_no_cursor_write(self) -> None:
        iid = _seed_instruction(self.tmp)
        report_id = _seed_peval(self.tmp)
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_PROMOTE_ENABLED": "1"}):
            pid = create_from_instruction(self.tmp, iid)["policy"]["policy_id"]
            promote(
                self.tmp,
                to_state="sandbox_evaluated",
                policy_id=pid,
                prompt_eval_report_id=report_id,
            )
            promote(self.tmp, to_state="shadowed", policy_id=pid)
            promote(
                self.tmp, to_state="approved", policy_id=pid, captain_approved=True
            )
            promote(
                self.tmp, to_state="active", policy_id=pid, captain_approved=True
            )
            result = materialize(self.tmp, pid)
            self.assertFalse(result["applied"])
            self.assertTrue(Path(result["path"]).is_dir())
            self.assertFalse((self.tmp / ".cursor").exists())

    def test_service_requires_gate(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_POLICY_PROMOTE_ENABLED", None)
            with self.assertRaises(PermissionError):
                list_registry(self.tmp)

    def test_cli_fail_closed_and_list(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_POLICY_PROMOTE_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [str(ROOT / "scripts" / "run-policy.sh"), "list", "--repo-root", str(self.tmp)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("COMPASS_POLICY_PROMOTE_ENABLED", proc.stderr)

        iid = _seed_instruction(self.tmp)
        env["COMPASS_POLICY_PROMOTE_ENABLED"] = "1"
        create = subprocess.run(
            [
                str(ROOT / "scripts" / "run-policy.sh"),
                "create",
                "--instruction-id",
                iid,
                "--repo-root",
                str(self.tmp),
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stderr)
        listed = list_policies(self.tmp)
        self.assertEqual(len(listed), 1)

    def test_export_csv(self) -> None:
        iid = _seed_instruction(self.tmp)
        with mock.patch.dict(os.environ, {"COMPASS_POLICY_PROMOTE_ENABLED": "1"}):
            create_from_instruction(self.tmp, iid)
            dest = self.tmp / "policies.csv"
            path = export_policies_csv(self.tmp, dest)
            text = path.read_text(encoding="utf-8")
            self.assertIn("policy_id", text)
            self.assertIn("lifecycle_state", text)


if __name__ == "__main__":
    unittest.main()
