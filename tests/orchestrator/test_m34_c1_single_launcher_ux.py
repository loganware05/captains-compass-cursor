"""M34 / C1 single launcher UX — hermetic help + docs index checks."""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORTHSTAR = ROOT / "scripts" / "northstar"
INDEX = ROOT / "docs" / "INDEX.md"
PRODUCT_INDEX = ROOT / "templates" / "docs" / "INDEX.md"
ONBOARDING = ROOT / "docs" / "PRODUCT_ONBOARDING.md"
INSTALL = ROOT / "scripts" / "install.sh"

REQUIRED_SURFACES = ("skills", "review", "intent", "outcomes", "repair", "precision")
_MD_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _relative_md_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in _MD_LINK.finditer(text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0]
        if target:
            targets.append(target)
    return targets


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
    def test_control_index_links_resolve(self) -> None:
        text = INDEX.read_text(encoding="utf-8")
        self.assertIn("Control vs product", text)
        for surface in REQUIRED_SURFACES:
            self.assertIn(f"`{surface}`", text)
        docs_root = INDEX.parent
        for target in _relative_md_targets(text):
            path = (docs_root / target).resolve()
            self.assertTrue(path.is_file(), f"broken control INDEX link: {target}")

    def test_product_index_template_links_resolve_against_installed_set(self) -> None:
        text = PRODUCT_INDEX.read_text(encoding="utf-8")
        self.assertIn("product install", text.lower())
        self.assertIn("Run from control", text)
        # Relative links in the product template must only point at docs that
        # install.sh actually copies alongside INDEX.
        allowed = {
            "EVIDENCE_MATRIX.md",
            "integrations/code-reviewer.md",
            "integrations/multi-runtime-agents.md",
            "integrations/technology-intelligence.md",
        }
        for target in _relative_md_targets(text):
            self.assertIn(target, allowed, f"product INDEX unexpected link: {target}")
            self.assertTrue((ROOT / "docs" / target).is_file(), target)

    def test_onboarding_and_install_boundary(self) -> None:
        onboarding = ONBOARDING.read_text(encoding="utf-8")
        self.assertIn("What install does (and does not)", onboarding)
        self.assertIn("Stays in control repo only", onboarding)
        install = INSTALL.read_text(encoding="utf-8")
        self.assertIn("Does NOT copy control-repo scripts", install)
        self.assertIn("templates/docs/INDEX.md", install)


class InstallBoundaryTests(unittest.TestCase):
    def test_hermetic_install_copies_product_index_not_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            product = Path(tmp) / "product"
            product.mkdir()
            subprocess.run(["git", "init"], cwd=str(product), check=True, capture_output=True)
            # Seed minimal files so install conflict checks pass without --force
            proc = subprocess.run(
                [str(INSTALL), str(product)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertFalse((product / "scripts").exists())
            self.assertFalse((product / "scripts" / "northstar").exists())
            index = product / "docs" / "INDEX.md"
            self.assertTrue(index.is_file())
            installed = index.read_text(encoding="utf-8")
            self.assertIn("product install", installed.lower())
            self.assertNotIn("plans/B4_REPAIR_LOOP.md", installed)
            docs_root = product / "docs"
            for target in _relative_md_targets(installed):
                path = (docs_root / target).resolve()
                self.assertTrue(path.is_file(), f"broken product INDEX link after install: {target}")


if __name__ == "__main__":
    unittest.main()
