"""M16 live Hugging Face Hub TI tests."""

from __future__ import annotations

import json
import os
import unittest

from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider
from orchestrator.providers.technology_intelligence.huggingface_live_provider import (
    HuggingFaceHubLiveTechnologyIntelligenceProvider,
)


class HuggingFaceHubLiveTITests(unittest.TestCase):
    def test_mocked_hub_search(self) -> None:
        def fake_get(url: str, timeout: float) -> bytes:
            self.assertIn("huggingface.co/api/models", url)
            return json.dumps(
                [
                    {
                        "id": "sentence-transformers/all-MiniLM-L6-v2",
                        "pipeline_tag": "sentence-similarity",
                        "tags": ["transformers", "pytorch", "sentence-embeddings"],
                    },
                    {
                        "id": "openai/whisper-tiny",
                        "pipeline_tag": "automatic-speech-recognition",
                        "tags": ["audio", "transformers"],
                    },
                ]
            ).encode("utf-8")

        provider = HuggingFaceHubLiveTechnologyIntelligenceProvider(http_get=fake_get)
        found = provider.discover_candidates("sentence embeddings semantic similarity", {})
        self.assertTrue(found)
        signals = {c.discovery_signal for c in found}
        self.assertTrue(any("huggingface-hub-live:" in s for s in signals))
        for cand in found:
            self.assertFalse(cand.to_dict()["approved_for_execution"])

    def test_hub_failure_returns_empty(self) -> None:
        def boom(url: str, timeout: float) -> bytes:
            raise TimeoutError("simulated")

        provider = HuggingFaceHubLiveTechnologyIntelligenceProvider(http_get=boom)
        self.assertEqual(provider.discover_candidates("embeddings", {}), [])

    def test_select_ti_provider_hub_live(self) -> None:
        old = os.environ.get("COMPASS_TI_PROVIDER")
        os.environ["COMPASS_TI_PROVIDER"] = "huggingface-hub"
        try:
            provider = select_ti_provider()
            self.assertIsInstance(provider, HuggingFaceHubLiveTechnologyIntelligenceProvider)
        finally:
            if old is None:
                os.environ.pop("COMPASS_TI_PROVIDER", None)
            else:
                os.environ["COMPASS_TI_PROVIDER"] = old


if __name__ == "__main__":
    unittest.main()
