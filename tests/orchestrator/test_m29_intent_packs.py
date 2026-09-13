"""M29 NorthStar Code Reviewer — intent packs + installer templates."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from orchestrator.review.detect import load_intent
from orchestrator.review.intent import (
    IntentError,
    intent_from_json,
    intent_from_plan_markdown,
    load_intent_pack,
)
from orchestrator.review.pipeline import run_code_review
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "code-review"


class IntentPackSchemaTests(unittest.TestCase):
    def test_fixture_pack_validates(self) -> None:
        pack = json.loads(
            (FIXTURES / "intent-pack.json").read_text(encoding="utf-8")
        )
        validate_document(pack, "intent-pack.schema.json")
        self.assertIs(pack["captain_approval"], False)

    def test_captain_approval_forced_false(self) -> None:
        pack = intent_from_json(FIXTURES / "intent-pack.json")
        self.assertIs(pack["captain_approval"], False)
        # Even if a caller tries to flip it, loader forces false.
        dirty = json.loads(
            (FIXTURES / "intent-pack.json").read_text(encoding="utf-8")
        )
        dirty["captain_approval"] = True
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as handle:
            json.dump(dirty, handle)
            path = Path(handle.name)
        try:
            forced = intent_from_json(path)
            self.assertIs(forced["captain_approval"], False)
        finally:
            path.unlink(missing_ok=True)


class IntentParseTests(unittest.TestCase):
    def test_plan_markdown_sections(self) -> None:
        pack = intent_from_plan_markdown(FIXTURES / "plan.md")
        self.assertEqual(pack["source"], "plan")
        self.assertIn("Evidence-only code review reports", pack["acceptance_criteria"])
        self.assertIn("Auto-posting GitHub reviews", pack["non_goals"])
        self.assertIs(pack["captain_approval"], False)

    def test_intent_json_override(self) -> None:
        pack = load_intent_pack(intent_json=FIXTURES / "intent-pack.json")
        self.assertEqual(pack["source"], "fixture")
        self.assertIn(
            "Load intent from normalized JSON without a temp plan",
            pack["acceptance_criteria"],
        )

    def test_detect_load_intent_json(self) -> None:
        intent = load_intent(None, intent_json=FIXTURES / "intent-pack.json")
        self.assertIs(intent["captain_approval"], False)
        self.assertEqual(intent["source"], "fixture")
        self.assertTrue(intent["acceptance_criteria"])

    def test_missing_json_raises(self) -> None:
        with self.assertRaises(IntentError):
            intent_from_json(FIXTURES / "does-not-exist.json")


class IntentPipelineTests(unittest.TestCase):
    def test_review_with_intent_json_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            session = repo / "src" / "auth" / "session.py"
            session.parent.mkdir(parents=True)
            session.write_text(
                "def create_session(user_id: str) -> dict:\n    return {}\n",
                encoding="utf-8",
            )
            result = run_code_review(
                repo_root=repo,
                run_id="fixture-m29-intent-json",
                diff_file=FIXTURES / "sample.diff",
                changed_paths=["src/auth/session.py"],
                intent_json=FIXTURES / "intent-pack.json",
                plan_id="m29-intent-packs",
            )
            report = result["report"]
            validate_document(report, "code-review-report.schema.json")
            self.assertFalse(report["provenance"]["github_review_posted"])
            self.assertTrue(report["provenance"]["hermetic"])
            intent = result["detection"]["intent"]
            self.assertEqual(intent["source"], "fixture")
            self.assertIs(intent["captain_approval"], False)
            self.assertIn(
                "Load intent from normalized JSON without a temp plan",
                intent["acceptance_criteria"],
            )

    def test_auto_discover_intent_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "a.py").write_text("x=1\n", encoding="utf-8")
            intent_dir = repo / ".agent" / "intent"
            intent_dir.mkdir(parents=True)
            target = intent_dir / "current.json"
            target.write_text(
                (FIXTURES / "intent-pack.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            result = run_code_review(
                repo_root=repo,
                run_id="fixture-m29-autodiscover",
                changed_paths=["a.py"],
                diff_text="diff --git a/a.py b/a.py\n+x=1\n",
                candidates_mode="heuristics",
            )
            self.assertEqual(result["detection"]["intent"]["source"], "fixture")


class CliAndInstallerTests(unittest.TestCase):
    def test_export_intent_from_linear_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "intent.json"
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "export-intent-from-linear.sh"),
                    "--out",
                    str(out),
                    "--fixture",
                    str(FIXTURES / "linear-issue.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            pack = json.loads(out.read_text(encoding="utf-8"))
            validate_document(pack, "intent-pack.schema.json")
            self.assertIs(pack["captain_approval"], False)
            self.assertEqual(pack["source"], "linear")
            self.assertEqual(pack["linear_issue_id"], "OVA-FIXTURE-M29")

    def test_run_code_review_sh_intent_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "auth.py").write_text("TOKEN='x'\n", encoding="utf-8")
            proc = subprocess.run(
                [
                    str(ROOT / "scripts" / "run-code-review.sh"),
                    "--repo-root",
                    str(repo),
                    "--intent-json",
                    str(FIXTURES / "intent-pack.json"),
                    "--diff-file",
                    str(FIXTURES / "sample.diff"),
                    "--changed",
                    "src/auth/session.py",
                    "--run-id",
                    "cli-m29-intent",
                    "--plan-id",
                    "m29-intent-packs",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["intent_source"], "fixture")
            self.assertFalse(payload["github_review_posted"])

    def test_installer_adds_intent_pack_skip_if_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "product"
            target.mkdir()
            subprocess.run(
                ["git", "init"],
                cwd=target,
                check=True,
                capture_output=True,
                text=True,
            )
            # Seed an existing APPROVED plan that must not be overwritten.
            (target / "IMPLEMENTATION_PLAN.md").write_text(
                "# Existing\n\n| Status | APPROVED |\n",
                encoding="utf-8",
            )
            for name in (
                "AGENTS.md",
                "PROJECT_CONTEXT.md",
                "DECISIONS.md",
                "PROGRESS.md",
                "TESTING.md",
                "CHANGELOG.md",
            ):
                (target / name).write_text(f"# {name}\n", encoding="utf-8")

            proc = subprocess.run(
                [str(ROOT / "scripts" / "install.sh"), "--force", str(target)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("keep: IMPLEMENTATION_PLAN.md", proc.stdout)
            self.assertTrue((target / "INTENT_PACK.md").is_file())
            self.assertTrue((target / ".agent" / "intent").is_dir())
            plan = (target / "IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
            self.assertIn("APPROVED", plan)
            self.assertNotIn("Acceptance Criteria", plan)


if __name__ == "__main__":
    unittest.main()
