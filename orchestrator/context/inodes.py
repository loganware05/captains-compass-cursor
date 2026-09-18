"""Inode-style metadata store (M40).

Structural metadata (exported interfaces, function signatures, I/O types,
declared complexities) is indexed under ``.agent/inodes/`` decoupled from raw
source. Inodes are content-addressed: ``<sha256-of-source-bytes>.json`` — the
same content always yields the same inode, and a source edit produces a new
inode ID, which is what makes staleness detection and reputation pinning
sound. Inodes never contain file contents, only metadata.

The store is fully deterministic: no wall-clock timestamps are written, so
identical source trees produce byte-identical stores.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterator

from orchestrator.context.extract import extract_for_path
from orchestrator.schemas.validate import validate_document

INODE_STORE_VERSION = "1.0.0"
INDEX_FILENAME = "index.json"
DEFAULT_STORE_DIR = Path(".agent") / "inodes"

DEFAULT_EXCLUDE_DIRS = frozenset(
    {
        ".git",
        ".agent",
        "node_modules",
        "dist",
        "build",
        "coverage",
        ".venv",
        "venv",
        "__pycache__",
        ".next",
        "DerivedData",
        "Pods",
    }
)
INDEXED_SUFFIXES = frozenset({".py", ".ts", ".tsx", ".mts", ".cts"})


class InodeStoreError(ValueError):
    """Raised when the inode store cannot be built or read safely."""


def content_hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inode_id_for(content_hash: str) -> str:
    return f"ino-{content_hash[:16]}"


def module_route_for(rel_path: str) -> str:
    """Context route (domain/module) for a repo-relative source path."""
    parts = Path(rel_path).parent.parts
    return "/".join(parts[:2]) if parts else ""


def build_inode(repo_root: Path, rel_path: str) -> dict[str, Any]:
    repo_root = Path(repo_root)
    data = (repo_root / rel_path).read_bytes()
    source = data.decode("utf-8", errors="replace")
    extracted = extract_for_path(rel_path, source)
    chash = content_hash_bytes(data)
    symbols = extracted["symbols"]
    exports = sorted({symbol["name"] for symbol in symbols if symbol.get("exported")})
    inode = {
        "inode_id": inode_id_for(chash),
        "store_version": INODE_STORE_VERSION,
        "source_path": rel_path,
        "content_hash": chash,
        "language": extracted["language"],
        "byte_size": len(data),
        "module": module_route_for(rel_path),
        "exports": exports,
        "symbols": symbols,
        "imports": extracted["imports"],
        "declared_complexity": extracted["declared_complexity"],
    }
    validate_document(inode, "context-inode.schema.json")
    return inode


def iter_source_files(
    repo_root: Path,
    *,
    exclude_dirs: frozenset[str] = DEFAULT_EXCLUDE_DIRS,
) -> Iterator[str]:
    """Yield repo-relative POSIX paths of indexable source files, sorted."""
    repo_root = Path(repo_root)
    collected: list[str] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root)
        if any(part in exclude_dirs for part in rel.parts):
            continue
        if path.suffix.lower() not in INDEXED_SUFFIXES:
            continue
        collected.append(rel.as_posix())
    yield from sorted(collected)


def build_store(
    repo_root: Path,
    *,
    output_dir: Path | None = None,
    exclude_dirs: frozenset[str] = DEFAULT_EXCLUDE_DIRS,
) -> dict[str, Any]:
    """Build the inode store for a repository. Deterministic: same sources ⇒ same bytes."""
    repo_root = Path(repo_root)
    store_dir = Path(output_dir) if output_dir else repo_root / DEFAULT_STORE_DIR
    store_dir.mkdir(parents=True, exist_ok=True)

    inodes_by_hash: dict[str, dict[str, Any]] = {}
    aliases: dict[str, list[str]] = {}
    files_index: dict[str, Any] = {}

    for rel_path in iter_source_files(repo_root, exclude_dirs=exclude_dirs):
        inode = build_inode(repo_root, rel_path)
        chash = inode["content_hash"]
        if chash in inodes_by_hash:
            aliases.setdefault(chash, []).append(rel_path)
        else:
            inodes_by_hash[chash] = inode
        files_index[rel_path] = {
            "inode_id": inode["inode_id"],
            "content_hash": chash,
            "byte_size": inode["byte_size"],
            "module": inode["module"],
        }

    for chash, inode in inodes_by_hash.items():
        extra = sorted(aliases.get(chash, []))
        if extra:
            inode["alias_paths"] = extra
            validate_document(inode, "context-inode.schema.json")
        out_path = store_dir / f"{chash}.json"
        with out_path.open("w", encoding="utf-8") as handle:
            json.dump(inode, handle, indent=2, sort_keys=True)
            handle.write("\n")

    index = {
        "store_version": INODE_STORE_VERSION,
        "file_count": len(files_index),
        "inode_count": len(inodes_by_hash),
        "files": files_index,
        "inodes": sorted(inode["inode_id"] for inode in inodes_by_hash.values()),
    }
    index_path = store_dir / INDEX_FILENAME
    with index_path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return index


def load_index(repo_root: Path, *, store_dir: Path | None = None) -> dict[str, Any]:
    path = (Path(store_dir) if store_dir else Path(repo_root) / DEFAULT_STORE_DIR) / INDEX_FILENAME
    if not path.is_file():
        raise InodeStoreError(f"inode index not found: {path} (run scripts/build-context-inodes.sh)")
    with path.open(encoding="utf-8") as handle:
        index = json.load(handle)
    if not isinstance(index, dict) or "files" not in index:
        raise InodeStoreError(f"inode index malformed: {path}")
    return index


def load_inode(repo_root: Path, inode_id: str, *, store_dir: Path | None = None) -> dict[str, Any]:
    base = Path(store_dir) if store_dir else Path(repo_root) / DEFAULT_STORE_DIR
    index = load_index(repo_root, store_dir=base)
    for entry in index["files"].values():
        if entry["inode_id"] == inode_id:
            path = base / f"{entry['content_hash']}.json"
            with path.open(encoding="utf-8") as handle:
                return json.load(handle)
    raise InodeStoreError(f"inode not found in store: {inode_id}")


def inode_for_path(repo_root: Path, rel_path: str, *, store_dir: Path | None = None) -> dict[str, Any] | None:
    """Return the inode for a repo-relative source path, or None when unindexed."""
    base = Path(store_dir) if store_dir else Path(repo_root) / DEFAULT_STORE_DIR
    try:
        index = load_index(repo_root, store_dir=base)
    except InodeStoreError:
        return None
    entry = index["files"].get(rel_path)
    if not entry:
        return None
    path = base / f"{entry['content_hash']}.json"
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def find_stale(repo_root: Path, *, store_dir: Path | None = None) -> list[dict[str, str]]:
    """Return indexed paths whose current content hash differs from the store.

    Missing store ⇒ empty list (callers treat absence as "not built", not
    "stale"). Deleted or modified sources are reported with a reason.
    """
    repo_root = Path(repo_root)
    try:
        index = load_index(repo_root, store_dir=store_dir)
    except InodeStoreError:
        return []
    stale: list[dict[str, str]] = []
    for rel_path, entry in sorted(index["files"].items()):
        source = repo_root / rel_path
        if not source.is_file():
            stale.append({"path": rel_path, "reason": "deleted"})
            continue
        current = content_hash_bytes(source.read_bytes())
        if current != entry["content_hash"]:
            stale.append({"path": rel_path, "reason": "modified"})
    return stale
