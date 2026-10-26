"""N5 feedback service — N4 deltas → proposal-only Skill-fit / routing."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.feedback.n5.enabled import require_n5_gate
from orchestrator.feedback.n5.suggest import (
    MIN_DELTA,
    build_skill_fit_suggestions,
    skill_confidence_deltas_from_suggestions,
)
from orchestrator.matcher.score import get_weights
from orchestrator.routing.propose import write_routing_proposal
from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA = "n5-feedback-report.schema.json"
SCHEMA_VERSION = "1"
PLAN_ID = "n5-skill-routing-feedback"
DEFAULT_N4_REL = Path(".agent/evidence/n4-cross-stack-benchmark/LATEST_hermetic.json")


class N5ServiceError(ValueError):
    """Operator-facing N5 errors."""


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _version(repo_root: Path) -> str:
    path = Path(repo_root) / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _git_sha(repo_root: Path) -> str:
    head = Path(repo_root) / ".git" / "HEAD"
    if not head.is_file():
        return ""
    try:
        raw = head.read_text(encoding="utf-8").strip()
        if raw.startswith("ref:"):
            ref = raw.split(" ", 1)[1].strip()
            ref_path = Path(repo_root) / ".git" / ref
            if ref_path.is_file():
                return ref_path.read_text(encoding="utf-8").strip()[:40]
        return raw[:40]
    except OSError:
        return ""


def _feedback_id() -> str:
    digest = hashlib.sha256(
        f"n5|{_utc_now()}|{uuid4().hex}".encode()
    ).hexdigest()[:12]
    return f"n5-feedback-{digest}"


def _evidence_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "n5-skill-routing-feedback"


def resolve_n4_report_path(repo_root: Path, n4_report: Path | None) -> Path:
    repo_root = Path(repo_root).resolve()
    if n4_report is None:
        return (repo_root / DEFAULT_N4_REL).resolve()
    path = Path(n4_report)
    if not path.is_absolute():
        path = (repo_root / path).resolve()
    else:
        path = path.resolve()
    # Path allowlist: must live under repo_root
    try:
        path.relative_to(repo_root)
    except ValueError as exc:
        raise N5ServiceError(
            f"N4 report path must be under repo root: {path}"
        ) from exc
    return path


def load_n4_report(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise N5ServiceError(f"N4 report not found: {path}")
    try:
        with path.open(encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise N5ServiceError(f"invalid N4 report JSON: {path}: {exc}") from exc
    if not isinstance(doc, dict):
        raise N5ServiceError("N4 report must be a JSON object")
    try:
        validate_document(doc, "n4-benchmark-report.schema.json")
    except ValidationError as exc:
        raise N5ServiceError(f"N4 report failed schema validation: {exc}") from exc
    if doc.get("plan_id") != "n4-cross-stack-benchmark":
        raise N5ServiceError("N4 report plan_id mismatch")
    return doc


def _build_routing_proposal(
    feedback_id: str,
    n4: dict[str, Any],
    suggestions: list[dict[str, Any]],
) -> dict[str, Any]:
    deltas = skill_confidence_deltas_from_suggestions(suggestions)
    report_id = str(n4.get("report_id") or "")
    return {
        "proposal_id": f"n5-route-{feedback_id.replace('n5-feedback-', '')}",
        "kind": "routing-proposal",
        "based_on_experiences": [f"n4-report:{report_id}"] if report_id else [],
        "skill_confidence_deltas": deltas,
        "decomposition_hints": [],
        "matcher_weight_suggestions": dict(get_weights()),
        "auto_apply": False,
        "captain_approved": False,
        "notes": (
            "N5 Skill-fit / routing feedback from N4 deltas. "
            "Proposal-only; do not apply until Captain sets "
            "captain_approved=true and runs apply-routing-proposal.sh."
        ),
        "created_at": _utc_now(),
        "captain_approval_required": True,
        "source_plan_id": PLAN_ID,
        "source_n4_report_id": report_id,
    }


def run_n5_feedback(
    repo_root: Path,
    *,
    n4_report: Path | None = None,
    write_proposals: bool = True,
    persist: bool = True,
) -> dict[str, Any]:
    require_n5_gate()
    repo_root = Path(repo_root).resolve()
    n4_path = resolve_n4_report_path(repo_root, n4_report)
    n4 = load_n4_report(n4_path)

    suggestions = build_skill_fit_suggestions(n4)
    actionable = [
        s for s in suggestions if s.get("action") in {"boost", "dampen"}
    ]
    feedback_id = _feedback_id()
    routing_proposal: dict[str, Any] | None = None
    proposal_path: str | None = None

    if actionable:
        routing_proposal = _build_routing_proposal(feedback_id, n4, suggestions)
        if write_proposals:
            path = write_routing_proposal(repo_root, routing_proposal)
            proposal_path = str(path)

    n4_deltas = n4.get("deltas") or {}
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "feedback_id": feedback_id,
        "created_at": _utc_now(),
        "plan_id": PLAN_ID,
        "northstar_version": _version(repo_root),
        "repository_sha": _git_sha(repo_root),
        "n4_report_id": str(n4.get("report_id") or ""),
        "n4_report_path": str(n4_path),
        "n4_seed": int(n4.get("seed") or 0),
        "n4_mode": str(n4.get("mode") or ""),
        "n4_deltas": {
            "accept_rate": float(n4_deltas.get("accept_rate") or 0.0),
            "skill_reuse_rate": float(n4_deltas.get("skill_reuse_rate") or 0.0),
            "retrieval_precision": float(n4_deltas.get("retrieval_precision") or 0.0),
            "primary_efficiency": float(n4_deltas.get("primary_efficiency") or 0.0),
        },
        "min_delta_threshold": MIN_DELTA,
        "skill_fit_suggestions": suggestions,
        "routing_proposal_id": (
            None if routing_proposal is None else routing_proposal["proposal_id"]
        ),
        "routing_proposal_path": proposal_path,
        "validation_summary": {
            "actionable_suggestions": len(actionable),
            "proposal_written": bool(proposal_path),
            "proposal_applied": False,
            "n4_security_regression": bool(n4.get("security_regression")),
        },
        "notes": (
            "N5 Skill-fit / routing feedback. Proposal-only. "
            "Does not apply matcher weights, promote policies, "
            "or authorize Level 3 GPU spend."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_applied": False,
        "policy_promoted": False,
        "weights_applied": False,
    }

    validate_document(packet, SCHEMA)

    if persist:
        out_dir = _evidence_dir(repo_root)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{feedback_id}.json"
        with out_path.open("w", encoding="utf-8") as handle:
            json.dump(packet, handle, indent=2, sort_keys=True)
            handle.write("\n")
        latest = out_dir / "LATEST.json"
        with latest.open("w", encoding="utf-8") as handle:
            json.dump(packet, handle, indent=2, sort_keys=True)
            handle.write("\n")
        packet = dict(packet)
        packet["evidence_path"] = str(out_path)

    return packet
