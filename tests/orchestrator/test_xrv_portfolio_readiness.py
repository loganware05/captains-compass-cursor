"""XRV W3: product profile + portfolio readiness."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.xrv import eer, portfolio, readiness

REPO = Path(__file__).resolve().parents[2]


class ProductProfileTests(unittest.TestCase):
    def test_product_repo_uses_control_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# A\n", encoding="utf-8")
            (root / "TESTING.md").write_text("# T\n", encoding="utf-8")
            (root / "README.md").write_text("# R\n", encoding="utf-8")
            (root / "PROJECT_CONTEXT.md").write_text("# P\n", encoding="utf-8")
            (root / "PROGRESS.md").write_text("# G\n", encoding="utf-8")
            (root / "IMPLEMENTATION_PLAN.md").write_text("# I\n", encoding="utf-8")
            (root / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
            (root / "package.json").write_text("{}\n", encoding="utf-8")
            (root / ".cursor" / "hooks").mkdir(parents=True)
            (root / ".cursor" / "hooks.json").write_text("{}\n", encoding="utf-8")
            (root / ".cursor" / "hooks" / "secret-protection.sh").write_text(
                "#!/bin/sh\n", encoding="utf-8"
            )
            (root / ".cursor" / "rules").mkdir(parents=True)
            (
                root / ".cursor" / "rules" / "01-plan-approval-gate.mdc"
            ).write_text("x\n", encoding="utf-8")
            (root / ".agent" / "evidence").mkdir(parents=True)
            (root / ".agent" / "COMPASS_VERSION").write_text("1.84.0\n", encoding="utf-8")
            with mock.patch.dict(
                os.environ, {"COMPASS_XRV_READINESS_ENABLED": "1"}, clear=False
            ):
                result = readiness.assess_readiness(
                    root,
                    require_gate=True,
                    write_evidence=False,
                    profile="product",
                    control_root=REPO,
                )
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["scorecard"]["profile"], "product")
            self.assertGreaterEqual(
                result["scorecard"]["repository_readiness"]["scored_count"], 1
            )


class PortfolioTests(unittest.TestCase):
    def test_portfolio_two_repos(self) -> None:
        with mock.patch.dict(
            os.environ, {"COMPASS_XRV_READINESS_ENABLED": "1"}, clear=False
        ):
            result = portfolio.assess_portfolio(
                [
                    ("northstar", REPO, "control"),
                ],
                require_gate=True,
                write_evidence=False,
                control_root=REPO,
            )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["portfolio"]["repos"]), 1)
        self.assertIs(result["portfolio"]["scores_invented"], False)


class PilotEerTests(unittest.TestCase):
    def test_pilot_eers_validate(self) -> None:
        for name in (
            "eer-traphouse-slice17-reconcile.json",
            "eer-bitcoin-pilot-b-continuity.json",
        ):
            path = REPO / ".agent" / "evidence" / "xrv" / name
            with mock.patch.dict(
                os.environ, {"COMPASS_XRV_EER_ENABLED": "1"}, clear=False
            ):
                result = eer.validate_eer_path(REPO, path, require_gate=True)
            self.assertEqual(result["status"], "ok", msg=name)
            self.assertEqual(result["lifecycle_state"], "merged")


if __name__ == "__main__":
    unittest.main()
