"""Phase B registry compiler tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.registry.compiler import (
    RegistryCompileError,
    compile_registry,
    write_registry,
)
from orchestrator.registry.infer import infer_capability
from orchestrator.registry.yaml_simple import load_simple_yaml

ROOT = Path(__file__).resolve().parents[2]


class YamlSimpleTests(unittest.TestCase):
    def test_parse_nested_sidecar(self) -> None:
        text = """
id: react-engineering
source:
  type: compass-skill
  path: .cursor/skills/react-engineering/SKILL.md
capabilities_provided:
  - ui-component-development
tags: [react, typescript]
"""
        doc = load_simple_yaml(text)
        self.assertEqual(doc["id"], "react-engineering")
        self.assertEqual(doc["source"]["type"], "compass-skill")
        self.assertEqual(doc["capabilities_provided"], ["ui-component-development"])


class InferTests(unittest.TestCase):
    def test_infer_from_description(self) -> None:
        doc = infer_capability(
            "react-engineering",
            "react-engineering",
            "Implements React and TypeScript UI changes",
        )
        self.assertTrue(doc["provenance"]["inferred"])
        self.assertIn("react-component-development", doc["capabilities_provided"])


class RegistryCompileTests(unittest.TestCase):
    def test_compile_control_repo_registry(self) -> None:
        result = compile_registry(ROOT)
        self.assertEqual(len(result.registry["skills"]), 36)
        self.assertEqual(len(result.registry["reference_profiles"]), 10)
        self.assertEqual(result.warnings, [])

    def test_skill_ids_are_unique(self) -> None:
        result = compile_registry(ROOT)
        ids = [s["id"] for s in result.registry["skills"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_path_traversal_in_source_path_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / ".cursor" / "skills" / "evil-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: evil-skill\ndescription: Evil\n---\n",
                encoding="utf-8",
            )
            (skill_dir / "capability.yaml").write_text(
                """
id: evil-skill
version: "1.0.0"
kind: skill
source:
  type: compass-skill
  path: .cursor/skills/../../../etc/passwd
capabilities_provided:
  - x
""".strip()
                + "\n",
                encoding="utf-8",
            )
            from orchestrator.registry import compiler as comp

            original = comp.SKILL_SLUGS
            original_profiles = comp.AGENT_PROFILES
            comp.SKILL_SLUGS = ("evil-skill",)
            comp.AGENT_PROFILES = ()
            try:
                with self.assertRaises(RegistryCompileError):
                    compile_registry(repo)
            finally:
                comp.SKILL_SLUGS = original
                comp.AGENT_PROFILES = original_profiles

    def test_id_mismatch_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / ".cursor" / "skills" / "bad-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: bad-skill\ndescription: Bad\n---\n",
                encoding="utf-8",
            )
            (skill_dir / "capability.yaml").write_text(
                """
id: wrong-id
version: "1.0.0"
kind: skill
source:
  type: compass-skill
  path: .cursor/skills/bad-skill/SKILL.md
capabilities_provided:
  - x
""".strip()
                + "\n",
                encoding="utf-8",
            )
            # Monkeypatch SKILL_SLUGS by importing module internals
            from orchestrator.registry import compiler as comp

            original = comp.SKILL_SLUGS
            original_profiles = comp.AGENT_PROFILES
            comp.SKILL_SLUGS = ("bad-skill",)
            comp.AGENT_PROFILES = ()
            try:
                with self.assertRaises(RegistryCompileError):
                    compile_registry(repo)
            finally:
                comp.SKILL_SLUGS = original
                comp.AGENT_PROFILES = original_profiles


if __name__ == "__main__":
    unittest.main()
