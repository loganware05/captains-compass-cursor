"""Build keyword inverted index for knowledge items (stdlib-first)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.knowledge.store import KnowledgeStoreError, index_path, list_knowledge_items

_TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]{1,48}")
STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "into",
        "under",
        "via",
        "are",
        "was",
        "not",
    }
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tokenize(text: str) -> list[str]:
    normalized = text.lower().replace("-", " ").replace("_", " ")
    tokens = []
    for match in _TOKEN.finditer(normalized):
        token = match.group(0)
        if token not in STOPWORDS and len(token) >= 2:
            tokens.append(token)
    return tokens


def extract_tokens(item: dict) -> set[str]:
    parts = [
        str(item.get("title") or ""),
        str(item.get("summary") or ""),
        str(item.get("kind") or ""),
    ]
    parts.extend(str(k) for k in item.get("keywords") or [])
    source = item.get("source_artifact") or {}
    parts.append(str(source.get("type") or ""))
    tokens: set[str] = set()
    for part in parts:
        tokens.update(tokenize(part))
    return tokens


def build_index(repo_root: Path) -> dict:
    """Rebuild keyword inverted index from all knowledge items."""
    items = list_knowledge_items(repo_root)
    inverted: dict[str, list[str]] = {}
    item_tokens: dict[str, list[str]] = {}
    for item in items:
        item_id = str(item["item_id"])
        tokens = sorted(extract_tokens(item))
        item_tokens[item_id] = tokens
        for token in tokens:
            bucket = inverted.setdefault(token, [])
            if item_id not in bucket:
                bucket.append(item_id)
    for token in inverted:
        inverted[token].sort()
    return {
        "version": "1.0.0",
        "kind": "keyword-index",
        "item_count": len(items),
        "token_count": len(inverted),
        "inverted": inverted,
        "item_tokens": item_tokens,
        "built_at": _utc_now(),
    }


def write_index(repo_root: Path, index: dict | None = None) -> Path:
    index = index if index is not None else build_index(repo_root)
    path = index_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def load_index(repo_root: Path) -> dict:
    path = index_path(repo_root)
    if not path.is_file():
        return build_index(repo_root)
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict) or "inverted" not in doc:
        raise KnowledgeStoreError(f"invalid index: {path}")
    return doc
