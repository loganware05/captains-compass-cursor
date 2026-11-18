"""Bend proof spike (#278): policy-lifecycle conformance, drift, and mutation controls.

Tests that need the Bend toolchain skip when it is not installed, so default
CI and doctor behave exactly as before.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.behavior.policy import states as policy_states
from orchestrator.formal import policy_lifecycle as pl
from orchestrator.formal.gates import require_bend_proof_enabled
from orchestrator.formal.toolchain import discover

REPO = Path(__file__).resolve().parents[2]
FORMAL = REPO / pl.FORMAL_REL
TOOLCHAIN = discover(REPO)
needs_bend = unittest.skipUnless(TOOLCHAIN is not None, "Bend toolchain not installed")


class GateTests(unittest.TestCase):
    def test_disabled_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(PermissionError):
                require_bend_proof_enabled()

    def test_enabled_values(self) -> None:
        for value in ("1", "true", "YES", "on"):
            with mock.patch.dict(os.environ, {"COMPASS_BEND_PROOF_ENABLED": value}, clear=True):
                require_bend_proof_enabled()


class TablesAndDriftTests(unittest.TestCase):
    def test_lock_matches_python_tables(self) -> None:
        result = pl.check_drift(REPO)
        self.assertEqual(result["status"], "pass", result)

    def test_drift_detected_when_tables_change(self) -> None:
        mutated = dict(policy_states.TRANSITIONS)
        mutated["candidate"] = mutated["candidate"] | {"active"}
        with pl.patched_python_tables(transitions=mutated):
            self.assertNotEqual(pl.tables_sha256(), json_lock_hash())
            self.assertEqual(pl.check_drift(REPO)["status"], "fail")

    def test_drift_detected_when_captain_set_changes(self) -> None:
        cap = policy_states.CAPTAIN_REQUIRED - {"approved"}
        with pl.patched_python_tables(captain_required=cap):
            self.assertEqual(pl.check_drift(REPO)["status"], "fail")

    def test_missing_lock_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(pl.check_drift(Path(tmp))["status"], "fail")

    def test_write_lock_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / pl.FORMAL_REL).mkdir(parents=True)
            pl.write_lock(root)
            self.assertEqual(pl.check_drift(root)["status"], "pass")


def json_lock_hash() -> str:
    import json

    return json.loads(pl.lock_path(REPO).read_text(encoding="utf-8"))["tables_sha256"]


class PythonDecisionTests(unittest.TestCase):
    def test_table_is_exhaustive(self) -> None:
        rows = pl.python_decisions()
        n = len(policy_states.LIFECYCLE_STATES)
        self.assertEqual(len(rows), n * n * 2)

    def test_known_decisions(self) -> None:
        rows = pl.python_decisions()
        self.assertEqual(rows[("candidate", "sandbox_evaluated", 0)], 1)  # no Captain needed
        self.assertEqual(rows[("shadowed", "approved", 0)], 0)  # Captain required
        self.assertEqual(rows[("shadowed", "approved", 1)], 1)
        self.assertEqual(rows[("candidate", "approved", 1)], 0)  # skips stages
        for t in policy_states.LIFECYCLE_STATES:
            for cap in (0, 1):
                self.assertEqual(rows[("retired", t, cap)], 0)  # terminal

    def test_parse_roundtrip_and_errors(self) -> None:
        parsed = pl.parse_model_table("candidate retired 1 1\n\nactive proven 0 0\n")
        self.assertEqual(parsed[("candidate", "retired", 1)], 1)
        self.assertEqual(parsed[("active", "proven", 0)], 0)
        with self.assertRaises(ValueError):
            pl.parse_model_table("candidate retired 1\n")
        with self.assertRaises(ValueError):
            pl.parse_model_table("a b 2 1\n")

    def test_compare_detects_mismatch_and_gaps(self) -> None:
        py = {("a", "b", 0): 1, ("a", "b", 1): 1}
        self.assertEqual(pl.compare_tables(py, dict(py)), [])
        self.assertEqual(len(pl.compare_tables(py, {("a", "b", 0): 0, ("a", "b", 1): 1})), 1)
        self.assertTrue(pl.compare_tables(py, {("a", "b", 0): 1})[0].startswith("missing in model"))
        extra = dict(py)
        extra[("a", "c", 0)] = 0
        self.assertTrue(any(d.startswith("missing in python") for d in pl.compare_tables(py, extra)))


class MutantDefinitionTests(unittest.TestCase):
    """Mutants must apply to the shipped model; a renamed anchor fails loudly."""

    def test_every_model_mutant_changes_the_model(self) -> None:
        original = (FORMAL / "Model.bend").read_text(encoding="utf-8")
        for m in pl.MODEL_MUTANTS:
            with self.subTest(m.mutant_id):
                self.assertNotEqual(m.apply(original), original)

    def test_missing_anchor_raises(self) -> None:
        with self.assertRaises(pl.MutationError):
            pl.set_legal("def legal(f, t):\n  x\n", "candidate", "active", True)

    def test_mutant_ids_unique(self) -> None:
        ids = [m.mutant_id for m in pl.MODEL_MUTANTS]
        self.assertEqual(len(ids), len(set(ids)))


class CheckWithoutToolTests(unittest.TestCase):
    def test_skipped_when_tool_absent(self) -> None:
        result = pl.check(REPO, write_evidence=False, toolchain=None)
        self.assertEqual(result["status"], "skipped")
        self.assertFalse(result["authority_mutation"])
        self.assertFalse(result["approved_for_execution"])

    def test_require_tool_fails_when_absent(self) -> None:
        result = pl.check(REPO, write_evidence=False, toolchain=None, require_tool=True)
        self.assertEqual(result["status"], "fail")

    def test_discover_honours_explicit_missing_binary(self) -> None:
        with mock.patch.dict(os.environ, {"COMPASS_BEND_BIN": "/nonexistent/bend"}):
            self.assertIsNone(discover(REPO))


class LawIntegrityTests(unittest.TestCase):
    def test_absent_on_base_is_not_a_change(self) -> None:
        result = pl.law_integrity(REPO, base_ref="refs/does-not-exist")
        self.assertFalse(result["changed"])
        self.assertEqual({v["base"] for v in result["files"].values()}, {"absent"})

    def test_modified_laws_flagged_against_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import subprocess

            for name in pl.CAPTAIN_OWNED:
                dst = root / pl.FORMAL_REL / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text((FORMAL / name).read_text(encoding="utf-8"), encoding="utf-8")
            run = lambda *a: subprocess.run(a, cwd=root, check=True, capture_output=True)  # noqa: E731
            run("git", "init", "-q")
            run("git", "add", ".")
            run("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
            self.assertFalse(pl.law_integrity(root, base_ref="HEAD")["changed"])
            laws = root / pl.FORMAL_REL / "LAWS.bend"
            laws.write_text(laws.read_text(encoding="utf-8") + "\n# weakened\n", encoding="utf-8")
            result = pl.law_integrity(root, base_ref="HEAD")
            self.assertTrue(result["changed"])
            self.assertTrue(result["needs_captain_review"])
            self.assertTrue(result["files"]["LAWS.bend"]["changed"])
            self.assertFalse(result["files"]["SPEC.bend"]["changed"])


@needs_bend
class BendEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = pl.check(REPO, write_evidence=False)

    def test_overall_ok(self) -> None:
        self.assertEqual(self.result["status"], "ok", self.result.get("failures"))

    def test_proofs_pass_with_kernel_verdict_when_lean_present(self) -> None:
        self.assertEqual(self.result["proofs"]["status"], "pass", self.result["proofs"]["output"])

    def test_python_matches_model_exhaustively(self) -> None:
        conf = self.result["conformance"]
        self.assertEqual(conf["status"], "pass", conf["diffs"])
        self.assertEqual(conf["rows"], 98)

    def test_all_mutants_rejected(self) -> None:
        muts = self.result["mutations"]
        self.assertEqual(muts["uncaught"], [])
        self.assertEqual(muts["caught"], muts["injected"])
        self.assertEqual(muts["python_mutants_detected_by_drift_lock"], 5)

    def test_mutants_tripped_the_expected_law(self) -> None:
        expect = {
            "skip-stage": "p1_pipeline",
            "backward-edge": "p1_pipeline",
            "evidence-drop-shadow-present": "p7c_approved_needs_shadow_present",
            "evidence-drop-proven": "p7d_proven_needs_proven_ok",
        }
        rows = {r["mutant_id"]: r for r in self.result["mutations"]["rows"]}
        for mutant_id, law in expect.items():
            with self.subTest(mutant_id):
                self.assertIn("proofs", rows[mutant_id]["caught_by"])
                self.assertEqual(rows[mutant_id]["first_failed_law"], law)

    def test_evidence_record_has_provenance(self) -> None:
        self.assertEqual(len(self.result["toolchain"]["bend_sha256"]), 64)
        self.assertEqual(set(self.result["files"]), set(pl.BEND_FILES))
        self.assertFalse(self.result["authority_mutation"])


if __name__ == "__main__":
    unittest.main()
