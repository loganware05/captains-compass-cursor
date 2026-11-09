"""I5 WorkOS AuthKit identity surface (fixture-first)."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.integrations.workos import service
from orchestrator.status.development_refs import collect_identity_refs

REPO = Path(__file__).resolve().parents[2]


class WorkOSIdentityServiceTests(unittest.TestCase):
    def _with_schema(self, root: Path) -> None:
        schema_dir = root / "orchestrator" / "schemas"
        schema_dir.mkdir(parents=True)
        schema_dir.joinpath("workos-identity-packet.schema.json").write_text(
            (
                REPO / "orchestrator/schemas/workos-identity-packet.schema.json"
            ).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def test_sync_persist_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            with mock.patch.dict(os.environ, {"COMPASS_IDENTITY_ENABLED": "1"}, clear=False):
                result = service.sync(root)
                packet = result["packet"]
                self.assertEqual(packet["provider"], "workos")
                self.assertIs(packet["grants_captain_approval"], False)
                self.assertIs(packet["live_synced"], False)
                self.assertIs(packet["approved_for_execution"], False)
                self.assertGreaterEqual(len(packet["memberships"]), 1)
                listed = service.list_packets(root)
                self.assertEqual(listed["count"], 1)
                shown = service.show(root, packet["packet_id"])
                self.assertEqual(shown["packet"]["packet_id"], packet["packet_id"])
            refs = collect_identity_refs(root)
            self.assertEqual(len(refs), 1)
            self.assertEqual(refs[0]["claim_kind"], "external")

    def test_sync_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ.pop("COMPASS_IDENTITY_ENABLED", None)
                os.environ.pop("COMPASS_WORKOS_ENABLED", None)
                with self.assertRaises(PermissionError):
                    service.sync(Path(tmp))

    def test_alias_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._with_schema(root)
            with mock.patch.dict(
                os.environ,
                {"COMPASS_WORKOS_ENABLED": "1"},
                clear=False,
            ):
                os.environ.pop("COMPASS_IDENTITY_ENABLED", None)
                result = service.sync(root)
            self.assertEqual(result["packet"]["mode"], "fixture")

    def test_live_deferred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(
                os.environ,
                {
                    "COMPASS_IDENTITY_ENABLED": "1",
                    "COMPASS_IDENTITY_LIVE": "1",
                    "COMPASS_WORKOS_API_KEY": "sk_test",
                },
                clear=False,
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    service.sync(Path(tmp), live=True)
                self.assertIn("deferred", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
