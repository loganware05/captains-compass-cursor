"""Pluggable embedding providers — fixture-only dense vectors in M11 (no live HTTP)."""

from __future__ import annotations

import hashlib
import math
import os
from typing import Protocol


class EmbeddingProvider(Protocol):
    """Embed text into dense vectors for optional semantic knowledge search."""

    name: str
    dimensions: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        return vector
    return [round(v / norm, 6) for v in vector]


def _tokenize(text: str) -> list[str]:
    cleaned = text.lower().replace("/", " ").replace("-", " ").replace("_", " ")
    return [tok for tok in cleaned.split() if len(tok) >= 2]


class FixtureEmbeddingProvider:
    """Deterministic bag-of-tokens hash projection (offline; no network).

    Used when ``COMPASS_EMBEDDING_PROVIDER=fixture``. Produces fixed-dimension
    dense vectors suitable for CI golden tests. Not a live model API.
    """

    name = "fixture"
    dimensions = 32

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = _tokenize(text)
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(self.dimensions):
                # Map byte to signed contribution in [-1, 1]
                byte = digest[i % len(digest)]
                vector[i] += (byte / 127.5) - 1.0
        return _l2_normalize(vector)


def select_embedding_provider() -> EmbeddingProvider | None:
    """Return embedding provider from env, or None for TF-IDF-only path.

    Values:
    - ``tfidf`` / empty — None (use existing TF-IDF vector index only)
    - ``fixture`` — FixtureEmbeddingProvider
    """
    name = os.environ.get("COMPASS_EMBEDDING_PROVIDER", "tfidf").strip().lower() or "tfidf"
    if name in {"tfidf", "none", "off"}:
        return None
    if name in {"fixture", "fixtures", "hash"}:
        return FixtureEmbeddingProvider()
    # Unknown → fail closed to TF-IDF (no surprise network backends)
    return None
