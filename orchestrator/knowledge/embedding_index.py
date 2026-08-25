"""Dense embedding index for knowledge items (fixture provider, M11)."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.knowledge.adapters.embeddings import (
    EmbeddingProvider,
    FixtureEmbeddingProvider,
    select_embedding_provider,
)
from orchestrator.knowledge.store import (
    KnowledgeStoreError,
    embedding_index_path,
    list_knowledge_items,
)
from orchestrator.schemas.validate import validate_document


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _round_score(value: float) -> float:
    return round(value, 4)


def _item_embed_text(item: dict) -> str:
    parts = [
        str(item.get("title") or ""),
        str(item.get("summary") or ""),
        str(item.get("kind") or ""),
        " ".join(str(t) for t in (item.get("tags") or [])),
    ]
    return " ".join(p for p in parts if p).strip()


def cosine_dense(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    left_norm = math.sqrt(sum(v * v for v in left))
    right_norm = math.sqrt(sum(v * v for v in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    return dot / (left_norm * right_norm)


def build_embedding_index(
    repo_root: Path,
    provider: EmbeddingProvider | None = None,
) -> dict:
    """Build dense vectors for all knowledge items using the given provider."""
    provider = provider or select_embedding_provider() or FixtureEmbeddingProvider()
    items = list_knowledge_items(repo_root)
    texts = [_item_embed_text(item) for item in items]
    vectors_list = provider.embed(texts)
    vectors: dict[str, list[float]] = {}
    for item, vec in zip(items, vectors_list):
        vectors[str(item["item_id"])] = vec
    return {
        "version": "1.0.0",
        "kind": "dense-embedding-index",
        "backend": provider.name,
        "dimensions": provider.dimensions,
        "item_count": len(items),
        "vectors": vectors,
        "built_at": _utc_now(),
    }


def write_embedding_index(
    repo_root: Path,
    index: dict | None = None,
    provider: EmbeddingProvider | None = None,
) -> Path:
    index = index if index is not None else build_embedding_index(repo_root, provider=provider)
    validate_document(index, "embedding-index.schema.json")
    path = embedding_index_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def load_embedding_index(repo_root: Path) -> dict | None:
    path = embedding_index_path(repo_root)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise KnowledgeStoreError(f"invalid embedding index: {path}")
    validate_document(doc, "embedding-index.schema.json")
    return doc


def embedding_index_exists(repo_root: Path) -> bool:
    return embedding_index_path(repo_root).is_file()


def query_embedding_scores(
    repo_root: Path,
    query: str,
    *,
    top_n: int = 10,
    provider: EmbeddingProvider | None = None,
) -> list[tuple[str, float]]:
    """Return ranked (item_id, embedding_score) from the dense index."""
    index = load_embedding_index(repo_root)
    if index is None:
        return []
    provider = provider or select_embedding_provider() or FixtureEmbeddingProvider()
    query_vec = provider.embed([query])[0]
    if not query_vec or all(v == 0.0 for v in query_vec):
        return []
    ranked: list[tuple[float, str]] = []
    for item_id, doc_vector in (index.get("vectors") or {}).items():
        if not isinstance(doc_vector, list):
            continue
        score = cosine_dense(query_vec, [float(x) for x in doc_vector])
        if score <= 0:
            continue
        ranked.append((_round_score(score), str(item_id)))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]))
    return [(item_id, score) for score, item_id in ranked[:top_n]]
