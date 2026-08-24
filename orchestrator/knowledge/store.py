"""Knowledge Steward store paths and helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path

from orchestrator.schemas.validate import ValidationError, validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
_SECRET_PATTERN = re.compile(r"\.env|secret|password|token|api[_-]?key", re.I)


class KnowledgeStoreError(ValueError):
    """Raised when knowledge store operations fail."""


def knowledge_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "knowledge"


def items_dir(repo_root: Path) -> Path:
    return knowledge_root(repo_root) / "items"


def index_path(repo_root: Path) -> Path:
    return knowledge_root(repo_root) / "index.json"


def vector_index_path(repo_root: Path) -> Path:
    return knowledge_root(repo_root) / "vector-index.json"


def ingest_log_dir(repo_root: Path) -> Path:
    return knowledge_root(repo_root) / "ingest-log"


def procedures_dir(repo_root: Path) -> Path:
    return knowledge_root(repo_root) / "procedures"


def ensure_store_layout(repo_root: Path) -> None:
    for path in (
        items_dir(repo_root),
        ingest_log_dir(repo_root),
        procedures_dir(repo_root) / "proposals",
        procedures_dir(repo_root) / "staging",
        procedures_dir(repo_root) / "approved",
    ):
        path.mkdir(parents=True, exist_ok=True)
    intel_cache = Path(repo_root) / ".agent" / "intelligence" / "ti-cache"
    intel_cache.mkdir(parents=True, exist_ok=True)


def assert_safe_id(value: str, label: str = "item_id") -> None:
    if not value or not _SAFE_ID.match(value):
        raise KnowledgeStoreError(f"unsafe {label}: {value!r}")


def reject_secret_path(path: str) -> None:
    if _SECRET_PATTERN.search(path):
        raise KnowledgeStoreError(f"secret-like path rejected: {path!r}")


def write_knowledge_item(repo_root: Path, item: dict) -> Path:
    validate_document(item, "knowledge-item.schema.json")
    item_id = str(item["item_id"])
    assert_safe_id(item_id)
    source_path = str((item.get("source_artifact") or {}).get("path") or "")
    if source_path:
        reject_secret_path(source_path)
    ensure_store_layout(repo_root)
    path = items_dir(repo_root) / f"{item_id}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(item, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def load_knowledge_item(repo_root: Path, item_id: str) -> dict:
    assert_safe_id(item_id)
    path = items_dir(repo_root) / f"{item_id}.json"
    if not path.is_file():
        raise KnowledgeStoreError(f"knowledge item not found: {path}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "knowledge-item.schema.json")
    return doc


def list_knowledge_items(repo_root: Path) -> list[dict]:
    directory = items_dir(repo_root)
    if not directory.is_dir():
        return []
    results: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
            validate_document(doc, "knowledge-item.schema.json")
            results.append(doc)
        except (OSError, json.JSONDecodeError, ValidationError):
            continue
    return results
