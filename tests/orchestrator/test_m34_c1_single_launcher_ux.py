"""M34 / C1 single launcher UX — hermetic help + docs index checks."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORTHSTAR = ROOT / "scripts" / "northstar"
INDEX = ROOT / "docs" / "INDEX.md"
ONBOARDING = ROOT / "docs" / "PRODUCT_ONBOARDING.md"
INSTALL = ROOT / "scripts" / "install.sh"

REQUIRED_SURFACES = ("skills", "review", "intent", "outcomes", "repair", "precision")


class NorthstarHelpTests(unittest.TestCase):
    def test_help_lists_all_surfaces_and_docs_index(self) -> None:
        proc = subprocess.run(
            [str(NORTHSTAR), "help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = proc.stdout
        self.assertIn("Surfaces (one-line purpose)", out)
        self.assertIn("docs/INDEX.md", out)
        self.assertIn("Product installs get docs/Skills via install.sh", out)
        for surface in REQUIRED_SURFACES:
            self.assertRegex(out, rf"(?m)^  {surface}\s+")

    def test_help_alias_flags(self) -> None:
        for flag in ("-h", "--help"):
            proc = subprocess.run(
                [str(NORTHSTAR), flag],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("precision", proc.stdout)


class DocsIndexTests(unittest.TestCase):
    def test_index_links_key_paths(self) -> None:
        text = INDEX.read_text(encoding="utf-8")
        self.assertIn("Control vs product", text)
        self.assertIn("integrations/code-reviewer.md", text)
        self.assertIn("integrations/linear-skills-learning-loop.md", text)
        self.assertIn("PRODUCT_ONBOARDING.md", text)
        for surface in REQUIRED_SURFACES:
            self.assertIn(f"`{surface}`", text)

    def test_onboarding_and_install_boundary(self) -> None:
        onboarding = ONBOARDING.read_text(encoding="utf-8")
        self.assertIn("What install does (and does not)", onboarding)
        self.assertIn("Stays in control repo only", onboarding)
        install = INSTALL.read_text(encoding="utf-8")
        self.assertIn("Does NOT copy control-repo scripts", install)
        self.assertIn("docs/INDEX.md", install)


if __name__ == "__main__":
    unittest.main()
