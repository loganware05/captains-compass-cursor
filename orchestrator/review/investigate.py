"""Assemble an investigation context pack for the code review pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.integrations.events import redact_secrets

# Cap per-file content to keep packs small and hermetic.
_MAX_FILE_BYTES = 16_384
_MAX_DIFF_CHARS = 200_000
_MAX_NEIGHBORS = 12


def _safe_rel(repo_root: Path, path: Path) -> str | None:
    try:
        rel = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return None
    return rel.as_posix()


def _read_capped(path: Path) -> str:
    data = path.read_bytes()[:_MAX_FILE_BYTES]
    return data.decode("utf-8", errors="replace")


def related_paths(repo_root: Path, changed_paths: list[str]) -> list[str]:
    related: list[str] = []
    seen = set(changed_paths)
    for rel in changed_paths:
        parent = (repo_root / rel).resolve().parent
        if not parent.is_dir():
            continue
        try:
            parent.relative_to(repo_root.resolve())
        except ValueError:
            continue
        for child in sorted(parent.iterdir()):
            if not child.is_file():
                continue
            rel_child = _safe_rel(repo_root, child)
            if not rel_child or rel_child in seen:
                continue
            seen.add(rel_child)
            related.append(rel_child)
            if len(related) >= _MAX_NEIGHBORS:
                return related
    return related


def investigate(
    *,
    repo_root: Path,
    detection: dict[str, Any],
    diff_text: str = "",
) -> dict[str, Any]:
    root = repo_root.resolve()
    file_snippets: dict[str, str] = {}
    for rel in detection.get("changed_paths") or []:
        path = (root / rel).resolve()
        if not path.is_file():
            continue
        if _safe_rel(root, path) is None:
            continue
        file_snippets[rel] = _read_capped(path)

    neighbors = related_paths(root, list(detection.get("changed_paths") or []))
    neighbor_snippets: dict[str, str] = {}
    for rel in neighbors:
        path = (root / rel).resolve()
        if path.is_file() and _safe_rel(root, path) is not None:
            neighbor_snippets[rel] = _read_capped(path)

    diff_capped = diff_text[:_MAX_DIFF_CHARS]
    pack = {
        "repository": str(root),
        "domains": list(detection.get("domains") or []),
        "changed_paths": list(detection.get("changed_paths") or []),
        "related_paths": neighbors,
        "skills_suggested": list(detection.get("skills_suggested") or []),
        "intent": detection.get("intent") or {},
        "diff": diff_capped,
        "file_snippets": file_snippets,
        "related_snippets": neighbor_snippets,
    }
    return redact_secrets(pack)
