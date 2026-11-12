"""Experience Evidence Record validate (XRV)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.xrv.gates import require_xrv_eer_enabled

AUTHORITY_LOCKS = (
    "approved_for_execution",
    "authority_mutation",
    "issues_auto_closed",
    "auto_promoted",
)


def _load_schema(repo_root: Path) -> dict[str, Any]:
    path = (
        Path(repo_root)
        / "orchestrator"
        / "schemas"
        / "experience-evidence-record.schema.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _authority_fallback(doc: dict[str, Any]) -> None:
    for key in AUTHORITY_LOCKS:
        if doc.get(key) is not False:
            raise ValueError(f"{key} must be false")
    for key in (
        "schema_version",
        "eer_id",
        "created_at",
        "repository",
        "commit_sha",
        "plan_id",
        "lifecycle_state",
        "skills_selected",
        "test_evidence",
        "verified_outcome",
    ):
        if key not in doc:
            raise ValueError(f"missing required field: {key}")


def validate_eer_document(repo_root: Path, doc: dict[str, Any]) -> dict[str, Any]:
    """Validate an EER dict against schema (or authority fallback)."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        _authority_fallback(doc)
        return {"status": "ok", "validator": "authority-fallback"}
    jsonschema.validate(instance=doc, schema=_load_schema(repo_root))
    return {"status": "ok", "validator": "jsonschema"}


def validate_eer_path(
    repo_root: Path,
    path: Path,
    *,
    require_gate: bool = True,
) -> dict[str, Any]:
    """Load and validate an EER JSON file. Fail-closed unless gate disabled for tests."""
    if require_gate:
        require_xrv_eer_enabled()
    root = Path(repo_root)
    eer_path = Path(path)
    if not eer_path.is_file():
        raise FileNotFoundError(f"EER file not found: {eer_path}")
    doc = json.loads(eer_path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("EER root must be an object")
    result = validate_eer_document(root, doc)
    result["path"] = str(eer_path)
    result["eer_id"] = doc.get("eer_id")
    result["lifecycle_state"] = doc.get("lifecycle_state")
    result["approved_for_execution"] = False
    result["authority_mutation"] = False
    result["issues_auto_closed"] = False
    result["auto_promoted"] = False
    return result
