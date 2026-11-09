"""I6 hermetic cross-provider validation harness."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.integrations.i6 import service

REPO = Path(__file__).resolve().parents[2]


class I6ValidationTests(unittest.TestCase):
    def _with_schema(self, root: Path) -> None:
        schema_dir = root / "orchestrator" / "schemas"
        schema_dir.mkdir(parents=True)
        schema_dir.joinpath("i6-cross-provider-scorecard.schema.json").write_text(
            (
                REPO / "orchestrator/schemas/i6-cross-provider-scorecard.schema.json"
            ).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def test_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ.pop("COMPASS_I6_VALIDATE_ENABLED", None)
                with self.assertRaises(PermissionError):
                    service.run(Path(tmp), write_evidence=False)

    def test_hermetic_run_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            with mock.patch.dict(
                os.environ, {"COMPASS_I6_VALIDATE_ENABLED": "1"}, clear=False
            ):
                result = service.run(root, write_evidence=True)
            self.assertEqual(result["status"], "ok")
            scorecard = result["scorecard"]
            self.assertEqual(scorecard["provider"], "i6")
            self.assertEqual(scorecard["mode"], "hermetic")
            self.assertIs(scorecard["approved_for_execution"], False)
            self.assertEqual(scorecard["failed"], 0)
            self.assertEqual(scorecard["passed"], 5)
            self.assertEqual(len(scorecard["providers"]), 5)
            self.assertTrue(Path(result["path"]).is_file())


if __name__ == "__main__":
    unittest.main()
