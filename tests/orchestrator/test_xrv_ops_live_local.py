"""XRV live-local ops smoke tests (#316)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.xrv import live_local

REPO = Path(__file__).resolve().parents[2]
FAKE_SHA = "abcdef0123456789abcdef0123456789abcdef01"


class LiveLocalSmokeTests(unittest.TestCase):
    def _with_schema(self, root: Path) -> None:
        schema_dir = root / "orchestrator" / "schemas"
        schema_dir.mkdir(parents=True)
        src = REPO / "orchestrator/schemas/experience-evidence-record.schema.json"
        schema_dir.joinpath("experience-evidence-record.schema.json").write_text(
            src.read_text(encoding="utf-8"), encoding="utf-8"
        )

    def test_smoke_binds_real_tip_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            with mock.patch.dict(
                os.environ, {"COMPASS_XRV_EER_ENABLED": "1"}, clear=False
            ):
                result = live_local.run_live_local_smoke(
                    root,
                    require_gate=True,
                    tip_sha=FAKE_SHA,
                    run_doctor=False,
                    smoke_id="unit-live-local",
                )
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["repository_sha"], FAKE_SHA)
            self.assertIs(result["live_deploy"], False)
            self.assertTrue(result["ops_verified"])
            self.assertIs(result["approved_for_execution"], False)
            self.assertIs(result["auto_promoted"], False)
            eer_path = Path(result["eer_path"])
            self.assertTrue(eer_path.is_file())
            eer = json.loads(eer_path.read_text(encoding="utf-8"))
            self.assertEqual(eer["commit_sha"], FAKE_SHA)
            self.assertEqual(eer["ops_verification"]["repository_sha"], FAKE_SHA)
            self.assertIs(eer["ops_verification"]["live_deploy"], False)
            self.assertEqual(eer["lifecycle_state"], "operationally_verified")

    def test_refuse_production_live_deploy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            with mock.patch.dict(
                os.environ,
                {"COMPASS_XRV_EER_ENABLED": "1", "COMPASS_XRV_LIVE_DEPLOY": "1"},
                clear=False,
            ):
                with self.assertRaises(live_local.LiveLocalError):
                    live_local.run_live_local_smoke(
                        root,
                        require_gate=True,
                        tip_sha=FAKE_SHA,
                        run_doctor=False,
                        smoke_id="unit-refuse-live",
                    )

    def test_gate_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ.pop("COMPASS_XRV_EER_ENABLED", None)
                with self.assertRaises(PermissionError):
                    live_local.run_live_local_smoke(
                        Path(tmp),
                        require_gate=True,
                        tip_sha=FAKE_SHA,
                        run_doctor=False,
                    )


if __name__ == "__main__":
    unittest.main()
