"""XRV W2: eight-pillar readiness assessor."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.xrv import readiness

REPO = Path(__file__).resolve().parents[2]


class XrvReadinessTests(unittest.TestCase):
    def _with_schema(self, root: Path) -> None:
        schema_dir = root / "orchestrator" / "schemas"
        schema_dir.mkdir(parents=True)
        schema_dir.joinpath("xrv-readiness-scorecard.schema.json").write_text(
            (
                REPO / "orchestrator/schemas/xrv-readiness-scorecard.schema.json"
            ).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def test_disabled_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ.pop("COMPASS_XRV_READINESS_ENABLED", None)
                with self.assertRaises(PermissionError):
                    readiness.assess_readiness(
                        Path(tmp), require_gate=True, write_evidence=False
                    )

    def test_control_repo_hermetic(self) -> None:
        with mock.patch.dict(
            os.environ, {"COMPASS_XRV_READINESS_ENABLED": "1"}, clear=False
        ):
            result = readiness.assess_readiness(
                REPO, require_gate=True, write_evidence=False
            )
        self.assertEqual(result["status"], "ok")
        sc = result["scorecard"]
        self.assertEqual(sc["mode"], "hermetic")
        self.assertIs(sc["approved_for_execution"], False)
        self.assertIs(sc["scores_invented"], False)
        self.assertEqual(len(sc["repository_readiness"]["pillars"]), 8)
        self.assertGreaterEqual(sc["repository_readiness"]["scored_count"], 1)
        self.assertIn(
            sc["northstar_effectiveness"]["overall_status"],
            {"effective", "partial", "blocked", "unscored"},
        )

    def test_empty_repo_unscored_not_invented(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            with mock.patch.dict(
                os.environ, {"COMPASS_XRV_READINESS_ENABLED": "1"}, clear=False
            ):
                result = readiness.assess_readiness(
                    root, require_gate=True, write_evidence=False
                )
            sc = result["scorecard"]
            self.assertIs(sc["scores_invented"], False)
            self.assertEqual(sc["repository_readiness"]["scored_count"], 0)
            self.assertEqual(sc["repository_readiness"]["overall_status"], "unscored")
            self.assertIsNone(sc["repository_readiness"]["overall_score"])


if __name__ == "__main__":
    unittest.main()
