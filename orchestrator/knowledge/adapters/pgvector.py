"""Hosted pgvector backend for knowledge semantic search (M13 / Neon)."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol

from orchestrator.knowledge.adapters.embeddings import (
    EmbeddingProvider,
    EmbeddingProviderError,
    FixtureEmbeddingProvider,
    select_embedding_provider,
)
from orchestrator.knowledge.embedding_index import _item_embed_text
from orchestrator.knowledge.store import list_knowledge_items


class HostedVectorError(RuntimeError):
    """Raised when hosted vector operations fail closed."""


@dataclass(frozen=True)
class PgvectorRecord:
    item_id: str
    kind: str | None
    embedding: list[float]


class PgvectorBackend(Protocol):
    """Namespace-scoped vector store with cosine similarity ranking."""

    def ensure_schema(self, dimensions: int) -> None: ...

    def upsert_items(self, namespace: str, records: list[PgvectorRecord]) -> int: ...

    def query(
        self,
        namespace: str,
        vector: list[float],
        *,
        top_n: int,
        kind: str | None,
    ) -> list[tuple[str, float]]: ...


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{float(v):.6f}" for v in vector) + "]"


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    left_norm = math.sqrt(sum(v * v for v in left))
    right_norm = math.sqrt(sum(v * v for v in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    return round(dot / (left_norm * right_norm), 4)


def pgvector_schema_sql(dimensions: int) -> str:
    """Return DDL for Captain-local Neon/pgvector bootstrap."""
    dim = int(dimensions)
    if dim <= 0:
        raise HostedVectorError("dimensions must be positive")
    return f"""CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS compass_knowledge_vectors (
  namespace TEXT NOT NULL,
  item_id TEXT NOT NULL,
  kind TEXT,
  embedding vector({dim}) NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (namespace, item_id)
);

CREATE INDEX IF NOT EXISTS compass_knowledge_vectors_kind_idx
  ON compass_knowledge_vectors (namespace, kind);
"""


class InMemoryPgvectorBackend:
    """Deterministic in-memory pgvector simulation for CI and tests."""

    name = "pgvector-mock"

    def __init__(self) -> None:
        self._rows: dict[tuple[str, str], PgvectorRecord] = {}
        self._dimensions: int | None = None

    def ensure_schema(self, dimensions: int) -> None:
        self._dimensions = int(dimensions)

    def upsert_items(self, namespace: str, records: list[PgvectorRecord]) -> int:
        count = 0
        for record in records:
            if self._dimensions is not None and len(record.embedding) != self._dimensions:
                raise HostedVectorError(
                    f"embedding dimension mismatch: expected {self._dimensions}, "
                    f"got {len(record.embedding)} for {record.item_id}"
                )
            key = (namespace, record.item_id)
            self._rows[key] = record
            count += 1
        return count

    def query(
        self,
        namespace: str,
        vector: list[float],
        *,
        top_n: int,
        kind: str | None,
    ) -> list[tuple[str, float]]:
        ranked: list[tuple[float, str]] = []
        for (ns, item_id), record in self._rows.items():
            if ns != namespace:
                continue
            if kind and record.kind != kind:
                continue
            score = _cosine_similarity(vector, record.embedding)
            if score <= 0:
                continue
            ranked.append((score, item_id))
        ranked.sort(key=lambda pair: (-pair[0], pair[1]))
        return [(item_id, score) for score, item_id in ranked[:top_n]]


ConnectFn = Callable[[], object]


class LivePgvectorBackend:
    """Captain-local Neon/Postgres pgvector backend (never CI default)."""

    name = "pgvector"

    def __init__(
        self,
        dsn: str,
        *,
        connect: ConnectFn | None = None,
    ) -> None:
        self._dsn = dsn.strip()
        if not self._dsn:
            raise HostedVectorError("COMPASS_VECTOR_DATABASE_URL is required")
        self._connect = connect or self._default_connect

    def _default_connect(self) -> object:
        try:
            import psycopg  # type: ignore[import-not-found]
        except ImportError as exc:
            raise HostedVectorError(
                "psycopg is required for live pgvector; install with: pip install 'psycopg[binary]'"
            ) from exc
        try:
            return psycopg.connect(self._dsn)
        except Exception as exc:  # noqa: BLE001 — convert driver errors to HostedVectorError
            raise HostedVectorError(f"pgvector connect failed: {exc}") from exc

    def ensure_schema(self, dimensions: int) -> None:
        sql = pgvector_schema_sql(dimensions)
        try:
            with self._connect() as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute(sql)
        except HostedVectorError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise HostedVectorError(f"pgvector schema apply failed: {exc}") from exc

    def upsert_items(self, namespace: str, records: list[PgvectorRecord]) -> int:
        if not records:
            return 0
        upsert_sql = """
            INSERT INTO compass_knowledge_vectors (namespace, item_id, kind, embedding, updated_at)
            VALUES (%s, %s, %s, %s::vector, now())
            ON CONFLICT (namespace, item_id) DO UPDATE SET
              kind = EXCLUDED.kind,
              embedding = EXCLUDED.embedding,
              updated_at = now()
        """
        count = 0
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    for record in records:
                        cur.execute(
                            upsert_sql,
                            (
                                namespace,
                                record.item_id,
                                record.kind,
                                _vector_literal(record.embedding),
                            ),
                        )
                        count += 1
                conn.commit()
        except HostedVectorError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise HostedVectorError(f"pgvector upsert failed: {exc}") from exc
        return count

    def query(
        self,
        namespace: str,
        vector: list[float],
        *,
        top_n: int,
        kind: str | None,
    ) -> list[tuple[str, float]]:
        literal = _vector_literal(vector)
        if kind:
            sql = """
                SELECT item_id, 1 - (embedding <=> %s::vector) AS score
                FROM compass_knowledge_vectors
                WHERE namespace = %s AND kind = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params: tuple[object, ...] = (literal, namespace, kind, literal, top_n)
        else:
            sql = """
                SELECT item_id, 1 - (embedding <=> %s::vector) AS score
                FROM compass_knowledge_vectors
                WHERE namespace = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params = (literal, namespace, literal, top_n)
        ranked: list[tuple[str, float]] = []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
        except HostedVectorError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise HostedVectorError(f"pgvector query failed: {exc}") from exc
        for item_id, score in rows:
            ranked.append((str(item_id), round(float(score), 4)))
        return ranked


_MOCK_BACKEND: InMemoryPgvectorBackend | None = None


def _get_mock_backend() -> InMemoryPgvectorBackend:
    global _MOCK_BACKEND
    if _MOCK_BACKEND is None:
        _MOCK_BACKEND = InMemoryPgvectorBackend()
    return _MOCK_BACKEND


def reset_mock_hosted_vector_backend() -> None:
    """Clear the in-process mock backend (tests only)."""
    global _MOCK_BACKEND
    _MOCK_BACKEND = None


def vector_namespace(repo_root: Path | None = None) -> str:
    explicit = os.environ.get("COMPASS_VECTOR_NAMESPACE", "").strip()
    if explicit:
        return explicit
    if repo_root is not None:
        return Path(repo_root).resolve().name
    return "default"


def select_hosted_vector_backend() -> PgvectorBackend | None:
    """Return hosted backend from env, or None for file-backed vector search only."""
    name = os.environ.get("COMPASS_VECTOR_PROVIDER", "file").strip().lower() or "file"
    if name in {"file", "tfidf", "none", "off"}:
        return None
    if name in {"mock", "memory", "fixture", "pgvector-mock"}:
        return _get_mock_backend()
    if name in {"pgvector", "neon", "postgres"}:
        dsn = os.environ.get("COMPASS_VECTOR_DATABASE_URL", "").strip()
        if not dsn:
            raise HostedVectorError("COMPASS_VECTOR_DATABASE_URL required for pgvector provider")
        return LivePgvectorBackend(dsn)
    return None


def build_pgvector_records(
    repo_root: Path,
    provider: EmbeddingProvider | None = None,
) -> list[PgvectorRecord]:
    provider = provider or select_embedding_provider() or FixtureEmbeddingProvider()
    items = list_knowledge_items(repo_root)
    texts = [_item_embed_text(item) for item in items]
    vectors = provider.embed(texts)
    records: list[PgvectorRecord] = []
    for item, vec in zip(items, vectors):
        records.append(
            PgvectorRecord(
                item_id=str(item["item_id"]),
                kind=str(item.get("kind") or "") or None,
                embedding=vec,
            )
        )
    return records


def sync_knowledge_vectors(
    repo_root: Path,
    *,
    backend: PgvectorBackend | None = None,
    provider: EmbeddingProvider | None = None,
) -> dict:
    """Upsert all knowledge items into the hosted vector store (explicit CLI only)."""
    repo_root = Path(repo_root)
    backend = backend or select_hosted_vector_backend()
    if backend is None:
        raise HostedVectorError(
            "hosted vector sync requires COMPASS_VECTOR_PROVIDER=pgvector or mock"
        )
    provider = provider or select_embedding_provider() or FixtureEmbeddingProvider()
    records = build_pgvector_records(repo_root, provider=provider)
    if not records:
        return {
            "namespace": vector_namespace(repo_root),
            "backend": getattr(backend, "name", "pgvector"),
            "upserted": 0,
            "dimensions": provider.dimensions,
            "synced_at": _utc_now(),
        }
    backend.ensure_schema(provider.dimensions)
    namespace = vector_namespace(repo_root)
    upserted = backend.upsert_items(namespace, records)
    return {
        "namespace": namespace,
        "backend": getattr(backend, "name", "pgvector"),
        "upserted": upserted,
        "dimensions": provider.dimensions,
        "synced_at": _utc_now(),
    }


def query_hosted_vector_scores(
    repo_root: Path,
    query: str,
    *,
    kind: str | None,
    top_n: int,
    backend: PgvectorBackend | None = None,
    provider: EmbeddingProvider | None = None,
) -> list[tuple[str, float]]:
    """Query hosted vectors; raise HostedVectorError only for caller to handle.

    Callers that must never crash (plan Knowledge Context) should catch
    HostedVectorError and fall back to dense/TF-IDF.
    """
    if backend is None:
        backend = select_hosted_vector_backend()
    if backend is None:
        return []
    provider = provider or select_embedding_provider()
    if provider is None:
        return []
    try:
        query_vec = provider.embed([query])[0]
    except EmbeddingProviderError:
        return []
    if not query_vec or all(v == 0.0 for v in query_vec):
        return []
    namespace = vector_namespace(repo_root)
    try:
        return backend.query(namespace, query_vec, top_n=top_n, kind=kind)
    except HostedVectorError:
        raise
    except Exception as exc:  # noqa: BLE001 — any live/driver failure → fail closed for callers
        raise HostedVectorError(f"hosted vector query failed: {exc}") from exc
