"""Module dependency graph with hard/symlinked edges (M40 Task 2).

Built from the inode store's import metadata. An edge from module A to module
B is:

- **hard** when A names B's exported symbols in its import — A depends on B's
  contract (interface/signature), so the two are version-locked. The shared
  symbol names are recorded as the edge's ``contract``.
- **symlink** when the import is a bare path / side-effect reference — loose
  coupling through indirection.

Edges crossing a context route boundary (different ``domain/module``) are
flagged ``cross_boundary`` — those are the edges the review gate checks.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from orchestrator.context.inodes import load_index, module_route_for

GRAPH_VERSION = "1.0.0"
_RESOLVE_SUFFIXES = (".ts", ".tsx", ".py", ".mts", ".cts")
_RESOLVE_INDEX_FILES = ("index.ts", "index.tsx", "__init__.py")


class DependencyGraphError(ValueError):
    """Raised when the dependency graph cannot be built."""


def _resolve_relative(importer: str, module: str) -> str:
    base = PurePosixPath(importer).parent
    parts: list[str] = []
    for part in (base / module).parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part not in (".", ""):
            parts.append(part)
    return "/".join(parts)


def _resolve_python_relative(importer: str, module: str) -> str:
    level = len(module) - len(module.lstrip("."))
    remainder = module.lstrip(".").replace(".", "/")
    base = list(PurePosixPath(importer).parent.parts)
    for _ in range(max(level - 1, 0)):
        if base:
            base.pop()
    return "/".join(base + ([remainder] if remainder else []))


def resolve_import(importer: str, module: str, indexed_paths: set[str]) -> str | None:
    """Resolve an import module string to an indexed repo-relative path."""
    if module.startswith("./") or module.startswith("../"):
        target = _resolve_relative(importer, module)
    elif module.startswith(".") and not module.startswith("./"):
        target = _resolve_python_relative(importer, module)
    elif importer.endswith(".py"):
        target = module.replace(".", "/")
    else:
        return None

    candidates = [target + suffix for suffix in _RESOLVE_SUFFIXES]
    candidates += [f"{target}/{name}" for name in _RESOLVE_INDEX_FILES]
    candidates.append(target)
    for candidate in candidates:
        if candidate in indexed_paths:
            return candidate
    return None


def build_dependency_graph(
    repo_root: Path,
    *,
    store_dir: Path | None = None,
) -> dict[str, Any]:
    """Build the hard/symlink module dependency graph from the inode store."""
    repo_root = Path(repo_root)
    index = load_index(repo_root, store_dir=store_dir)
    base = Path(store_dir) if store_dir else repo_root / ".agent" / "inodes"

    inodes: dict[str, dict[str, Any]] = {}
    path_by_inode: dict[str, str] = {}
    for rel_path, entry in sorted(index["files"].items()):
        inode_path = base / f"{entry['content_hash']}.json"
        if not inode_path.is_file():
            raise DependencyGraphError(f"inode file missing: {inode_path}")
        with inode_path.open(encoding="utf-8") as handle:
            inodes[rel_path] = json.load(handle)
        path_by_inode[entry["inode_id"]] = rel_path

    indexed_paths = set(inodes)
    edges: list[dict[str, Any]] = []
    for rel_path, inode in sorted(inodes.items()):
        importer_route = module_route_for(rel_path)
        target_exports = {
            path: set(doc.get("exports") or []) for path, doc in inodes.items()
        }
        for imp in inode.get("imports") or []:
            module = imp.get("module") or ""
            target = resolve_import(rel_path, module, indexed_paths)
            if target is None or target == rel_path:
                continue
            names = [name for name in (imp.get("names") or []) if name]
            shared = sorted(set(names) & target_exports.get(target, set()))
            edge: dict[str, Any] = {
                "from": rel_path,
                "to": target,
                "link": "hard" if shared else "symlink",
                "cross_boundary": module_route_for(target) != importer_route,
            }
            if shared:
                edge["contract"] = shared
            if names:
                edge["names"] = sorted(names)
            edges.append(edge)

    edges.sort(key=lambda edge: (edge["from"], edge["to"], edge["link"]))
    stats = {
        "node_count": len(inodes),
        "edge_count": len(edges),
        "hard": sum(1 for edge in edges if edge["link"] == "hard"),
        "symlink": sum(1 for edge in edges if edge["link"] == "symlink"),
        "cross_boundary": sum(1 for edge in edges if edge["cross_boundary"]),
    }
    return {
        "version": GRAPH_VERSION,
        "nodes": sorted(inodes),
        "edges": edges,
        "stats": stats,
    }


def write_dependency_graph(
    repo_root: Path,
    *,
    store_dir: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    graph = build_dependency_graph(repo_root, store_dir=store_dir)
    out = Path(output_path) if output_path else Path(repo_root) / ".agent" / "plans" / "dependency-graph.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(graph, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return graph
