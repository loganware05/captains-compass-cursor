"""M12 live OpenAI-compatible embeddings + package-registry TI + soft-hook skip-env."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from orchestrator.knowledge.adapters.embeddings import (
    EmbeddingProviderError,
    OpenAICompatibleEmbeddingProvider,
    select_embedding_provider,
)
from orchestrator.knowledge.embedding_index import write_embedding_index
from orchestrator.knowledge.query import query_knowledge
from orchestrator.knowledge.store import write_knowledge_item
from orchestrator.knowledge.vector_index import write_vector_index
from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider
from orchestrator.providers.technology_intelligence.package_registry_live_provider import (
    PackageRegistryLiveTechnologyIntelligenceProvider,
)

ROOT = Path(__file__).resolve().parents[2]


def _sample_item(item_id: str, title: str, summary: str) -> dict:
    return {
        "item_id": item_id,
        "kind": "knowledge",
        "title": title,
        "summary": summary,
        "provenance": {"source": "test"},
        "source_artifact": {"type": "fixture", "id": item_id, "path": f"tests/{item_id}.md"},
        "created_at": "2026-08-24T00:00:00Z",
        "updated_at": "2026-08-24T00:00:00Z",
    }


class OpenAICompatibleEmbeddingTests(unittest.TestCase):
    def test_fail_closed_without_api_key(self) -> None:
        provider = OpenAICompatibleEmbeddingProvider(api_key="")
        with self.assertRaises(EmbeddingProviderError):
            provider.embed(["hello"])

    def test_mocked_http_embed_and_query(self) -> None:
        def fake_post(url: str, headers: dict, body: bytes, timeout: float) -> bytes:
            self.assertIn("/embeddings", url)
            self.assertTrue(headers.get("Authorization", "").startswith("Bearer "))
            self.assertNotIn("sk-secret", str(body))
            payload = json.loads(body.decode("utf-8"))
            n = len(payload["input"])
            data = [
                {"index": i, "embedding": [float(i + 1), 0.1, 0.2, 0.3]}
                for i in range(n)
            ]
            return json.dumps({"data": data}).encode("utf-8")

        provider = OpenAICompatibleEmbeddingProvider(
            api_key="sk-secret",
            base_url="https://example.test/v1",
            model="text-embedding-test",
            http_post=fake_post,
        )
        vectors = provider.embed(["alpha", "beta"])
        self.assertEqual(len(vectors), 2)
        self.assertEqual(provider.dimensions, 4)

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_knowledge_item(
                repo,
                _sample_item("know-m12-a", "Matcher routing", "routing weights autonomy"),
            )
            write_knowledge_item(
                repo,
                _sample_item("know-m12-b", "React forms", "accessible form validation"),
            )
            write_vector_index(repo)
            write_embedding_index(repo, provider=provider)

            old = {
                "COMPASS_EMBEDDING_PROVIDER": os.environ.get("COMPASS_EMBEDDING_PROVIDER"),
                "COMPASS_EMBEDDING_API_KEY": os.environ.get("COMPASS_EMBEDDING_API_KEY"),
            }
            os.environ["COMPASS_EMBEDDING_PROVIDER"] = "openai-compatible"
            os.environ["COMPASS_EMBEDDING_API_KEY"] = "sk-secret"
            try:
                # Inject mock via constructing provider used by write; for query,
                # monkeypatch select by rebuilding with env + temporary module path is hard.
                # Query uses select_embedding_provider() which would hit real HTTP —
                # so test provider selection and fail-closed path instead for live query.
                selected = select_embedding_provider()
                self.assertIsInstance(selected, OpenAICompatibleEmbeddingProvider)

                # Direct query with injected provider scores
                from orchestrator.knowledge.embedding_index import query_embedding_scores

                ranked = query_embedding_scores(
                    repo, "routing", top_n=5, provider=provider
                )
                self.assertTrue(ranked)
            finally:
                for key, val in old.items():
                    if val is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = val

    def test_live_embed_failure_falls_back_to_tfidf(self) -> None:
        def boom(url: str, headers: dict, body: bytes, timeout: float) -> bytes:
            raise TimeoutError("simulated")

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_knowledge_item(
                repo,
                _sample_item("know-m12-c", "Matcher routing weights", "bounded autonomy matcher"),
            )
            write_vector_index(repo)
            # Dense index present from a prior fixture-like write using mock success once
            ok_provider = OpenAICompatibleEmbeddingProvider(
                api_key="sk-x",
                base_url="https://example.test/v1",
                http_post=lambda *a, **k: json.dumps(
                    {"data": [{"index": 0, "embedding": [1.0, 0.0, 0.0, 0.0]}]}
                ).encode("utf-8"),
            )
            write_embedding_index(repo, provider=ok_provider)

            failing = OpenAICompatibleEmbeddingProvider(
                api_key="sk-x",
                base_url="https://example.test/v1",
                http_post=boom,
            )
            os.environ["COMPASS_EMBEDDING_PROVIDER"] = "openai-compatible"
            os.environ["COMPASS_EMBEDDING_API_KEY"] = "sk-x"
            # Patch select by temporarily replacing module function
            import orchestrator.knowledge.query as query_mod
            import orchestrator.knowledge.adapters.embeddings as emb_mod

            original = emb_mod.select_embedding_provider
            emb_mod.select_embedding_provider = lambda: failing  # type: ignore
            query_mod.select_embedding_provider = emb_mod.select_embedding_provider
            try:
                results = query_knowledge(repo, "matcher routing", mode="vector", top_n=5)
                self.assertTrue(results)
                self.assertEqual(results[0].get("vector_backend"), "tfidf")
            finally:
                emb_mod.select_embedding_provider = original
                query_mod.select_embedding_provider = original
                os.environ.pop("COMPASS_EMBEDDING_PROVIDER", None)
                os.environ.pop("COMPASS_EMBEDDING_API_KEY", None)


class PackageRegistryLiveTITests(unittest.TestCase):
    def test_mocked_npm_and_pypi(self) -> None:
        def fake_get(url: str, timeout: float) -> bytes:
            if "registry.npmjs.org" in url:
                return json.dumps(
                    {
                        "objects": [
                            {
                                "package": {
                                    "name": "zod",
                                    "version": "3.23.8",
                                    "description": "TypeScript schema validation",
                                }
                            }
                        ]
                    }
                ).encode("utf-8")
            if "pypi.org/pypi/" in url:
                return json.dumps(
                    {
                        "info": {
                            "name": "pydantic",
                            "version": "2.9.0",
                            "summary": "Data validation using Python type hints",
                        }
                    }
                ).encode("utf-8")
            raise AssertionError(f"unexpected url {url}")

        provider = PackageRegistryLiveTechnologyIntelligenceProvider(
            ecosystems=("npm", "pypi"),
            http_get=fake_get,
        )
        found = provider.discover_candidates("schema validation typescript pydantic", {})
        self.assertTrue(found)
        ecosystems = {c.source_path.split(":")[0] for c in found}
        self.assertTrue("npm" in ecosystems or "pypi" in ecosystems)
        for cand in found:
            self.assertFalse(cand.to_dict()["approved_for_execution"])

    def test_select_ti_provider_live(self) -> None:
        old = os.environ.get("COMPASS_TI_PROVIDER")
        os.environ["COMPASS_TI_PROVIDER"] = "package-registry"
        try:
            provider = select_ti_provider()
            self.assertIsInstance(provider, PackageRegistryLiveTechnologyIntelligenceProvider)
        finally:
            if old is None:
                os.environ.pop("COMPASS_TI_PROVIDER", None)
            else:
                os.environ["COMPASS_TI_PROVIDER"] = old


class SoftHookSkipEnvFileTests(unittest.TestCase):
    def test_compass_skip_env_file_allows_format_hook(self) -> None:
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".agent").mkdir(parents=True)
            (repo / ".agent" / "compass-skip.env").write_text(
                "COMPASS_SKIP_FORMAT=1\n", encoding="utf-8"
            )
            # Minimal package.json so format hook finds something to skip before running
            (repo / "package.json").write_text('{"name":"t"}\n', encoding="utf-8")
            hook = ROOT / ".cursor" / "hooks" / "pre-commit-formatting.sh"
            payload = json.dumps({"command": "git commit -m x", "cwd": str(repo)})
            result = subprocess.run(
                [str(hook)],
                input=payload,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertIn('"permission":"allow"', result.stdout.replace(" ", ""))
            self.assertIn("allow", result.stdout)


if __name__ == "__main__":
    unittest.main()
