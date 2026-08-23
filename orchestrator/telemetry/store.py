"""Telemetry store paths and JSON persistence for ExecutionRun / Experience."""

from __future__ import annotations

import json
import re
from pathlib import Path

from orchestrator.schemas.validate import ValidationError, validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


class TelemetryStoreError(ValueError):
    """Raised when telemetry paths or payloads are invalid."""


def _assert_safe_id(value: str, label: str) -> None:
    if not value or not _SAFE_ID.match(value):
        raise TelemetryStoreError(f"invalid {label}: {value!r}")
    if ".." in value:
        raise TelemetryStoreError(f"path traversal rejected in {label}: {value!r}")


def runs_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "runs"


def experience_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "experience"


def ensure_store_layout(repo_root: Path) -> None:
    """Create .agent/runs and .agent/experience directories."""
    runs_dir(repo_root).mkdir(parents=True, exist_ok=True)
    experience_dir(repo_root).mkdir(parents=True, exist_ok=True)


def write_execution_run(repo_root: Path, run: dict) -> Path:
    validate_document(run, "execution-run.schema.json")
    run_id = run["run_id"]
    _assert_safe_id(run_id, "run_id")
    ensure_store_layout(repo_root)
    path = runs_dir(repo_root) / f"{run_id}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(run, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def load_execution_run(repo_root: Path, run_id: str) -> dict:
    _assert_safe_id(run_id, "run_id")
    path = runs_dir(repo_root) / f"{run_id}.json"
    if not path.is_file():
        raise TelemetryStoreError(f"execution run not found: {path}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "execution-run.schema.json")
    return doc


def write_experience(repo_root: Path, experience: dict) -> Path:
    validate_document(experience, "experience.schema.json")
    experience_id = experience["experience_id"]
    _assert_safe_id(experience_id, "experience_id")
    ensure_store_layout(repo_root)
    path = experience_dir(repo_root) / f"{experience_id}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(experience, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def load_experience(repo_root: Path, experience_id: str) -> dict:
    _assert_safe_id(experience_id, "experience_id")
    path = experience_dir(repo_root) / f"{experience_id}.json"
    if not path.is_file():
        raise TelemetryStoreError(f"experience not found: {path}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "experience.schema.json")
    return doc


def list_experiences(repo_root: Path) -> list[dict]:
    directory = experience_dir(repo_root)
    if not directory.is_dir():
        return []
    results: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            doc = json.load(handle)
        try:
            validate_document(doc, "experience.schema.json")
        except ValidationError:
            continue
        results.append(doc)
    return results
