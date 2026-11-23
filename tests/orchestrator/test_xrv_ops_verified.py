"""XRV ops-verified: hermetic EER + cycle reconstruct (#310)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.xrv import eer

REPO = Path(__file__).resolve().parents[2]
OPS_FIXTURE = REPO / ".agent/evidence/xrv/eer-ops-verified-hermetic.json"
I6_FIXTURE = REPO / ".agent/evidence/xrv/eer-i6-cross-provider-fixture.json"


class OpsVerifiedEerTests(unittest.TestCase):
    def _with_schema(self, root: Path) -> None:
        schema_dir = root / "orchestrator" / "schemas"
        schema_dir.mkdir(parents=True)
        schema_dir.joinpath("experience-evidence-record.schema.json").write_text(
            (
                REPO / "orchestrator/schemas/experience-evidence-record.schema.json"
            ).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def test_ops_fixture_validates(self) -> None:
        self.assertTrue(OPS_FIXTURE.is_file())
        with mock.patch.dict(
            os.environ, {"COMPASS_XRV_EER_ENABLED": "1"}, clear=False
        ):
            result = eer.validate_eer_path(REPO, OPS_FIXTURE, require_gate=True)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["lifecycle_state"], "operationally_verified")
        self.assertEqual(result["ops_verification"]["smoke_id"], "hermetic-ops-smoke-310")
        self.assertIs(result["ops_verification"]["live_deploy"], False)
        self.assertIs(result["approved_for_execution"], False)
        self.assertIs(result["auto_promoted"], False)

    def test_ops_verified_requires_ops_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            doc = json.loads(OPS_FIXTURE.read_text(encoding="utf-8"))
            del doc["ops_verification"]
            path = root / "bad.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with mock.patch.dict(
                os.environ, {"COMPASS_XRV_EER_ENABLED": "1"}, clear=False
            ):
                with self.assertRaises(Exception):
                    eer.validate_eer_path(root, path, require_gate=True)

    def test_reconstruct_ops_cycle_complete(self) -> None:
        with mock.patch.dict(
            os.environ, {"COMPASS_XRV_EER_ENABLED": "1"}, clear=False
        ):
            result = eer.reconstruct_eer_path(REPO, OPS_FIXTURE, require_gate=True)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["ops_verified"])
        self.assertTrue(result["cycle_complete_for_state"])
        stages = [s["stage"] for s in result["stages"]]
        self.assertEqual(
            stages,
            [
                "issue",
                "plan",
                "implement",
                "validate",
                "review",
                "merge",
                "operationally_verified",
            ],
        )
        ops_stage = result["stages"][-1]
        self.assertTrue(ops_stage["present"])
        self.assertEqual(
            ops_stage["ops_verification"]["smoke_id"], "hermetic-ops-smoke-310"
        )
        self.assertIs(ops_stage["ops_verification"]["live_deploy"], False)
        self.assertIs(result["approved_for_execution"], False)

    def test_reconstruct_merged_fixture_not_ops_verified(self) -> None:
        doc = json.loads(I6_FIXTURE.read_text(encoding="utf-8"))
        result = eer.reconstruct_cycle(doc)
        self.assertEqual(result["lifecycle_state"], "merged")
        self.assertFalse(result["ops_verified"])
        self.assertTrue(result["cycle_complete_for_state"])
        ops_stage = next(
            s for s in result["stages"] if s["stage"] == "operationally_verified"
        )
        self.assertFalse(ops_stage["present"])


if __name__ == "__main__":
    unittest.main()
