"""Pluggable vector index adapter — file-backed TF-IDF (M6) with dense optional (M11)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from orchestrator.knowledge.adapters.embeddings import select_embedding_provider
from orchestrator.knowledge.embedding_index import (
    embedding_index_exists,
    query_embedding_scores,
    write_embedding_index,
)
from orchestrator.knowledge.vector_index import query_vector_scores, write_vector_index


class VectorIndexAdapter(Protocol):
    """Vector store interface for semantic knowledge search."""

    def index_items(self, items: list[dict]) -> None: ...

    def query(self, text: str, *, top_n: int = 10) -> list[dict]: ...


class NoOpVectorIndexAdapter:
    """Fallback adapter when vector index is unavailable."""

    def index_items(self, items: list[dict]) -> None:
        return None

    def query(self, text: str, *, top_n: int = 10) -> list[dict]:
        return []


class FileVectorIndexAdapter:
    """M6 file-backed TF-IDF vector index adapter (always available fallback)."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)

    def index_items(self, items: list[dict]) -> None:
        del items
        write_vector_index(self.repo_root)

    def query(self, text: str, *, top_n: int = 10) -> list[dict]:
        ranked = query_vector_scores(self.repo_root, text, top_n=top_n)
        return [{"item_id": item_id, "vector_score": score} for item_id, score in ranked]


class DenseThenTfidfVectorIndexAdapter:
    """M11: rebuild TF-IDF always; rebuild dense when fixture embedding provider is set.

    Query prefers dense scores when an embedding index exists; TF-IDF remains fallback.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self._tfidf = FileVectorIndexAdapter(repo_root)

    def index_items(self, items: list[dict]) -> None:
        self._tfidf.index_items(items)
        provider = select_embedding_provider()
        if provider is not None:
            write_embedding_index(self.repo_root, provider=provider)

    def query(self, text: str, *, top_n: int = 10) -> list[dict]:
        from orchestrator.knowledge.adapters.embeddings import EmbeddingProviderError

        provider = select_embedding_provider()
        if provider is not None and embedding_index_exists(self.repo_root):
            try:
                ranked = query_embedding_scores(
                    self.repo_root, text, top_n=top_n, provider=provider
                )
            except EmbeddingProviderError:
                ranked = []
            if ranked:
                backend = getattr(provider, "name", "dense") or "dense"
                if backend == "fixture":
                    backend = "fixture-embedding"
                return [
                    {
                        "item_id": item_id,
                        "vector_score": score,
                        "vector_backend": backend,
                    }
                    for item_id, score in ranked
                ]
        return self._tfidf.query(text, top_n=top_n)


def default_vector_adapter(repo_root: Path | None = None) -> VectorIndexAdapter:
    if repo_root is None:
        return NoOpVectorIndexAdapter()
    if select_embedding_provider() is not None:
        return DenseThenTfidfVectorIndexAdapter(repo_root)
    return FileVectorIndexAdapter(repo_root)
