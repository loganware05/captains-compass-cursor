"""Pluggable vector index adapter — NoOp stub in M5."""

from __future__ import annotations

from typing import Protocol


class VectorIndexAdapter(Protocol):
    """Future M6+ vector store interface."""

    def index_items(self, items: list[dict]) -> None: ...

    def query(self, text: str, *, top_n: int = 10) -> list[dict]: ...


class NoOpVectorIndexAdapter:
    """Default M5 adapter — keyword index only."""

    def index_items(self, items: list[dict]) -> None:
        return None

    def query(self, text: str, *, top_n: int = 10) -> list[dict]:
        return []


def default_vector_adapter() -> VectorIndexAdapter:
    return NoOpVectorIndexAdapter()
