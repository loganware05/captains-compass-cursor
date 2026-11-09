"""I4 Scrimba Explain surface (fixture-first)."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.integrations.scrimba import service
from orchestrator.status.development_refs import collect_explainer_refs

REPO = Path(__file__).resolve().parents[2]


class ScrimbaExplainServiceTests(unittest.TestCase):
    def _with_schema(self, root: Path) -> None:
        schema_dir = root / "orchestrator" / "schemas"
        schema_dir.mkdir(parents=True)
        schema_dir.joinpath("scrimba-explainer-packet.schema.json").write_text(
            (
                REPO / "orchestrator/schemas/scrimba-explainer-packet.schema.json"
            ).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def test_create_persist_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            with mock.patch.dict(os.environ, {"COMPASS_EXPLAIN_ENABLED": "1"}, clear=False):
                result = service.create(root, "How NorthStar approval gates work")
                packet = result["packet"]
                self.assertEqual(packet["provider"], "fixture")
                self.assertIs(packet["auto_published"], False)
                self.assertIs(packet["streamed_live"], False)
                self.assertIs(packet["approved_for_execution"], False)
                self.assertGreaterEqual(len(packet["slides"]), 2)
                listed = service.list_packets(root)
                self.assertEqual(listed["count"], 1)
                shown = service.show(root, packet["packet_id"])
                self.assertEqual(shown["packet"]["packet_id"], packet["packet_id"])
            refs = collect_explainer_refs(root)
            self.assertEqual(len(refs), 1)
            self.assertEqual(refs[0]["claim_kind"], "external")

    def test_create_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ.pop("COMPASS_EXPLAIN_ENABLED", None)
                with self.assertRaises(PermissionError):
                    service.create(Path(tmp), "x")

    def test_live_deferred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(
                os.environ,
                {"COMPASS_EXPLAIN_ENABLED": "1", "COMPASS_EXPLAIN_LIVE": "1"},
                clear=False,
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    service.create(Path(tmp), "x", live=True)
                self.assertIn("deferred", str(ctx.exception).lower())

    def test_pr_mcp_endpoint_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            with mock.patch.dict(os.environ, {"COMPASS_EXPLAIN_ENABLED": "1"}, clear=False):
                result = service.create(root, "PR walkthrough", mcp="pr")
            self.assertIn("/explain/pr/mcp", result["packet"]["mcp_endpoint"])


if __name__ == "__main__":
    unittest.main()
