"""Bend proof spike (#278): policy-lifecycle conformance, drift, hardening, mutation controls.

Pure-Python tests always run. Tests that execute Bend require *all* of: the
toolchain, Lean (for ``--verdict``), and ``COMPASS_BEND_PROOF_ENABLED=1`` (the
experiment is opt-in), so default CI and doctor behave exactly as before.
"""

from __future__ import annotations

import inspect
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.behavior.policy import promote as policy_promote
from orchestrator.behavior.policy import states as policy_states
from orchestrator.formal import policy_lifecycle as pl
from orchestrator.formal import toolchain as tcmod
from orchestrator.formal.gates import require_bend_proof_enabled

REPO = Path(__file__).resolve().parents[2]
FORMAL = REPO / pl.FORMAL_REL
GATE_ON = {"COMPASS_BEND_PROOF_ENABLED": "1"}


def _optional_toolchain():
    try:
        return tcmod.discover(REPO)
    except tcmod.ToolchainError:
        return None


TOOLCHAIN = _optional_toolchain()
E2E_READY = bool(
    TOOLCHAIN
    and TOOLCHAIN.lean_version()
    and (os.environ.get("COMPASS_BEND_PROOF_ENABLED") or "").strip().lower() in {"1", "true", "yes", "on"}
)
needs_bend = unittest.skipUnless(
    E2E_READY, "needs Bend + Lean and COMPASS_BEND_PROOF_ENABLED=1 (opt-in experiment)"
)


def lock_hash() -> str:
    import json

    return json.loads(pl.lock_path(REPO).read_text(encoding="utf-8"))["tables_sha256"]


class GateTests(unittest.TestCase):
    def test_disabled_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(PermissionError):
                require_bend_proof_enabled()

    def test_enabled_values(self) -> None:
        for value in ("1", "true", "YES", "on"):
            with mock.patch.dict(os.environ, {"COMPASS_BEND_PROOF_ENABLED": value}, clear=True):
                require_bend_proof_enabled()

    def test_library_entry_points_enforce_the_gate(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(PermissionError):
                pl.check(REPO, write_evidence=False, toolchain=None)
            with self.assertRaises(PermissionError):
                pl.write_lock(REPO)


class StructureTests(unittest.TestCase):
    def test_real_promote_structure(self) -> None:
        st = pl.promote_structure()
        self.assertTrue(st["legality"])
        self.assertTrue(st["captain"])
        self.assertTrue(st["order_ok"])
        self.assertEqual(
            st["evidence"],
            {
                "approved": ["shadow_present"],
                "proven": ["proven_ok"],
                "sandbox_evaluated": ["eval_pass"],
                "shadowed": ["shadow_ok"],
            },
        )

    def test_source_edits_change_the_structure(self) -> None:
        src = inspect.getsource(policy_promote.promote_policy)
        base = pl.structure_from_source(src)
        for m in pl._python_mutants():
            if not m.source_edit:
                continue
            with self.subTest(m.mutant_id):
                old, new = m.source_edit
                self.assertIn(old, src)
                self.assertNotEqual(pl.structure_from_source(src.replace(old, new, 1)), base)

    def test_reordering_breaks_order_flag(self) -> None:
        src = inspect.getsource(policy_promote.promote_policy)
        a = "        require_captain_approved(to_state, captain_approved=captain_approved)\n"
        self.assertIn(a, src)
        moved = src.replace(a, "        pass\n", 1).replace(
            "    if not can_transition(from_state, to_state):",
            f"    {a.strip()}\n    if not can_transition(from_state, to_state):", 1)
        self.assertNotEqual(moved, src)
        self.assertFalse(pl.structure_from_source(moved)["order_ok"])


class StructureEvasionTests(unittest.TestCase):
    """Edits that keep the same gates *called* but change behavior must still trip the pin."""

    def test_evasions_are_invisible_to_the_flags_but_not_the_pin(self) -> None:
        src = inspect.getsource(policy_promote.promote_policy)
        base = pl.promote_structure()
        evasions = [m for m in pl._python_mutants() if not m.grid_visible]
        self.assertGreaterEqual(len(evasions), 6)
        for m in evasions:
            with self.subTest(m.mutant_id):
                old, new = m.source_edit
                self.assertIn(old, src)
                mutated = pl.promote_structure(src.replace(old, new, 1))
                flags = lambda st: {k: v for k, v in st.items() if k != "ast_sha256"}  # noqa: E731
                self.assertEqual(flags(mutated), flags(base), "extractor flags should not see this edit")
                self.assertNotEqual(mutated["ast_sha256"], base["ast_sha256"])

    def test_comment_only_edits_do_not_trip_the_pin(self) -> None:
        src = inspect.getsource(policy_promote.promote_policy)
        anchor = '    from_state = str(policy.get("lifecycle_state") or "candidate")\n'
        self.assertIn(anchor, src)
        edited = src.replace(anchor, "    # harmless comment\n" + anchor, 1)
        self.assertNotEqual(edited, src)
        self.assertEqual(pl.promote_structure(edited), pl.promote_structure())

    def test_fingerprint_ignores_empty_and_none_fields(self) -> None:
        import ast

        fn = ast.parse("def f(a):\n    return a\n").body[0]
        before = pl._ast_canonical(fn)
        fn.type_params = []  # added in 3.12; absent or empty must hash the same
        fn.returns = None
        self.assertEqual(pl._ast_canonical(fn), before)
        self.assertNotIn("type_params", before)
        self.assertNotIn("returns", before)

    def test_shadowed_gate_functions_break_binding_identity(self) -> None:
        self.assertTrue(pl.promote_structure()["bindings_ok"])
        with mock.patch.object(policy_promote, "can_transition", lambda f, t: True):
            self.assertFalse(pl.promote_structure()["bindings_ok"])
            self.assertEqual(pl.check_drift(REPO)["status"], "fail")
        with mock.patch.object(policy_promote, "require_captain_approved", lambda *a, **k: None):
            self.assertFalse(pl.promote_structure()["bindings_ok"])


class TablesAndDriftTests(unittest.TestCase):
    def test_lock_matches_python(self) -> None:
        result = pl.check_drift(REPO)
        self.assertEqual(result["status"], "pass", result)

    def test_drift_when_transitions_change(self) -> None:
        mutated = dict(policy_states.TRANSITIONS)
        mutated["candidate"] = mutated["candidate"] | {"active"}
        with pl.patched_python_tables(transitions=mutated):
            self.assertNotEqual(pl.tables_sha256(), lock_hash())
            self.assertEqual(pl.check_drift(REPO)["status"], "fail")

    def test_drift_when_captain_set_changes(self) -> None:
        with pl.patched_python_tables(captain_required=policy_states.CAPTAIN_REQUIRED - {"approved"}):
            self.assertEqual(pl.check_drift(REPO)["status"], "fail")

    def test_drift_when_promote_structure_changes(self) -> None:
        fake = dict(pl.promote_structure())
        fake["captain"] = False
        with mock.patch.object(pl, "promote_structure", return_value=fake):
            self.assertEqual(pl.check_drift(REPO)["status"], "fail")

    def test_missing_lock_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(pl.check_drift(Path(tmp))["status"], "fail")

    def test_write_lock_roundtrip_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(FORMAL, root / pl.FORMAL_REL)
            with mock.patch.dict(os.environ, GATE_ON):
                pl.write_lock(root)
            self.assertEqual(pl.check_drift(root)["status"], "pass")
            # Deleting a law *and* its proof together must trip the manifest.
            d = root / pl.FORMAL_REL
            laws = (d / "LAWS.bend").read_text(encoding="utf-8")
            start = laws.index("law p5_shadow_before_approval:")
            end = laws.index("# P6", start)
            (d / "LAWS.bend").write_text(laws[:start] + laws[end:], encoding="utf-8")
            proof = (d / "PROOF.bend").read_text(encoding="utf-8")
            start = proof.index("def Laws.p5_shadow_before_approval(")
            end = proof.index("def Laws.", start + 10)
            (d / "PROOF.bend").write_text(proof[:start] + proof[end:], encoding="utf-8")
            result = pl.check_drift(root)
            self.assertEqual(result["status"], "fail")
            self.assertIn("p5_shadow_before_approval", result["reason"])

    def test_conformance_and_model_files_are_locked(self) -> None:
        for name in pl.LOCKED_FILES:
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                shutil.copytree(FORMAL, root / pl.FORMAL_REL)
                with mock.patch.dict(os.environ, GATE_ON):
                    pl.write_lock(root)
                self.assertEqual(pl.check_drift(root)["status"], "pass")
                target = root / pl.FORMAL_REL / name
                target.write_text(target.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
                result = pl.check_drift(root)
                self.assertEqual(result["status"], "fail")
                self.assertIn(name, result["reason"])

    def test_liveness_law_exists_and_is_proved(self) -> None:
        names = pl.law_names(REPO)
        self.assertIn("p11_liveness", names["laws"])
        self.assertIn("p11_liveness", names["proofs"])

    def test_law_without_proof_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(FORMAL, root / pl.FORMAL_REL)
            with mock.patch.dict(os.environ, GATE_ON):
                pl.write_lock(root)
            d = root / pl.FORMAL_REL
            (d / "LAWS.bend").write_text(
                (d / "LAWS.bend").read_text(encoding="utf-8")
                + "\nlaw extra_open:\n  for +t: M.State\n  {S.is_retired(t) == S.is_retired(t) : Bool}\n",
                encoding="utf-8",
            )
            self.assertEqual(pl.check_drift(root)["status"], "fail")


class PythonDecisionTests(unittest.TestCase):
    def test_grid_is_exhaustive(self) -> None:
        n = len(policy_states.LIFECYCLE_STATES)
        self.assertEqual(len(pl.python_decisions()), n * n * 2 * 16)

    def test_known_decisions(self) -> None:
        rows = pl.python_decisions()
        self.assertEqual(rows[("candidate", "sandbox_evaluated", 0, "1000")], 1)
        self.assertEqual(rows[("candidate", "sandbox_evaluated", 0, "0000")], 0)  # needs eval_pass
        self.assertEqual(rows[("shadowed", "approved", 0, "0010")], 0)  # needs the Captain
        self.assertEqual(rows[("shadowed", "approved", 1, "0000")], 0)  # needs shadow_present
        self.assertEqual(rows[("shadowed", "approved", 1, "0010")], 1)
        self.assertEqual(rows[("candidate", "approved", 1, "1111")], 0)  # skips stages
        for t in policy_states.LIFECYCLE_STATES:
            for bits in pl.PRE_COMBOS:
                self.assertEqual(rows[("retired", t, 1, bits)], 0)  # terminal

    def test_parse_roundtrip_and_errors(self) -> None:
        parsed = pl.parse_model_table("candidate retired 1 0000 1\n\nactive proven 0 0001 0\n")
        self.assertEqual(parsed[("candidate", "retired", 1, "0000")], 1)
        for bad in ("candidate retired 1 1\n", "a b 2 0000 1\n", "a b 1 000 1\n", "a b 1 0000 2\n"):
            with self.assertRaises(ValueError):
                pl.parse_model_table(bad)
        with self.assertRaises(ValueError):
            pl.parse_model_table("a b 1 0000 1\na b 1 0000 0\n")  # duplicate row

    def test_compare_detects_mismatch_and_gaps(self) -> None:
        py = {("a", "b", 0, "0000"): 1, ("a", "b", 1, "0000"): 1}
        self.assertEqual(pl.compare_tables(py, dict(py)), [])
        self.assertEqual(len(pl.compare_tables(py, {("a", "b", 0, "0000"): 0, ("a", "b", 1, "0000"): 1})), 1)
        self.assertTrue(pl.compare_tables(py, {("a", "b", 0, "0000"): 1})[0].startswith("missing in model"))
        extra = dict(py)
        extra[("a", "c", 0, "0000")] = 0
        self.assertTrue(any(d.startswith("missing in python") for d in pl.compare_tables(py, extra)))


class MutantDefinitionTests(unittest.TestCase):
    def test_every_model_mutant_changes_the_model(self) -> None:
        original = (FORMAL / "Model.bend").read_text(encoding="utf-8")
        for m in pl.MODEL_MUTANTS:
            with self.subTest(m.mutant_id):
                self.assertNotEqual(m.apply(original), original)

    def test_missing_anchor_raises(self) -> None:
        with self.assertRaises(pl.MutationError):
            pl.set_legal("def legal(f, t):\n  x\n", "candidate", "active", True)

    def test_ids_unique(self) -> None:
        ids = [m.mutant_id for m in pl.MODEL_MUTANTS] + [m.mutant_id for m in pl._python_mutants()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_mutants_target_the_intended_case_only(self) -> None:
        original = (FORMAL / "Model.bend").read_text(encoding="utf-8")
        mutated = pl.pre_ok_edit(original, "active", "      True{}\n", "      False{}\n")
        a, b = pl._function_slice(original, "pre_ok")
        # Everything outside pre_ok must be byte-identical.
        self.assertEqual(mutated[:a], original[:a])
        self.assertEqual(mutated[len(mutated) - (len(original) - b):], original[b:])
        self.assertNotEqual(mutated[a:], original[a:])
        self.assertEqual(mutated.count("False{}"), original.count("False{}") + 1)


class ToolchainHardeningTests(unittest.TestCase):
    def _fake_bend(self, tmp: Path, body: str) -> Path:
        path = tmp / "bend"
        path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def test_environment_is_allowlisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake = self._fake_bend(Path(tmp), "env\n")
            env = {"PATH": "/usr/bin:/bin", "AWS_SECRET_ACCESS_KEY": "s3cret", "GITHUB_TOKEN": "tok",
                   "HOME": "/home/should-not-leak", "USER": "nobody-leak", "COMPASS_BEND_BIN": str(fake)}
            with mock.patch.dict(os.environ, env, clear=True):
                tc = tcmod.discover(REPO)
                out = tc.run([], cwd=Path(tmp))["stdout"]
            self.assertNotIn("s3cret", out)
            self.assertNotIn("GITHUB_TOKEN", out)
            self.assertNotIn("should-not-leak", out)
            self.assertNotIn("nobody-leak", out)
            self.assertIn("BEND_NO_TELEMETRY=1", out)

    def test_sha_pin_mismatch_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake = self._fake_bend(Path(tmp), "echo hi\n")
            env = {"PATH": "/usr/bin:/bin", "COMPASS_BEND_BIN": str(fake), "COMPASS_BEND_SHA256": "0" * 64}
            with mock.patch.dict(os.environ, env, clear=True):
                with self.assertRaises(tcmod.ToolchainError):
                    tcmod.discover(REPO)

    def test_sha_pin_match_is_accepted(self) -> None:
        import hashlib

        with tempfile.TemporaryDirectory() as tmp:
            fake = self._fake_bend(Path(tmp), "echo hi\n")
            digest = hashlib.sha256(fake.read_bytes()).hexdigest()
            env = {"PATH": "/usr/bin:/bin", "COMPASS_BEND_BIN": str(fake), "COMPASS_BEND_SHA256": digest}
            with mock.patch.dict(os.environ, env, clear=True):
                self.assertIsNotNone(tcmod.discover(REPO))

    def test_timeout_kills_the_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake = self._fake_bend(Path(tmp), "sleep 30 &\nsleep 30\n")
            tc = tcmod.Toolchain(bend=fake, env={"PATH": "/usr/bin:/bin"})
            res = tc.run([], cwd=Path(tmp), timeout=1)
            self.assertEqual(res["exit_code"], 124)
            self.assertIn("timeout", res["stderr"])
            self.assertLess(res["seconds"], 10)

    def test_version_tolerates_empty_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake = self._fake_bend(Path(tmp), "exit 0\n")
            self.assertEqual(tcmod.Toolchain(bend=fake, env={"PATH": "/usr/bin:/bin"}).version(), "")

    def test_explicit_missing_binary_is_not_a_silent_skip(self) -> None:
        with mock.patch.dict(os.environ, {**GATE_ON, "COMPASS_BEND_BIN": "/nonexistent/bend"}):
            self.assertIsNone(tcmod.discover(REPO))
            result = pl.check(REPO, write_evidence=False)
        self.assertEqual(result["status"], "fail")
        self.assertIn("toolchain-explicit-missing", result["failures"])


class CheckWithoutToolTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.dict(os.environ, GATE_ON)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("COMPASS_BEND_BIN", None)

    def test_skipped_when_tool_absent(self) -> None:
        result = pl.check(REPO, write_evidence=False, toolchain=None)
        self.assertEqual(result["status"], "skipped")
        self.assertFalse(result["authority_mutation"])
        self.assertFalse(result["approved_for_execution"])

    def test_require_tool_fails_when_absent(self) -> None:
        result = pl.check(REPO, write_evidence=False, toolchain=None, require_tool=True)
        self.assertEqual(result["status"], "fail")

    def test_drift_is_not_hidden_by_a_skip(self) -> None:
        mutated = dict(policy_states.TRANSITIONS)
        mutated["candidate"] = mutated["candidate"] | {"active"}
        with pl.patched_python_tables(transitions=mutated):
            result = pl.check(REPO, write_evidence=False, toolchain=None)
        self.assertEqual(result["status"], "fail")
        self.assertIn("drift", result["failures"])

    def test_strict_laws_fail_closed_on_bad_ref_even_without_tool(self) -> None:
        result = pl.check(REPO, write_evidence=False, toolchain=None, strict_laws=True,
                          base_ref="refs/does-not-exist")
        self.assertEqual(result["status"], "fail")
        self.assertIn("laws-unverified", result["failures"])


class LawIntegrityTests(unittest.TestCase):
    def test_bad_ref_is_an_error_not_clean(self) -> None:
        for ref in ("refs/does-not-exist", "--output=/tmp/x", ""):
            with self.subTest(ref=ref):
                result = pl.law_integrity(REPO, base_ref=ref)
                self.assertEqual(result["status"], "error")
                self.assertIsNone(result["changed"])

    def test_deleted_law_file_is_changed_not_a_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in pl.CAPTAIN_OWNED:
                dst = root / pl.FORMAL_REL / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text((FORMAL / name).read_text(encoding="utf-8"), encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "b"],
                           cwd=root, check=True, capture_output=True)
            (root / pl.FORMAL_REL / "LAWS.bend").unlink()
            result = pl.law_integrity(root, base_ref="HEAD")
            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["changed"])
            self.assertEqual(result["files"]["LAWS.bend"]["sha256"], "missing")

    def test_inherited_git_env_cannot_redirect_the_comparison(self) -> None:
        with mock.patch.dict(os.environ, {"GIT_DIR": "/nonexistent/.git", "GIT_WORK_TREE": "/nonexistent"}):
            result = pl.law_integrity(REPO, base_ref="HEAD")
        self.assertEqual(result["status"], "ok")

    def test_option_like_ref_never_writes_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out"
            pl.law_integrity(REPO, base_ref=f"--output={target}")
            self.assertFalse(target.exists())

    def test_law_files_absent_at_base_count_as_changed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in pl.CAPTAIN_OWNED:
                dst = root / pl.FORMAL_REL / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text((FORMAL / name).read_text(encoding="utf-8"), encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                            "--allow-empty", "-m", "empty"], cwd=root, check=True, capture_output=True)
            result = pl.law_integrity(root, base_ref="HEAD")
            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["changed"])
            self.assertTrue(result["needs_captain_review"])
            self.assertTrue(all(f["base"] == "absent" for f in result["files"].values()))

    def test_modified_laws_flagged_against_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in pl.CAPTAIN_OWNED:
                dst = root / pl.FORMAL_REL / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text((FORMAL / name).read_text(encoding="utf-8"), encoding="utf-8")

            def run(*a: str) -> None:
                subprocess.run(a, cwd=root, check=True, capture_output=True)

            run("git", "init", "-q")
            run("git", "add", ".")
            run("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
            self.assertFalse(pl.law_integrity(root, base_ref="HEAD")["changed"])
            laws = root / pl.FORMAL_REL / "LAWS.bend"
            laws.write_text(laws.read_text(encoding="utf-8") + "\n# weakened\n", encoding="utf-8")
            result = pl.law_integrity(root, base_ref="HEAD")
            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["changed"])
            self.assertTrue(result["needs_captain_review"])
            self.assertTrue(result["files"]["LAWS.bend"]["changed"])
            self.assertFalse(result["files"]["SPEC.bend"]["changed"])
            with mock.patch.dict(os.environ, GATE_ON):
                strict = pl.check(root, write_evidence=False, toolchain=None, strict_laws=True, base_ref="HEAD")
            self.assertIn("laws-changed-vs-base", strict["failures"])


class CliTests(unittest.TestCase):
    def _run(self, *args: str, gate: bool = True) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if k != "COMPASS_BEND_PROOF_ENABLED"}
        if gate:
            env["COMPASS_BEND_PROOF_ENABLED"] = "1"
        return subprocess.run([str(REPO / "scripts" / "northstar"), "formal", *args],
                              capture_output=True, text=True, env=env, cwd="/tmp", timeout=120)

    def test_lock_rejects_flags_it_would_ignore(self) -> None:
        for flag in ("--no-verdict", "--no-mutations", "--no-write", "--require-tool", "--strict-laws"):
            with self.subTest(flag):
                res = self._run("lock", "policy-lifecycle", flag)
                self.assertEqual(res.returncode, 2, res.stderr)
                self.assertIn("lock does not accept", res.stderr)

    def test_base_ref_requires_a_value(self) -> None:
        for args in (("--base-ref",), ("--base-ref", "--x")):
            with self.subTest(args):
                res = self._run("check", "policy-lifecycle", *args)
                self.assertEqual(res.returncode, 2)
                self.assertIn("requires a value", res.stderr)

    def test_gate_off_exits_2(self) -> None:
        res = self._run("check", "policy-lifecycle", gate=False)
        self.assertEqual(res.returncode, 2)
        self.assertIn("disabled", res.stderr)


class KnownGapTests(unittest.TestCase):
    def test_direct_entry_probe_runs_in_isolation(self) -> None:
        before = sorted(p.name for p in (REPO / ".agent").glob("evaluations*"))
        gap = pl.probe_direct_entry()
        after = sorted(p.name for p in (REPO / ".agent").glob("evaluations*"))
        self.assertEqual(before, after)
        self.assertTrue(gap["outside_model"])
        self.assertTrue(gap["authority_flags_false"])
        # Finding 001 production fix (#280): bypass must stay False.
        self.assertFalse(gap["bypass_observed"])
        self.assertEqual(gap["entered_state"], "candidate")
        self.assertIn(gap["entered_state"], policy_states.LIFECYCLE_STATES)
        self.assertIsNone(gap["captain_approved_at"])


@needs_bend
class BendEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = pl.check(REPO, write_evidence=False)

    def test_overall_ok(self) -> None:
        self.assertEqual(self.result["status"], "ok", self.result.get("failures"))

    def test_proofs_pass_with_kernel_verdict(self) -> None:
        self.assertTrue(self.result["proofs"]["verdict"])
        self.assertEqual(self.result["proofs"]["status"], "pass", self.result["proofs"]["output"])

    def test_python_matches_model_exhaustively(self) -> None:
        conf = self.result["conformance"]
        self.assertEqual(conf["status"], "pass", conf["diffs"])
        self.assertEqual(conf["rows"], 1568)
        self.assertEqual(conf["model_rows"], 1568)

    def test_all_mutants_rejected_as_expected(self) -> None:
        muts = self.result["mutations"]
        self.assertEqual(muts["uncaught"], [])
        self.assertEqual(muts["unexpected"], [])
        self.assertEqual(muts["caught"], muts["injected"])
        self.assertEqual(muts["python_mutants_detected_by_drift_lock"], muts["python_mutants"])

    def test_proof_caught_mutants_trip_the_expected_law(self) -> None:
        expected = {m.mutant_id: m.laws for m in pl.MODEL_MUTANTS}
        for row in self.result["mutations"]["rows"]:
            if row["kind"] != "model":
                continue
            with self.subTest(row["mutant_id"]):
                if expected[row["mutant_id"]]:
                    self.assertIn("proofs", row["caught_by"])
                    self.assertIn(row["first_failed_law"], expected[row["mutant_id"]])
                else:
                    # Restrictive mutants: laws are safety-only; the evidence grid catches them.
                    self.assertEqual(row["caught_by"], ["conformance"])

    def test_evasions_are_caught_only_by_the_lock(self) -> None:
        rows = [r for r in self.result["mutations"]["rows"] if r["kind"] == "python"]
        evasions = [r for r in rows if not r["grid_visible"]]
        self.assertGreaterEqual(len(evasions), 6)
        for r in evasions:
            with self.subTest(r["mutant_id"]):
                self.assertEqual(r["caught_by"], ["drift-lock"])
        for r in rows:
            if r["grid_visible"]:
                self.assertIn("conformance", r["caught_by"])

    def test_always_reject_model_is_caught_by_liveness(self) -> None:
        row = next(r for r in self.result["mutations"]["rows"] if r["mutant_id"] == "always-reject")
        self.assertEqual(row["first_failed_law"], "p11_liveness")

    def test_partial_runs_are_marked_degraded(self) -> None:
        partial = pl.check(REPO, write_evidence=False, mutations=False, verdict=False)
        self.assertEqual(partial["status"], "partial")
        self.assertTrue(partial["degraded"])
        self.assertEqual(sorted(partial["skipped_components"]), ["mutations", "verdict"])
        self.assertFalse(self.result["degraded"])

    def test_known_gap_is_recorded(self) -> None:
        self.assertEqual(self.result["known_gaps"][0]["name"], "direct-entry-bypass")

    def test_evidence_record_has_provenance(self) -> None:
        self.assertEqual(len(self.result["toolchain"]["bend_sha256"]), 64)
        self.assertEqual(set(self.result["files"]), set(pl.BEND_FILES))
        self.assertFalse(self.result["authority_mutation"])


if __name__ == "__main__":
    unittest.main()
