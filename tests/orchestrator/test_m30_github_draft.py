"""M30 NorthStar Code Reviewer — opt-in GitHub draft reviews."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.review.github_draft import (
    GitHubDraftError,
    create_pending_review,
    load_allowlist,
    post_if_allowed,
    render_draft_body,
    select_findings_for_draft,
)
from orchestrator.review.pipeline import run_code_review
from orchestrator.schemas.validate import validate_document

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = ROOT / "templates" / "agent" / "review" / "github-allowlist.yml"
SANDBOX_REPO = "loganware05/captain-compass-sandbox"


class AllowlistTests(unittest.TestCase):
    def test_template_allowlist_validates(self) -> None:
        pack = load_allowlist(ALLOWLIST)
        validate_document(pack, "github-allowlist.schema.json")
        self.assertIn(SANDBOX_REPO, pack["repos"])

    def test_severity_floor_filters(self) -> None:
        findings = [
            {
                "id": "a",
                "title": "high",
                "severity": "high",
                "status": "verified",
                "confidence": 0.9,
                "skill": "security-review",
            },
            {
                "id": "b",
                "title": "low",
                "severity": "low",
                "status": "verified",
                "confidence": 0.9,
                "skill": "testing-validation",
            },
            {
                "id": "c",
                "title": "discarded",
                "severity": "critical",
                "status": "discarded",
                "confidence": 0.9,
                "skill": "security-review",
            },
        ]
        selected = select_findings_for_draft(findings, severity_floor="medium")
        self.assertEqual([f["id"] for f in selected], ["a"])


class DraftPostingTests(unittest.TestCase):
    def test_refuse_when_not_allowlisted(self) -> None:
        result = post_if_allowed(
            report={"run_id": "r1", "summary": {}, "provenance": {}},
            findings=[],
            repo_slug="acme/not-listed",
            pull_number=7,
            allowlist_path=ALLOWLIST,
        )
        self.assertFalse(result["posted"])
        self.assertEqual(result["reason"], "repo_not_allowlisted")

    def test_pending_review_omits_event(self) -> None:
        captured: dict = {}

        def client(method, url, headers, body):
            captured["method"] = method
            captured["url"] = url
            captured["body"] = json.loads(body.decode("utf-8"))
            return 200, {
                "id": 99,
                "state": "PENDING",
                "html_url": "https://example.test/review/99",
            }

        result = create_pending_review(
            repo_slug=SANDBOX_REPO,
            pull_number=12,
            body="draft body",
            token="ghp_test_token_not_real",
            http_client=client,
        )
        self.assertTrue(result["posted"])
        self.assertEqual(captured["method"], "POST")
        self.assertNotIn("event", captured["body"])
        self.assertEqual(captured["body"]["body"], "draft body")
        self.assertEqual(result["state"], "PENDING")

    def test_post_if_allowed_with_mock(self) -> None:
        def client(method, url, headers, body):
            payload = json.loads(body.decode("utf-8"))
            self.assertNotIn("event", payload)
            return 201, {"id": 5, "state": "PENDING", "html_url": "https://example.test/5"}

        findings = [
            {
                "id": "sec-1",
                "title": "Secret risk",
                "severity": "high",
                "status": "verified",
                "confidence": 0.95,
                "skill": "security-review",
                "detail": "token in diff",
            }
        ]
        result = post_if_allowed(
            report={
                "run_id": "m30-mock",
                "summary": {"domains": ["python"]},
                "provenance": {"candidates_source": "specialists"},
            },
            findings=findings,
            repo_slug=SANDBOX_REPO,
            pull_number=3,
            allowlist_path=ALLOWLIST,
            token="ghp_test",
            http_client=client,
        )
        self.assertTrue(result["posted"])
        self.assertEqual(result["reason"], "posted_pending_draft")
        self.assertNotIn("ghp_test", json.dumps(result))

    def test_missing_token_refuses(self) -> None:
        with self.assertRaises(GitHubDraftError):
            create_pending_review(
                repo_slug=SANDBOX_REPO,
                pull_number=1,
                body="x",
                token="",
            )


class PipelineDraftTests(unittest.TestCase):
    def test_default_path_does_not_post(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "a.py").write_text("x=1\n", encoding="utf-8")
            result = run_code_review(
                repo_root=repo,
                run_id="m30-default",
                changed_paths=["src/a.py"],
                diff_text="diff --git a/src/a.py b/src/a.py\n+x=1\n",
                candidates_mode="heuristics",
            )
            self.assertFalse(result["report"]["provenance"]["github_review_posted"])
            self.assertIsNone(result.get("github_draft"))

    def test_pipeline_posts_when_enabled(self) -> None:
        calls: list[dict] = []

        def client(method, url, headers, body):
            calls.append(json.loads(body.decode("utf-8")))
            return 200, {"id": 42, "state": "PENDING", "html_url": "https://example.test/42"}

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            allow = repo / ".agent" / "review" / "github-allowlist.yml"
            allow.parent.mkdir(parents=True)
            allow.write_text(ALLOWLIST.read_text(encoding="utf-8"), encoding="utf-8")
            (repo / "src").mkdir()
            (repo / "src" / "auth.py").write_text("TOKEN='secretvalue'\n", encoding="utf-8")
            result = run_code_review(
                repo_root=repo,
                run_id="m30-post",
                changed_paths=["src/auth.py"],
                diff_text=(
                    "diff --git a/src/auth.py b/src/auth.py\n"
                    "+API_KEY='sk_live_example_not_real_123456'\n"
                ),
                candidates_mode="specialists",
                post_github_draft=True,
                github_repo=SANDBOX_REPO,
                pull_number=9,
                github_token="ghp_pipeline_test",
                github_http_client=client,
            )
            self.assertTrue(result["report"]["provenance"]["github_review_posted"])
            self.assertTrue(result["github_draft"]["posted"])
            self.assertEqual(len(calls), 1)
            self.assertNotIn("event", calls[0])
            evidence = (
                repo / ".agent" / "evidence" / "code-review" / "m30-post" / "github-draft.json"
            )
            self.assertTrue(evidence.is_file())
            validate_document(result["report"], "code-review-report.schema.json")


class RenderTests(unittest.TestCase):
    def test_render_includes_findings(self) -> None:
        body = render_draft_body(
            {"run_id": "r", "summary": {"domains": ["python"]}, "provenance": {}},
            [
                {
                    "id": "1",
                    "title": "Issue",
                    "severity": "high",
                    "confidence": 0.8,
                    "skill": "security-review",
                }
            ],
        )
        self.assertIn("Issue", body)
        self.assertIn("not an approval", body.lower())


if __name__ == "__main__":
    unittest.main()
