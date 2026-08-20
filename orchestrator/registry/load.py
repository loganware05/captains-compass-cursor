"""Load compiled capability registry."""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator.registry.compiler import compile_registry


def load_registry(repo_root: Path) -> dict:
    repo_root = Path(repo_root)
    compiled_path = repo_root / ".agent" / "capabilities" / "compiled" / "registry.json"
    if compiled_path.is_file():
        with compiled_path.open(encoding="utf-8") as handle:
            return json.load(handle)
    return compile_registry(repo_root).registry


def registry_skills(registry: dict) -> list[dict]:
    return list(registry.get("skills") or [])
