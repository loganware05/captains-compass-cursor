"""Persist T3 execution runs under .agent/executions/t3/."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,160}$")


class T3StoreError(ValueError):
    """Raised when T3 execution store IO fails."""


def executions_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "executions" / "t3"


def ensure_layout(repo_root: Path) -> None:
    executions_root(repo_root).mkdir(parents=True, exist_ok=True)


def assert_safe_id(value: str, label: str = "execution_id") -> None:
    if not value or not _SAFE_ID.match(value):
        raise T3StoreError(f"unsafe {label}: {value!r}")


def write_execution(repo_root: Path, doc: dict[str, Any]) -> Path:
    validate_document(doc, "t3-execution-run.schema.json")
    exec_id = str(doc["execution_id"])
    assert_safe_id(exec_id)
    ensure_layout(repo_root)
    path = executions_root(repo_root) / f"{exec_id}.json"
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_execution(repo_root: Path, execution_id: str) -> dict[str, Any]:
    assert_safe_id(execution_id)
    path = executions_root(repo_root) / f"{execution_id}.json"
    if not path.is_file():
        raise T3StoreError(f"execution not found: {execution_id}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise T3StoreError(str(exc)) from exc
    validate_document(doc, "t3-execution-run.schema.json")
    return doc


def list_executions(repo_root: Path) -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    out: list[dict[str, Any]] = []
    for path in sorted(executions_root(repo_root).glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            validate_document(doc, "t3-execution-run.schema.json")
            out.append(doc)
        except Exception:
            continue
    return out
