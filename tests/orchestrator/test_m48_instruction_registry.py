"""M48 Instruction Registry + Prompt Composer — hermetic proposal-only tests."""

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

from orchestrator.behavior.enabled import (
    instructions_enabled,
    require_instructions_enabled,
)
from orchestrator.behavior.instructions.composer import (
    compose_prompt_bundle,
    prompt_bundle_hash_for_packet,
)
from orchestrator.behavior.instructions.draft import draft_from_candidates
from orchestrator.behavior.instructions.service import (
    compose,
    list_registry,
)
from orchestrator.behavior.instructions.store import (
    build_instruction,
    hash_prompt_bundle_content,
    list_instructions,
    seed_global_operating_brief,
    write_instruction,
)
# write_instruction imported for scope-dir test
from orchestrator.behavior.patterns.store import build_candidate, build_pattern, write_candidate
from orchestrator.schemas.validate import ValidationError, validate_document


class EnabledGateTests(unittest.TestCase):
    def test_default_disabled(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COMPASS_INSTRUCTIONS_ENABLED", None)
            self.assertFalse(instructions_enabled())
            with self.assertRaises(PermissionError):
                require_instructions_enabled()

    def test_enabled_truthy(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_INSTRUCTIONS_ENABLED": "1"}):
            self.assertTrue(instructions_enabled())


class SchemaTests(unittest.TestCase):
    def test_instruction_and_bundle_validate(self) -> None:
        instruction = build_instruction(
            title="demo",
            body="Prefer evidence.",
            scope="proposal",
            approval_state="draft",
        )
        validate_document(instruction, "instruction.schema.json")
        self.assertFalse(instruction["approved_for_execution"])
        self.assertFalse(instruction["authority_mutation"])

    def test_authority_locks(self) -> None:
        instruction = build_instruction(
            title="demo",
            body="Prefer evidence.",
            scope="proposal",
        )
        bad = dict(instruction)
        bad["approved_for_execution"] = True
        with self.assertRaises(ValidationError):
            validate_document(bad, "instruction.schema.json")
        polluted = dict(instruction)
        polluted["api_key"] = "sk-secret"
        with self.assertRaises(ValidationError):
            validate_document(polluted, "instruction.schema.json")


class RegistryComposerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m48-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_seed_compose_deterministic_hash(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_INSTRUCTIONS_ENABLED": "1"}):
            seed_global_operating_brief(self.tmp)
            first = compose_prompt_bundle(self.tmp, agent="implementation-agent")
            second = compose_prompt_bundle(self.tmp, agent="implementation-agent")
            self.assertEqual(first["prompt_bundle_hash"], second["prompt_bundle_hash"])
            self.assertEqual(first["bundle_id"], second["bundle_id"])
            self.assertTrue(first["prompt_bundle_hash"].startswith("sha256:"))
            self.assertIn("persona", first)
            self.assertTrue(first["instructions"])
            self.assertTrue(first["constraints"])
            self.assertFalse(first["approved_for_execution"])
            # Stable content hash ignores timestamps
            again = dict(first)
            again["created_at"] = "2099-01-01T00:00:00Z"
            self.assertEqual(
                hash_prompt_bundle_content(first),
                hash_prompt_bundle_content(again),
            )

    def test_draft_from_candidates(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_INSTRUCTIONS_ENABLED": "1"}):
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
            candidate = build_candidate(pattern)
            write_candidate(self.tmp, candidate)
            result = draft_from_candidates(self.tmp)
            self.assertEqual(result["instruction_count"], 1)
            instructions = list_instructions(self.tmp)
            drafts = [i for i in instructions if i.get("approval_state") == "draft"]
            self.assertTrue(drafts)
            self.assertFalse(drafts[0]["approved_for_execution"])
            self.assertIn(candidate["candidate_id"], drafts[0]["source_candidate_ids"])

    def test_cli_requires_enable_flag(self) -> None:
        env = os.environ.copy()
        env.pop("COMPASS_INSTRUCTIONS_ENABLED", None)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "northstar"),
                "instructions",
                "list",
                "--repo",
                str(self.tmp),
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("COMPASS_INSTRUCTIONS_ENABLED", proc.stderr)

    def test_cli_compose_happy_path(self) -> None:
        env = os.environ.copy()
        env["COMPASS_INSTRUCTIONS_ENABLED"] = "1"
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [
                str(ROOT / "scripts" / "northstar"),
                "instructions",
                "compose",
                "--agent",
                "implementation-agent",
                "--repo",
                str(self.tmp),
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "composed")
        self.assertTrue(payload["bundle"]["prompt_bundle_hash"].startswith("sha256:"))

    def test_writes_only_under_behavior_instructions(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_INSTRUCTIONS_ENABLED": "1"}):
            compose(self.tmp, agent="implementation-agent")
            list_registry(self.tmp)
            draft_from_candidates(self.tmp)
        root = self.tmp / ".agent" / "evaluations" / "behavior" / "instructions"
        self.assertTrue((root / "global").is_dir())
        self.assertTrue((root / "bundles").is_dir())
        # Global seed lands under global/
        self.assertTrue(any((root / "global").glob("instr-*.json")))
        # No writes outside behavior instructions
        self.assertFalse((self.tmp / ".cursor").exists())
        self.assertFalse((self.tmp / ".agent" / "routing").exists())

    def test_scope_dirs_used(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_INSTRUCTIONS_ENABLED": "1"}):
            instruction = build_instruction(
                title="agent-overlay",
                body="Prefer small diffs.",
                scope="agent",
                agent="implementation-agent",
                approval_state="candidate",
            )
            path = write_instruction(self.tmp, instruction)
            self.assertIn("/agents/", str(path).replace("\\", "/"))
            loaded = list_instructions(self.tmp)
            self.assertTrue(any(i["instruction_id"] == instruction["instruction_id"] for i in loaded))


class EvaluateHashWireTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="m48-eval-"))
        (self.tmp / ".agent" / "runs").mkdir(parents=True)
        fixture = ROOT / "tests" / "fixtures" / "behavior" / "execution-run-contact.json"
        shutil.copy(
            fixture,
            self.tmp / ".agent" / "runs" / "run-fixture-contact-counter.json",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_prompt_bundle_hash_for_packet_requires_existing_bundle(self) -> None:
        packet = {
            "execution_id": "run-x",
            "agent": "implementation-agent",
            "skill_ids": ["testing-validation"],
        }
        self.assertEqual(prompt_bundle_hash_for_packet(self.tmp, packet), "")
        with mock.patch.dict(os.environ, {"COMPASS_INSTRUCTIONS_ENABLED": "1"}):
            composed = compose_prompt_bundle(
                self.tmp, agent="implementation-agent", skill_id="testing-validation"
            )
        digest = prompt_bundle_hash_for_packet(self.tmp, packet)
        self.assertEqual(digest, composed["prompt_bundle_hash"])

    def test_evaluate_records_bundle_hash_without_seeding(self) -> None:
        from orchestrator.behavior.service import evaluate_execution

        instr_root = (
            self.tmp / ".agent" / "evaluations" / "behavior" / "instructions"
        )
        with mock.patch.dict(
            os.environ,
            {
                "COMPASS_BEHAVIOR_EVAL_ENABLED": "1",
                "COMPASS_DECISION_PROVIDER": "file",
            },
        ):
            # No composed bundle yet → empty hash; must not create registry artifacts
            empty = evaluate_execution(self.tmp, "run-fixture-contact-counter")
            self.assertEqual(
                str(empty["record"].get("evaluator", {}).get("prompt_bundle_hash") or ""),
                "",
            )
            self.assertFalse(instr_root.exists())

            with mock.patch.dict(os.environ, {"COMPASS_INSTRUCTIONS_ENABLED": "1"}):
                compose_prompt_bundle(self.tmp, agent="implementation-agent")

            result = evaluate_execution(
                self.tmp, "run-fixture-contact-counter", force=True
            )
            self.assertTrue(
                str(result["record"].get("evaluator", {}).get("prompt_bundle_hash") or "").startswith(
                    "sha256:"
                )
            )


if __name__ == "__main__":
    unittest.main()
