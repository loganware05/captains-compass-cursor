"""M14 batch GitHub Star categorization ML pipeline tests."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider
from orchestrator.providers.technology_intelligence.github_stars_provider import (
    load_recorded_starred_fixtures,
)
from orchestrator.providers.technology_intelligence.stars_categorization import (
    categorize_records,
    load_manual_labels,
    predict_category,
    read_categorized_records,
    run_batch_categorization,
    train_naive_bayes,
)

ROOT = Path(__file__).resolve().parents[2]
LABELS = ROOT / "tests" / "fixtures" / "ti" / "github-stars-labels" / "manual-labels.json"
STARRED = ROOT / "tests" / "fixtures" / "ti" / "github-stars-recorded"


class StarsCategorizationTests(unittest.TestCase):
    def test_manual_labels_load(self) -> None:
        labels = load_manual_labels(LABELS)
        self.assertEqual(len(labels), 4)
        categories = {row["category"] for row in labels}
        self.assertIn("frontend-ui", categories)
        self.assertIn("backend-library", categories)

    def test_train_and_predict_fixture_repos(self) -> None:
        labels = load_manual_labels(LABELS)
        model = train_naive_bayes(labels)
        repos = load_recorded_starred_fixtures(STARRED)
        categorized = categorize_records(repos, model=model, labels=labels)
        by_name = {str(r["full_name"]): r for r in categorized}
        self.assertEqual(by_name["example-org/accessible-react-forms"]["star_category"], "frontend-ui")
        self.assertEqual(by_name["example-org/pdf-kit-node"]["star_category"], "backend-library")
        self.assertEqual(by_name["example-org/unrelated-quantum"]["star_category"], "ml-data")

    def test_batch_write_and_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            repos = load_recorded_starred_fixtures(STARRED)
            report = run_batch_categorization(
                repo,
                repos,
                labels_path=LABELS,
                source="fixtures:test",
            )
            self.assertEqual(report["record_count"], 3)
            self.assertTrue(read_categorized_records(repo))

            os.environ["COMPASS_TI_PROVIDER"] = "github-stars-categorized"
            try:
                provider = select_ti_provider(repo)
                found = provider.discover_candidates("accessible react forms", {})
                self.assertTrue(found)
                self.assertIn("[frontend-ui]", found[0].notes)
            finally:
                os.environ.pop("COMPASS_TI_PROVIDER", None)

    def test_predict_empty_repo_is_other(self) -> None:
        model = train_naive_bayes(load_manual_labels(LABELS))
        category, _ = predict_category(model, {})
        self.assertEqual(category, "other")


if __name__ == "__main__":
    unittest.main()
