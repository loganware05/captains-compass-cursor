"""Directory-style sequential context route walking (M40).

The context tree under ``.agent/context/`` mirrors the source tree:
``<domain>/<module>/`` segments derived from repo-relative source paths. Each
level carries a small generated ``node.json`` (summary + child segments +
inode refs for its subtree). The walker resolves a route one segment at a
time — like a path walk — loading only the nodes on the walked path, and
returns inode *pointers* for the resolved scope. Raw source is never loaded
by the walker; callers page in source explicitly when needed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from orchestrator.context.inodes import DEFAULT_STORE_DIR, load_index
from orchestrator.schemas.validate import validate_document

NODE_FILENAME = "node.json"
DEFAULT_CONTEXT_ROOT = Path(".agent") / "context"
_MAX_SUMMARY_EXPORTS = 8


class ContextWalkError(ValueError):
    """Raised when a context route cannot be resolved."""


def node_id_for(route: str) -> str:
    return f"ctx-{hashlib.sha256(route.encode('utf-8')).hexdigest()[:12]}"


def _summarize(exports: list[str], file_count: int) -> str:
    shown = exports[:_MAX_SUMMARY_EXPORTS]
    suffix = ", …" if len(exports) > _MAX_SUMMARY_EXPORTS else ""
    listing = ", ".join(shown) + suffix if shown else "none"
    return f"{file_count} file(s); exports: {listing}"


def derive_context_tree(
    repo_root: Path,
    *,
    store_dir: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Derive the ``.agent/context/`` node tree from the inode index.

    Deterministic: identical inode stores produce byte-identical nodes.
    Node summaries are computed in a single pass from inode export metadata.
    """
    repo_root = Path(repo_root)
    index = load_index(repo_root, store_dir=store_dir)
    base = Path(store_dir) if store_dir else repo_root / DEFAULT_STORE_DIR
    context_root = Path(output_dir) if output_dir else repo_root / DEFAULT_CONTEXT_ROOT
    context_root.mkdir(parents=True, exist_ok=True)

    exports_by_inode: dict[str, list[str]] = {}
    for entry in index["files"].values():
        inode_id = entry["inode_id"]
        if inode_id in exports_by_inode:
            continue
        inode_path = base / f"{entry['content_hash']}.json"
        if not inode_path.is_file():
            raise ContextWalkError(f"inode file missing for {inode_id}: {inode_path}")
        with inode_path.open(encoding="utf-8") as handle:
            inode_doc = json.load(handle)
        exports_by_inode[inode_id] = list(inode_doc.get("exports") or [])

    # route segment prefix -> {inode_ids: set(), children: set(), file_count: int}
    nodes: dict[str, dict[str, Any]] = {}
    for rel_path, entry in sorted(index["files"].items()):
        parts = Path(rel_path).parent.parts
        if not parts:
            continue
        for depth in range(1, len(parts) + 1):
            route = "/".join(parts[:depth])
            node = nodes.setdefault(route, {"inode_ids": set(), "children": set(), "file_count": 0})
            node["inode_ids"].add(entry["inode_id"])
            node["file_count"] += 1
            if depth < len(parts):
                node["children"].add(parts[depth])

    written: list[str] = []
    for route in sorted(nodes):
        node = nodes[route]
        inode_refs = sorted(node["inode_ids"])
        export_names = sorted(
            {name for inode_id in inode_refs for name in exports_by_inode.get(inode_id, [])}
        )
        doc = {
            "node_id": node_id_for(route),
            "route": route,
            "kind": "domain" if "/" not in route else "module",
            "file_count": node["file_count"],
            "summary": _summarize(export_names, node["file_count"]),
            "children": sorted(node["children"]),
            "inode_refs": inode_refs,
        }
        node_dir = context_root / route
        node_dir.mkdir(parents=True, exist_ok=True)
        node_path = node_dir / NODE_FILENAME
        with node_path.open("w", encoding="utf-8") as handle:
            json.dump(doc, handle, indent=2, sort_keys=True)
            handle.write("\n")
        written.append(str(node_path))

    return {
        "context_root": str(context_root),
        "node_count": len(nodes),
        "nodes": sorted(nodes),
        "written": written,
    }


def walk_route(
    repo_root: Path,
    route: str,
    *,
    context_root: Path | None = None,
) -> dict[str, Any]:
    """Resolve a context route segment-by-segment (sequential, like a path walk).

    Stops at the first segment that has no node — ``resolved`` is then false
    and ``failed_segment`` names the missing segment, mirroring ENOENT.
    """
    repo_root = Path(repo_root)
    base = Path(context_root) if context_root else repo_root / DEFAULT_CONTEXT_ROOT
    segments = [segment for segment in route.strip("/").split("/") if segment]
    if not segments:
        raise ContextWalkError("route must contain at least one segment")

    steps: list[dict[str, Any]] = []
    resolved = True
    failed_segment = ""
    terminal_node: dict[str, Any] | None = None
    current = base
    for segment in segments:
        node_path = current / segment / NODE_FILENAME
        if not node_path.is_file():
            resolved = False
            failed_segment = segment
            steps.append({"segment": segment, "found": False})
            break
        with node_path.open(encoding="utf-8") as handle:
            terminal_node = json.load(handle)
        steps.append(
            {
                "segment": segment,
                "found": True,
                "node_id": terminal_node.get("node_id", ""),
                "summary": terminal_node.get("summary", ""),
            }
        )
        current = current / segment

    result: dict[str, Any] = {
        "route": route,
        "resolved": resolved,
        "steps": steps,
        "inode_refs": list(terminal_node.get("inode_refs") or []) if resolved and terminal_node else [],
    }
    if not resolved:
        result["failed_segment"] = failed_segment
    validate_document(result, "context-route.schema.json")
    return result
