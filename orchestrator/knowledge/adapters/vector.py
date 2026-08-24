"""Pluggable vector index adapter — file-backed TF-IDF in M6."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

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
    """M6 file-backed TF-IDF vector index adapter."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)

    def index_items(self, items: list[dict]) -> None:
        write_vector_index(self.repo_root)

    def query(self, text: str, *, top_n: int = 10) -> list[dict]:
        ranked = query_vector_scores(self.repo_root, text, top_n=top_n)
        return [{"item_id": item_id, "vector_score": score} for item_id, score in ranked]


def default_vector_adapter(repo_root: Path | None = None) -> VectorIndexAdapter:
    if repo_root is None:
        return NoOpVectorIndexAdapter()
    return FileVectorIndexAdapter(repo_root)
