"""Experience Evidence Record validate + reconstruct (XRV).

Proposal/evidence only. Never grants authority. Never auto-closes issues.
"""

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

LIFECYCLE_ORDER = (
    "planned",
    "implemented",
    "merged",
    "tested",
    "deployed",
    "operationally_verified",
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


def _ops_verification_contract(doc: dict[str, Any]) -> None:
    """Semantic checks for operationally_verified beyond JSON Schema."""
    if doc.get("lifecycle_state") != "operationally_verified":
        return
    ops = doc.get("ops_verification")
    if not isinstance(ops, dict):
        raise ValueError(
            "lifecycle_state=operationally_verified requires ops_verification object"
        )
    for key in ("smoke_id", "verified_at", "repository_sha"):
        if not str(ops.get(key) or "").strip():
            raise ValueError(f"ops_verification.{key} is required and non-empty")
    paths = ops.get("evidence_paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("ops_verification.evidence_paths must be a non-empty list")
    if "live_deploy" not in ops or not isinstance(ops["live_deploy"], bool):
        raise ValueError("ops_verification.live_deploy must be a boolean")


def validate_eer_document(repo_root: Path, doc: dict[str, Any]) -> dict[str, Any]:
    """Validate an EER dict against schema (or authority fallback)."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        _authority_fallback(doc)
        _ops_verification_contract(doc)
        return {"status": "ok", "validator": "authority-fallback"}
    jsonschema.validate(instance=doc, schema=_load_schema(repo_root))
    _ops_verification_contract(doc)
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
    if isinstance(doc.get("ops_verification"), dict):
        result["ops_verification"] = {
            "smoke_id": doc["ops_verification"].get("smoke_id"),
            "live_deploy": doc["ops_verification"].get("live_deploy"),
            "verified_at": doc["ops_verification"].get("verified_at"),
        }
    result["approved_for_execution"] = False
    result["authority_mutation"] = False
    result["issues_auto_closed"] = False
    result["auto_promoted"] = False
    return result


def reconstruct_cycle(doc: dict[str, Any]) -> dict[str, Any]:
    """Auditor-facing ordered cycle from an EER document.

    Evidence pointers only — never grants authority.
    """
    if not isinstance(doc, dict):
        raise ValueError("EER root must be an object")
    for key in AUTHORITY_LOCKS:
        if doc.get(key) is not False:
            raise ValueError(f"{key} must be false")
    state = str(doc.get("lifecycle_state") or "")
    if state not in LIFECYCLE_ORDER:
        raise ValueError(f"unknown lifecycle_state: {state!r}")

    stages: list[dict[str, Any]] = [
        {
            "stage": "issue",
            "ref": doc.get("issue"),
            "present": bool(doc.get("issue")),
        },
        {
            "stage": "plan",
            "ref": doc.get("plan_id"),
            "present": bool(doc.get("plan_id")),
        },
        {
            "stage": "implement",
            "branch": doc.get("branch"),
            "commit_sha": doc.get("commit_sha"),
            "present": bool(doc.get("commit_sha")),
        },
        {
            "stage": "validate",
            "refs": list(doc.get("test_evidence") or []),
            "present": bool(doc.get("test_evidence")),
        },
        {
            "stage": "review",
            "refs": list(doc.get("review_refs") or []),
            "present": bool(doc.get("review_refs")),
        },
        {
            "stage": "merge",
            "ref": doc.get("pull_request"),
            "present": bool(doc.get("pull_request"))
            or (
                # Live-local smokes may bind tip SHA before a PR exists.
                state == "operationally_verified"
                and "live-local-smoke" in list(doc.get("permissions") or [])
            ),
        },
    ]

    ops = doc.get("ops_verification") if isinstance(doc.get("ops_verification"), dict) else None
    ops_present = state == "operationally_verified" and ops is not None
    stages.append(
        {
            "stage": "operationally_verified",
            "present": bool(ops_present),
            "ops_verification": (
                {
                    "smoke_id": ops.get("smoke_id"),
                    "verified_at": ops.get("verified_at"),
                    "repository_sha": ops.get("repository_sha"),
                    "evidence_paths": list(ops.get("evidence_paths") or []),
                    "live_deploy": ops.get("live_deploy"),
                }
                if ops
                else None
            ),
        }
    )

    required_keys = {"plan", "implement", "validate", "merge"}
    if state == "operationally_verified":
        required_keys.add("operationally_verified")
    required_present = all(
        s["present"] for s in stages if s["stage"] in required_keys
    )

    return {
        "eer_id": doc.get("eer_id"),
        "plan_id": doc.get("plan_id"),
        "lifecycle_state": state,
        "lifecycle_rank": LIFECYCLE_ORDER.index(state),
        "stages": stages,
        "cycle_complete_for_state": required_present,
        "ops_verified": state == "operationally_verified" and bool(ops_present),
        "approved_for_execution": False,
        "authority_mutation": False,
        "issues_auto_closed": False,
        "auto_promoted": False,
    }


def reconstruct_eer_path(
    repo_root: Path,
    path: Path,
    *,
    require_gate: bool = True,
) -> dict[str, Any]:
    """Validate then reconstruct — gated by COMPASS_XRV_EER_ENABLED."""
    if require_gate:
        require_xrv_eer_enabled()
    root = Path(repo_root)
    eer_path = Path(path)
    if not eer_path.is_file():
        raise FileNotFoundError(f"EER file not found: {eer_path}")
    doc = json.loads(eer_path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("EER root must be an object")
    validate_eer_document(root, doc)
    result = reconstruct_cycle(doc)
    result["path"] = str(eer_path)
    result["status"] = "ok"
    return result
