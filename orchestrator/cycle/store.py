"""Persist cycle state under .agent/cycles/ (runtime; gitignored)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


class CycleStoreError(ValueError):
    """Cycle persistence errors."""


def cycles_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "cycles"


def ensure_layout(repo_root: Path) -> None:
    cycles_dir(repo_root).mkdir(parents=True, exist_ok=True)


def _assert_safe_id(value: str) -> str:
    if not _SAFE_ID.match(value or ""):
        raise CycleStoreError(f"invalid execution_id: {value!r}")
    return value


def cycle_path(repo_root: Path, execution_id: str) -> Path:
    return cycles_dir(repo_root) / f"{_assert_safe_id(execution_id)}.json"


def write_cycle(repo_root: Path, state: dict[str, Any]) -> Path:
    validate_document(state, "cycle-state.schema.json")
    ensure_layout(repo_root)
    path = cycle_path(repo_root, str(state["execution_id"]))
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_cycle(repo_root: Path, execution_id: str) -> dict[str, Any]:
    path = cycle_path(repo_root, execution_id)
    if not path.is_file():
        raise CycleStoreError(f"cycle not found: {execution_id}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    validate_document(doc, "cycle-state.schema.json")
    return doc


def list_cycles(repo_root: Path) -> list[dict[str, Any]]:
    root = cycles_dir(repo_root)
    if not root.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            validate_document(doc, "cycle-state.schema.json")
            out.append(doc)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return out
