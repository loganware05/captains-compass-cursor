"""Ranked keyword search over the knowledge store."""

from __future__ import annotations

from pathlib import Path

from orchestrator.knowledge.index import load_index, tokenize, write_index
from orchestrator.knowledge.store import list_knowledge_items


def _score_item(query_tokens: set[str], item_tokens: list[str]) -> float:
    if not query_tokens:
        return 0.0
    item_set = set(item_tokens)
    overlap = len(query_tokens & item_set)
    if overlap == 0:
        return 0.0
    return overlap / len(query_tokens)


def query_knowledge(
    repo_root: Path,
    query: str,
    *,
    kind: str | None = None,
    top_n: int = 10,
    rebuild_index: bool = False,
) -> list[dict]:
    """Return ranked knowledge items matching query tokens (read-only)."""
    repo_root = Path(repo_root)
    if rebuild_index:
        write_index(repo_root)
    index = load_index(repo_root)
    inverted = index.get("inverted") or {}
    item_tokens_map = index.get("item_tokens") or {}

    query_tokens = set(tokenize(query))
    if not query_tokens:
        return []

    candidate_scores: dict[str, float] = {}
    for token in query_tokens:
        for item_id in inverted.get(token, []):
            candidate_scores[item_id] = candidate_scores.get(item_id, 0.0) + 1.0

    items_by_id = {str(i["item_id"]): i for i in list_knowledge_items(repo_root)}
    ranked: list[tuple[float, str]] = []
    for item_id, raw in candidate_scores.items():
        item = items_by_id.get(item_id)
        if item is None:
            continue
        if kind and str(item.get("kind")) != kind:
            continue
        score = _score_item(query_tokens, item_tokens_map.get(item_id, []))
        if score <= 0:
            continue
        ranked.append((score, item_id))

    ranked.sort(key=lambda pair: (-pair[0], pair[1]))
    results: list[dict] = []
    for score, item_id in ranked[:top_n]:
        item = dict(items_by_id[item_id])
        item["query_score"] = round(score, 4)
        results.append(item)
    return results
