"""Pluggable embedding providers — fixture + OpenAI-compatible HTTP (M11/M12)."""

from __future__ import annotations

import hashlib
import json
import math
import os
import urllib.error
import urllib.request
from typing import Callable, Protocol


class EmbeddingProvider(Protocol):
    """Embed text into dense vectors for optional semantic knowledge search."""

    name: str
    dimensions: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class EmbeddingProviderError(RuntimeError):
    """Raised when a live embedding provider fails closed."""


def _l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        return vector
    return [round(v / norm, 6) for v in vector]


def _tokenize(text: str) -> list[str]:
    cleaned = text.lower().replace("/", " ").replace("-", " ").replace("_", " ")
    return [tok for tok in cleaned.split() if len(tok) >= 2]


class FixtureEmbeddingProvider:
    """Deterministic bag-of-tokens hash projection (offline; no network)."""

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
                byte = digest[i % len(digest)]
                vector[i] += (byte / 127.5) - 1.0
        return _l2_normalize(vector)


def _default_http_post(url: str, headers: dict[str, str], body: bytes, timeout: float) -> bytes:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


class OpenAICompatibleEmbeddingProvider:
    """Captain-local OpenAI-compatible embeddings HTTP (never CI default).

    Env:
    - COMPASS_EMBEDDING_API_KEY (required)
    - COMPASS_EMBEDDING_BASE_URL (default https://api.openai.com/v1)
    - COMPASS_EMBEDDING_MODEL (default text-embedding-3-small)
    """

    name = "openai-compatible"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        dimensions: int | None = None,
        timeout: float = 30.0,
        http_post: Callable[[str, dict[str, str], bytes, float], bytes] | None = None,
    ) -> None:
        self.api_key = (api_key if api_key is not None else os.environ.get("COMPASS_EMBEDDING_API_KEY", "")).strip()
        base = (
            base_url
            if base_url is not None
            else os.environ.get("COMPASS_EMBEDDING_BASE_URL", "https://api.openai.com/v1")
        ).strip().rstrip("/")
        self.base_url = base
        self.model = (
            model if model is not None else os.environ.get("COMPASS_EMBEDDING_MODEL", "text-embedding-3-small")
        ).strip()
        dim_env = os.environ.get("COMPASS_EMBEDDING_DIMENSIONS", "").strip()
        self._fixed_dimensions = dimensions
        if self._fixed_dimensions is None and dim_env.isdigit():
            self._fixed_dimensions = int(dim_env)
        self.timeout = timeout
        self._http_post = http_post or _default_http_post
        self._resolved_dimensions: int | None = self._fixed_dimensions

    @property
    def dimensions(self) -> int:
        if self._resolved_dimensions is not None:
            return self._resolved_dimensions
        return 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise EmbeddingProviderError("COMPASS_EMBEDDING_API_KEY is required for openai-compatible")
        if not self.base_url:
            raise EmbeddingProviderError("COMPASS_EMBEDDING_BASE_URL is required for openai-compatible")
        if not texts:
            return []
        url = f"{self.base_url}/embeddings"
        payload: dict = {"model": self.model, "input": texts}
        if self._fixed_dimensions is not None:
            payload["dimensions"] = self._fixed_dimensions
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            raw = self._http_post(url, headers, body, self.timeout)
        except urllib.error.HTTPError as exc:
            raise EmbeddingProviderError(f"embedding HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise EmbeddingProviderError(f"embedding request failed: {exc}") from exc
        try:
            doc = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EmbeddingProviderError("embedding response was not valid JSON") from exc
        data = doc.get("data")
        if not isinstance(data, list) or len(data) != len(texts):
            raise EmbeddingProviderError("embedding response missing data[]")
        ordered = sorted(data, key=lambda row: int(row.get("index", 0)))
        vectors: list[list[float]] = []
        for row in ordered:
            emb = row.get("embedding")
            if not isinstance(emb, list) or not emb:
                raise EmbeddingProviderError("embedding vector missing")
            vec = [float(x) for x in emb]
            if self._resolved_dimensions is None:
                self._resolved_dimensions = len(vec)
            vectors.append(_l2_normalize(vec))
        return vectors


def select_embedding_provider() -> EmbeddingProvider | None:
    """Return embedding provider from env, or None for TF-IDF-only path.

    Values:
    - ``tfidf`` / empty — None (use existing TF-IDF vector index only)
    - ``fixture`` — FixtureEmbeddingProvider
    - ``openai-compatible`` — OpenAICompatibleEmbeddingProvider (Captain local)
    """
    name = os.environ.get("COMPASS_EMBEDDING_PROVIDER", "tfidf").strip().lower() or "tfidf"
    if name in {"tfidf", "none", "off"}:
        return None
    if name in {"fixture", "fixtures", "hash"}:
        return FixtureEmbeddingProvider()
    if name in {"openai-compatible", "openai", "oai"}:
        return OpenAICompatibleEmbeddingProvider()
    # Unknown → fail closed to TF-IDF (no surprise network backends)
    return None
