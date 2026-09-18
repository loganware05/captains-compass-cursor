"""M39 — opt-in Cursor Agentic Security ingest (Phase B)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.review.agentic_security_ingest import (
    AgenticSecurityIngestError,
    ingest_agentic_security,
    map_severity,
    normalize_artifact,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "code-review" / "agentic-security-sample.json"


class SeverityMapTests(unittest.TestCase):
    def test_maps_cursor_severities(self) -> None:
        self.assertEqual(map_severity("Critical"), "critical")
        self.assertEqual(map_severity("Medium"), "medium")
        self.assertEqual(map_severity("warning"), "medium")
        self.assertEqual(map_severity("Informational"), "info")

    def test_rejects_unknown(self) -> None:
        with self.assertRaises(AgenticSecurityIngestError):
            map_severity("ultra")


class NormalizeTests(unittest.TestCase):
    def test_fixture_normalizes(self) -> None:
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        findings = normalize_artifact(payload)
        self.assertEqual(len(findings), 3)
        by_id = {f["id"]: f for f in findings}
        self.assertEqual(by_id["asr-plan-self-serve"]["severity"], "medium")
        self.assertEqual(by_id["asr-refspec"]["severity"], "high")
        self.assertEqual(by_id["asr-info"]["severity"], "info")
        self.assertEqual(by_id["asr-plan-self-serve"]["category"], "agentic-security")
        self.assertEqual(by_id["asr-plan-self-serve"]["source"], "cursor-agentic-security")


class IngestGateTests(unittest.TestCase):
    def test_refuse_closed_without_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(AgenticSecurityIngestError) as ctx:
                ingest_agentic_security(
                    repo_root=root,
                    artifact_path=FIXTURE,
                    repo_slug="loganware05/captain-compass-sandbox",
                )
            self.assertIn("refuse-closed", str(ctx.exception).lower())

    def test_refuse_when_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            alist = root / ".agent" / "review" / "agentic-security-allowlist.yml"
            alist.parent.mkdir(parents=True)
            alist.write_text(
                "schema_version: northstar.agentic_security_allowlist.v1\n"
                "enabled: false\n"
                "repos:\n  - loganware05/captain-compass-sandbox\n",
                encoding="utf-8",
            )
            with self.assertRaises(AgenticSecurityIngestError):
                ingest_agentic_security(
                    repo_root=root,
                    artifact_path=FIXTURE,
                    repo_slug="loganware05/captain-compass-sandbox",
                )

    def test_ingest_writes_evidence_when_allowlisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            alist = root / ".agent" / "review" / "agentic-security-allowlist.yml"
            alist.parent.mkdir(parents=True)
            alist.write_text(
                "schema_version: northstar.agentic_security_allowlist.v1\n"
                "enabled: true\n"
                "repos:\n  - loganware05/captain-compass-sandbox\n",
                encoding="utf-8",
            )
            report = ingest_agentic_security(
                repo_root=root,
                artifact_path=FIXTURE,
                repo_slug="loganware05/captain-compass-sandbox",
                run_id="test-m39",
                outcomes_proposal=True,
            )
            self.assertEqual(report["finding_count"], 3)
            out = root / ".agent" / "evidence" / "review" / "test-m39" / "agentic-security"
            self.assertTrue((out / "findings.json").is_file())
            self.assertTrue((out / "SUMMARY.md").is_file())
            self.assertTrue(report["hermetic_default_unchanged"])
            self.assertEqual(len(report["outcomes_proposal"]), 3)


if __name__ == "__main__":
    unittest.main()
