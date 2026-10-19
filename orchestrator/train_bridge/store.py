"""Persist training-export manifests under .agent/training-exports/."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


class TrainBridgeStoreError(ValueError):
    """Training export persistence errors."""


def exports_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "training-exports"


def ensure_layout(repo_root: Path) -> None:
    exports_dir(repo_root).mkdir(parents=True, exist_ok=True)


def _assert_safe_id(value: str) -> str:
    if not _SAFE_ID.match(value or ""):
        raise TrainBridgeStoreError(f"invalid export_id: {value!r}")
    return value


def export_path(repo_root: Path, export_id: str) -> Path:
    return exports_dir(repo_root) / f"{_assert_safe_id(export_id)}.json"


def write_export(repo_root: Path, manifest: dict[str, Any]) -> Path:
    validate_document(manifest, "training-export-manifest.schema.json")
    ensure_layout(repo_root)
    path = export_path(repo_root, str(manifest["export_id"]))
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_export(repo_root: Path, export_id: str) -> dict[str, Any]:
    path = export_path(repo_root, export_id)
    if not path.is_file():
        raise TrainBridgeStoreError(f"export not found: {export_id}")
    return load_export_file(path)


def load_export_file(path: Path) -> dict[str, Any]:
    target = Path(path)
    if not target.is_file():
        raise TrainBridgeStoreError(f"export file not found: {target}")
    doc = json.loads(target.read_text(encoding="utf-8"))
    validate_document(doc, "training-export-manifest.schema.json")
    return doc
