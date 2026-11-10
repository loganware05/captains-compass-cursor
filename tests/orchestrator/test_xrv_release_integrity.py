"""XRV W1: release drift + Experience Evidence Record validation."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.xrv import eer, release_drift

REPO = Path(__file__).resolve().parents[2]


class ReleaseDriftTests(unittest.TestCase):
    def test_matching_versions_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "VERSION").write_text("1.83.1\n", encoding="utf-8")
            (root / "README.md").write_text(
                "# Demo\n\n## Current version: 1.83.1\n\nBody\n",
                encoding="utf-8",
            )
            report = release_drift.check_release_document_drift(root)
            self.assertTrue(report["ok"])
            self.assertEqual(report["version"], "1.83.1")
            self.assertEqual(report["readme_version"], "1.83.1")
            self.assertIs(report["issues_auto_closed"], False)

    def test_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "VERSION").write_text("1.83.1\n", encoding="utf-8")
            (root / "README.md").write_text(
                "## Current version: 1.76.0\n",
                encoding="utf-8",
            )
            report = release_drift.check_release_document_drift(root)
            self.assertFalse(report["ok"])
            self.assertTrue(any("does not match" in f for f in report["findings"]))


class EerValidationTests(unittest.TestCase):
    def _with_schema(self, root: Path) -> None:
        schema_dir = root / "orchestrator" / "schemas"
        schema_dir.mkdir(parents=True)
        schema_dir.joinpath("experience-evidence-record.schema.json").write_text(
            (
                REPO / "orchestrator/schemas/experience-evidence-record.schema.json"
            ).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def test_disabled_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "eer.json"
            path.write_text("{}", encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ.pop("COMPASS_XRV_EER_ENABLED", None)
                with self.assertRaises(PermissionError):
                    eer.validate_eer_path(root, path, require_gate=True)

    def test_i6_fixture_validates(self) -> None:
        fixture = REPO / ".agent/evidence/xrv/eer-i6-cross-provider-fixture.json"
        self.assertTrue(fixture.is_file())
        with mock.patch.dict(
            os.environ, {"COMPASS_XRV_EER_ENABLED": "1"}, clear=False
        ):
            result = eer.validate_eer_path(REPO, fixture, require_gate=True)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["lifecycle_state"], "merged")
        self.assertIs(result["approved_for_execution"], False)
        self.assertIs(result["auto_promoted"], False)

    def test_authority_lock_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            doc = json.loads(
                (
                    REPO / ".agent/evidence/xrv/eer-i6-cross-provider-fixture.json"
                ).read_text(encoding="utf-8")
            )
            doc["approved_for_execution"] = True
            path = root / "bad.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with mock.patch.dict(
                os.environ, {"COMPASS_XRV_EER_ENABLED": "1"}, clear=False
            ):
                with self.assertRaises(Exception):
                    eer.validate_eer_path(root, path, require_gate=True)


if __name__ == "__main__":
    unittest.main()
