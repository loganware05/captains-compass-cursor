"""TF-IDF vector index for knowledge items (stdlib-only, M6)."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.knowledge.index import extract_tokens, tokenize
from orchestrator.knowledge.store import KnowledgeStoreError, list_knowledge_items, vector_index_path
from orchestrator.schemas.validate import validate_document

HYBRID_KEYWORD_WEIGHT = 0.5
HYBRID_VECTOR_WEIGHT = 0.5


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _round_score(value: float) -> float:
    return round(value, 4)


def _document_tokens(item: dict) -> list[str]:
    return sorted(extract_tokens(item))


def _term_frequency(tokens: list[str]) -> dict[str, float]:
    if not tokens:
        return {}
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    total = float(len(tokens))
    return {token: count / total for token, count in counts.items()}


def _compute_idf(documents: list[list[str]]) -> dict[str, float]:
    doc_count = len(documents)
    if doc_count == 0:
        return {}
    df: dict[str, int] = {}
    for tokens in documents:
        for token in set(tokens):
            df[token] = df.get(token, 0) + 1
    return {
        token: math.log((doc_count + 1.0) / (freq + 1.0)) + 1.0 for token, freq in df.items()
    }


def _tfidf_vector(tf: dict[str, float], idf: dict[str, float]) -> dict[str, float]:
    return {token: tf_val * idf.get(token, 0.0) for token, tf_val in tf.items() if idf.get(token, 0.0) > 0}


def _vector_norm(vector: dict[str, float]) -> float:
    return math.sqrt(sum(weight * weight for weight in vector.values()))


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    left_norm = _vector_norm(left)
    right_norm = _vector_norm(right)
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    dot = sum(left.get(token, 0.0) * right.get(token, 0.0) for token in set(left) | set(right))
    return dot / (left_norm * right_norm)


def build_vector_index(repo_root: Path) -> dict:
    """Build TF-IDF sparse vectors from all knowledge items."""
    items = list_knowledge_items(repo_root)
    documents = [_document_tokens(item) for item in items]
    idf = _compute_idf(documents)
    vectors: dict[str, dict[str, float]] = {}
    for item, tokens in zip(items, documents):
        item_id = str(item["item_id"])
        tf = _term_frequency(tokens)
        sparse = _tfidf_vector(tf, idf)
        vectors[item_id] = {token: _round_score(weight) for token, weight in sparse.items()}
    return {
        "version": "1.0.0",
        "kind": "tfidf-vector-index",
        "item_count": len(items),
        "idf": {token: _round_score(weight) for token, weight in idf.items()},
        "vectors": vectors,
        "built_at": _utc_now(),
    }


def write_vector_index(repo_root: Path, index: dict | None = None) -> Path:
    index = index if index is not None else build_vector_index(repo_root)
    validate_document(index, "vector-index.schema.json")
    path = vector_index_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def load_vector_index(repo_root: Path) -> dict | None:
    path = vector_index_path(repo_root)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise KnowledgeStoreError(f"invalid vector index: {path}")
    validate_document(doc, "vector-index.schema.json")
    return doc


def vector_index_exists(repo_root: Path) -> bool:
    return vector_index_path(repo_root).is_file()


def _query_vector_from_index(index: dict, query: str) -> dict[str, float]:
    idf = index.get("idf") or {}
    tokens = tokenize(query)
    if not tokens:
        return {}
    tf = _term_frequency(tokens)
    sparse = _tfidf_vector(tf, idf)
    return {token: _round_score(weight) for token, weight in sparse.items()}


def query_vector_scores(repo_root: Path, query: str, *, top_n: int = 10) -> list[tuple[str, float]]:
    """Return ranked (item_id, vector_score) pairs from the vector index."""
    index = load_vector_index(repo_root)
    if index is None:
        return []
    query_vector = _query_vector_from_index(index, query)
    if not query_vector:
        return []
    vectors = index.get("vectors") or {}
    ranked: list[tuple[float, str]] = []
    for item_id, doc_vector in vectors.items():
        score = cosine_similarity(query_vector, doc_vector)
        if score <= 0:
            continue
        ranked.append((_round_score(score), str(item_id)))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]))
    return [(item_id, score) for score, item_id in ranked[:top_n]]


def select_knowledge_search_mode(repo_root: Path) -> str:
    """Resolve search mode: env override, hybrid when vector index exists, else keyword."""
    import os

    env = os.environ.get("COMPASS_KNOWLEDGE_SEARCH_MODE", "").strip().lower()
    if env in {"keyword", "vector", "hybrid"}:
        return env
    if vector_index_exists(repo_root):
        return "hybrid"
    return "keyword"
