"""Hermetic tests for additive COMPASS_PROFILE v0."""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.env_profiles import (
    PROFILE_ENV,
    ProfileError,
    apply_profile,
    expand_profile,
    export_shell,
    list_profiles,
)

ROOT = Path(__file__).resolve().parents[2]


class ExpandTests(unittest.TestCase):
    def test_known_profiles(self) -> None:
        self.assertEqual(list_profiles(), ["core", "integrations"])
        core = expand_profile("core")
        self.assertEqual(core["COMPASS_STATUS_ENABLED"], "1")
        self.assertEqual(core["COMPASS_BRAIN_ENABLED"], "1")
        integ = expand_profile("integrations")
        self.assertEqual(integ["COMPASS_SENTRY_INGEST_ENABLED"], "1")
        # Live dual-gates must never ship in profile defaults.
        self.assertNotIn("COMPASS_SENTRY_LIVE", integ)
        self.assertNotIn("COMPASS_T3_LIVE", integ)

    def test_unknown_profile(self) -> None:
        with self.assertRaises(ProfileError):
            expand_profile("nope")


class ApplyTests(unittest.TestCase):
    def test_additive_does_not_overwrite(self) -> None:
        env = {"COMPASS_STATUS_ENABLED": "0"}
        applied = apply_profile("core", environ=env, overwrite=False)
        self.assertNotIn("COMPASS_STATUS_ENABLED", applied)
        self.assertEqual(env["COMPASS_STATUS_ENABLED"], "0")
        self.assertEqual(env["COMPASS_BRAIN_ENABLED"], "1")
        self.assertIn("COMPASS_BRAIN_ENABLED", applied)

    def test_applies_when_unset(self) -> None:
        env: dict[str, str] = {}
        applied = apply_profile("integrations", environ=env)
        self.assertEqual(env["COMPASS_SENTRY_INGEST_ENABLED"], "1")
        self.assertEqual(applied["COMPASS_SENTRY_INGEST_ENABLED"], "1")

    def test_env_var_name(self) -> None:
        with mock.patch.dict(os.environ, {PROFILE_ENV: "core"}, clear=False):
            gates = expand_profile()
            self.assertIn("COMPASS_STATUS_ENABLED", gates)

    def test_export_shell_lines(self) -> None:
        text = export_shell("core", environ={})
        self.assertIn("export COMPASS_STATUS_ENABLED=1", text)
        self.assertIn("export COMPASS_BRAIN_ENABLED=1", text)


class CliTests(unittest.TestCase):
    def test_northstar_profile_list(self) -> None:
        proc = subprocess.run(
            [str(ROOT / "scripts" / "northstar"), "profile", "list"],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("core", proc.stdout)
        self.assertIn("integrations", proc.stdout)

    def test_northstar_profile_export(self) -> None:
        proc = subprocess.run(
            [str(ROOT / "scripts" / "northstar"), "profile", "export", "integrations"],
            capture_output=True,
            text=True,
            check=False,
            env={
                **os.environ,
                "PYTHONPATH": str(ROOT),
                # Clear integration gates so export emits them.
                "COMPASS_SENTRY_INGEST_ENABLED": "",
                "COMPASS_T3_EXEC_ENABLED": "",
                "COMPASS_APIFY_ENABLED": "",
                "COMPASS_EXPLAIN_ENABLED": "",
                "COMPASS_IDENTITY_ENABLED": "",
                "COMPASS_I6_VALIDATE_ENABLED": "",
                "COMPASS_CONVERSATION_INGEST_ENABLED": "",
            },
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("COMPASS_SENTRY_INGEST_ENABLED=1", proc.stdout)


if __name__ == "__main__":
    unittest.main()
