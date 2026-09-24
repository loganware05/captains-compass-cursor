"""M40 WS5 — content-addressed Skill inode tests."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.registry.compiler import compile_registry
from orchestrator.registry.inodes import (
    build_skill_inode,
    build_skill_inode_index,
    skill_content_hash,
    skill_inode_id_for,
    verify_skill_inodes,
)
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "build-skill-inodes.sh"

SKILL_MD = "---\nname: {slug}\ndescription: fixture skill {slug}\n---\n\n# {slug}\n"
CAPABILITY_YAML = (
    'id: {slug}\nversion: "1.0.0"\nkind: skill\n'
    "source:\n  type: compass-skill\n  path: .cursor/skills/{slug}/SKILL.md\n"
    "lifecycle_stage: AVAILABLE_SKILL\n"
    "capabilities_provided:\n  - fixture-capability\n"
)


def _make_repo(tmp: Path, slugs: tuple[str, ...] = ("alpha-skill", "beta-skill")) -> Path:
    skills_root = tmp / ".cursor" / "skills"
    for slug in slugs:
        skill_dir = skills_root / slug
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(SKILL_MD.format(slug=slug), encoding="utf-8")
        (skill_dir / "capability.yaml").write_text(
            CAPABILITY_YAML.format(slug=slug), encoding="utf-8"
        )
    return tmp


class SkillInodeBuildTests(unittest.TestCase):
    def test_inode_schema_and_addressing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp))
            skill_dir = repo / ".cursor" / "skills" / "alpha-skill"
            inode = build_skill_inode(skill_dir)
            validate_document(inode, "skill-inode.schema.json")
            self.assertEqual(inode["slug"], "alpha-skill")
            self.assertEqual(inode["skill_inode_id"], skill_inode_id_for(inode["content_hash"]))
            self.assertEqual(inode["lifecycle_stage"], "AVAILABLE_SKILL")
            self.assertEqual(inode["sources"], ["SKILL.md", "capability.yaml"])
            self.assertIsNone(inode["reputation"]["carry_over_from"])
            self.assertIs(inode["reputation"]["captain_approved"], False)

    def test_hash_changes_on_content_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp))
            skill_dir = repo / ".cursor" / "skills" / "alpha-skill"
            before = skill_content_hash(skill_dir)
            with (skill_dir / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\nEdit: new procedure step.\n")
            after = skill_content_hash(skill_dir)
            self.assertNotEqual(before, after)
            self.assertNotEqual(skill_inode_id_for(before), skill_inode_id_for(after))

    def test_index_deterministic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp))
            out_a = Path(tmp) / "out-a"
            out_b = Path(tmp) / "out-b"
            result_a = build_skill_inode_index(repo, output_dir=out_a)
            result_b = build_skill_inode_index(repo, output_dir=out_b)
            self.assertEqual(result_a["index"], result_b["index"])
            names_a = sorted(p.name for p in out_a.glob("*.json"))
            for name in names_a:
                self.assertEqual((out_a / name).read_bytes(), (out_b / name).read_bytes())
            self.assertEqual(result_a["index"]["skill_count"], 2)


class CarryOverGateTests(unittest.TestCase):
    def test_content_change_requires_captain_for_carry_over(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp))
            first = build_skill_inode_index(repo)
            alpha_v1 = first["index"]["skills"]["alpha-skill"]

            skill_md = repo / ".cursor" / "skills" / "alpha-skill" / "SKILL.md"
            with skill_md.open("a", encoding="utf-8") as handle:
                handle.write("\nEdit: revised procedure.\n")

            second = build_skill_inode_index(repo)
            alpha_v2 = second["index"]["skills"]["alpha-skill"]
            self.assertNotEqual(alpha_v1["skill_inode_id"], alpha_v2["skill_inode_id"])
            self.assertEqual(
                alpha_v2["reputation"]["carry_over_from"], alpha_v1["skill_inode_id"]
            )
            self.assertIs(alpha_v2["reputation"]["captain_approved"], False)

            third = build_skill_inode_index(repo, captain_approved=True)
            alpha_v3 = third["index"]["skills"]["alpha-skill"]
            self.assertEqual(alpha_v3["skill_inode_id"], alpha_v2["skill_inode_id"])
            self.assertIs(alpha_v3["reputation"]["captain_approved"], True)

            fourth = build_skill_inode_index(repo)
            self.assertIs(
                fourth["index"]["skills"]["alpha-skill"]["reputation"]["captain_approved"],
                True,
            )

    def test_unchanged_content_keeps_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp))
            first = build_skill_inode_index(repo)
            second = build_skill_inode_index(repo)
            self.assertEqual(
                first["index"]["skills"]["beta-skill"]["skill_inode_id"],
                second["index"]["skills"]["beta-skill"]["skill_inode_id"],
            )


class VerifyTests(unittest.TestCase):
    def test_missing_index_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp))
            problems = verify_skill_inodes(repo)
            self.assertEqual(len(problems), 1)
            self.assertIn("missing", problems[0]["reason"])

    def test_stale_and_removed_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp))
            build_skill_inode_index(repo)
            self.assertEqual(verify_skill_inodes(repo), [])

            skill_md = repo / ".cursor" / "skills" / "beta-skill" / "SKILL.md"
            with skill_md.open("a", encoding="utf-8") as handle:
                handle.write("\nEdit without re-index.\n")
            problems = verify_skill_inodes(repo)
            self.assertEqual(
                problems,
                [{"slug": "beta-skill", "reason": "content changed — rerun scripts/build-skill-inodes.sh"}],
            )


class CompilerIntegrationTests(unittest.TestCase):
    def test_registry_embeds_content_addressed_provenance(self) -> None:
        result = compile_registry(ROOT)
        # M41 WS0 registered code-reviewer + northstar-connected-routine in SKILL_SLUGS.
        self.assertEqual(result.warnings, [])
        for skill in result.registry["skills"]:
            provenance = skill.get("provenance") or {}
            self.assertIn("content_hash", provenance, skill.get("id"))
            self.assertIn("skill_inode", provenance, skill.get("id"))
            self.assertEqual(
                provenance["skill_inode"],
                skill_inode_id_for(provenance["content_hash"]),
            )


class CliTests(unittest.TestCase):
    def test_build_then_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = _make_repo(Path(tmp))
            build = subprocess.run(
                [str(CLI), "--repo-root", str(repo)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            summary = json.loads(build.stdout)
            self.assertEqual(summary["skills_indexed"], 2)

            check = subprocess.run(
                [str(CLI), "--repo-root", str(repo), "--check"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(check.returncode, 0, check.stdout)

            skill_md = repo / ".cursor" / "skills" / "alpha-skill" / "SKILL.md"
            with skill_md.open("a", encoding="utf-8") as handle:
                handle.write("\nUnindexed edit.\n")
            recheck = subprocess.run(
                [str(CLI), "--repo-root", str(repo), "--check"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(recheck.returncode, 1)


if __name__ == "__main__":
    unittest.main()
