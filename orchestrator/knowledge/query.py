"""Ranked keyword, vector, and hybrid search over the knowledge store."""

from __future__ import annotations

from pathlib import Path

from orchestrator.knowledge.adapters.embeddings import select_embedding_provider
from orchestrator.knowledge.embedding_index import (
    embedding_index_exists,
    query_embedding_scores,
)
from orchestrator.knowledge.index import load_index, tokenize, write_index
from orchestrator.knowledge.store import list_knowledge_items
from orchestrator.knowledge.vector_index import (
    HYBRID_KEYWORD_WEIGHT,
    HYBRID_VECTOR_WEIGHT,
    query_vector_scores,
    vector_index_exists,
)


def _score_item(query_tokens: set[str], item_tokens: list[str]) -> float:
    if not query_tokens:
        return 0.0
    item_set = set(item_tokens)
    overlap = len(query_tokens & item_set)
    if overlap == 0:
        return 0.0
    return overlap / len(query_tokens)


def _keyword_ranked(repo_root: Path, query: str, *, kind: str | None, top_n: int) -> dict[str, float]:
    index = load_index(repo_root)
    inverted = index.get("inverted") or {}
    item_tokens_map = index.get("item_tokens") or {}
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return {}

    candidate_scores: dict[str, float] = {}
    for token in query_tokens:
        for item_id in inverted.get(token, []):
            candidate_scores[item_id] = candidate_scores.get(item_id, 0.0) + 1.0

    items_by_id = {str(i["item_id"]): i for i in list_knowledge_items(repo_root)}
    ranked: dict[str, float] = {}
    for item_id in candidate_scores:
        item = items_by_id.get(item_id)
        if item is None:
            continue
        if kind and str(item.get("kind")) != kind:
            continue
        score = _score_item(query_tokens, item_tokens_map.get(item_id, []))
        if score <= 0:
            continue
        ranked[item_id] = round(score, 4)
    return ranked


def _dense_ranked(repo_root: Path, query: str, *, kind: str | None, top_n: int) -> dict[str, float]:
    """Dense embedding scores when embedding provider + embedding index are active."""
    from orchestrator.knowledge.adapters.embeddings import EmbeddingProviderError

    provider = select_embedding_provider()
    if provider is None or not embedding_index_exists(repo_root):
        return {}
    items_by_id = {str(i["item_id"]): i for i in list_knowledge_items(repo_root)}
    ranked: dict[str, float] = {}
    try:
        scored = query_embedding_scores(
            repo_root, query, top_n=top_n * 3, provider=provider
        )
    except EmbeddingProviderError:
        return {}
    for item_id, score in scored:
        item = items_by_id.get(item_id)
        if item is None:
            continue
        if kind and str(item.get("kind")) != kind:
            continue
        ranked[item_id] = score
        if len(ranked) >= top_n:
            break
    return ranked


def _tfidf_ranked(repo_root: Path, query: str, *, kind: str | None, top_n: int) -> dict[str, float]:
    if not vector_index_exists(repo_root):
        return {}
    items_by_id = {str(i["item_id"]): i for i in list_knowledge_items(repo_root)}
    ranked: dict[str, float] = {}
    for item_id, score in query_vector_scores(repo_root, query, top_n=top_n * 3):
        item = items_by_id.get(item_id)
        if item is None:
            continue
        if kind and str(item.get("kind")) != kind:
            continue
        ranked[item_id] = score
        if len(ranked) >= top_n:
            break
    return ranked


def _vector_ranked(
    repo_root: Path, query: str, *, kind: str | None, top_n: int
) -> tuple[dict[str, float], str]:
    """Return vector scores and backend label. Dense first; TF-IDF always fallback."""
    provider = select_embedding_provider()
    dense = _dense_ranked(repo_root, query, kind=kind, top_n=top_n)
    if dense:
        name = getattr(provider, "name", "") if provider is not None else ""
        if name == "openai-compatible":
            backend = "openai-compatible"
        elif name == "fixture":
            backend = "fixture-embedding"
        elif name:
            backend = str(name)
        else:
            backend = "dense"
        return dense, backend
    tfidf = _tfidf_ranked(repo_root, query, kind=kind, top_n=top_n)
    if tfidf:
        return tfidf, "tfidf"
    return {}, "none"


def _merge_hybrid(
    keyword_scores: dict[str, float],
    vector_scores: dict[str, float],
) -> dict[str, tuple[float, float, float]]:
    merged: dict[str, tuple[float, float, float]] = {}
    for item_id in set(keyword_scores) | set(vector_scores):
        keyword_score = keyword_scores.get(item_id, 0.0)
        vector_score = vector_scores.get(item_id, 0.0)
        if keyword_score <= 0 and vector_score <= 0:
            continue
        final_score = round(
            HYBRID_KEYWORD_WEIGHT * keyword_score + HYBRID_VECTOR_WEIGHT * vector_score,
            4,
        )
        merged[item_id] = (final_score, keyword_score, vector_score)
    return merged


def query_knowledge(
    repo_root: Path,
    query: str,
    *,
    kind: str | None = None,
    top_n: int = 10,
    rebuild_index: bool = False,
    mode: str = "keyword",
) -> list[dict]:
    """Return ranked knowledge items matching query (read-only)."""
    repo_root = Path(repo_root)
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"keyword", "vector", "hybrid"}:
        normalized_mode = "keyword"

    if rebuild_index:
        write_index(repo_root)

    items_by_id = {str(i["item_id"]): i for i in list_knowledge_items(repo_root)}
    if not items_by_id:
        return []

    if normalized_mode == "keyword":
        keyword_scores = _keyword_ranked(repo_root, query, kind=kind, top_n=top_n)
        ranked = sorted(keyword_scores.items(), key=lambda pair: (-pair[1], pair[0]))
        results: list[dict] = []
        for item_id, score in ranked[:top_n]:
            item = dict(items_by_id[item_id])
            item["query_score"] = score
            item["keyword_score"] = score
            item["search_mode"] = "keyword"
            results.append(item)
        return results

    if normalized_mode == "vector":
        vector_scores, backend = _vector_ranked(repo_root, query, kind=kind, top_n=top_n)
        if not vector_scores:
            return []
        ranked = sorted(vector_scores.items(), key=lambda pair: (-pair[1], pair[0]))
        results = []
        for item_id, score in ranked[:top_n]:
            item = dict(items_by_id[item_id])
            item["query_score"] = score
            item["vector_score"] = score
            item["search_mode"] = "vector"
            item["vector_backend"] = backend
            results.append(item)
        return results

    keyword_scores = _keyword_ranked(repo_root, query, kind=kind, top_n=top_n)
    vector_scores, backend = _vector_ranked(repo_root, query, kind=kind, top_n=top_n)
    if not vector_scores:
        ranked = sorted(keyword_scores.items(), key=lambda pair: (-pair[1], pair[0]))
        results = []
        for item_id, score in ranked[:top_n]:
            item = dict(items_by_id[item_id])
            item["query_score"] = score
            item["keyword_score"] = score
            item["search_mode"] = "hybrid"
            item["search_fallback"] = "keyword-only"
            results.append(item)
        return results

    merged = _merge_hybrid(keyword_scores, vector_scores)
    ranked = sorted(merged.items(), key=lambda pair: (-pair[1][0], -pair[1][1], pair[0]))
    results = []
    for item_id, (final_score, keyword_score, vector_score) in ranked[:top_n]:
        item = dict(items_by_id[item_id])
        item["query_score"] = final_score
        item["keyword_score"] = keyword_score
        item["vector_score"] = vector_score
        item["search_mode"] = "hybrid"
        item["vector_backend"] = backend
        results.append(item)
    return results
