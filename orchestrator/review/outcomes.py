"""Record Code Reviewer finding triage outcomes into Experience (M31).

Outcomes never originate Captain approval. RoutingProposal emission is optional
and always proposal-only (auto_apply=false).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.integrations.events import redact_secrets
from orchestrator.routing.propose import build_routing_proposal, write_routing_proposal
from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.telemetry.store import write_experience

SCHEMA_VERSION = "northstar.finding_outcome.v1"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
# Free-text notes may embed secrets; scrub common patterns before durable writes.
_SECRET_TEXT = re.compile(
    r"(?i)("
    r"ghp_[A-Za-z0-9_]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
    r"|gho_[A-Za-z0-9_]{20,}"
    r"|sk-[A-Za-z0-9_-]{20,}"
    r"|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|Bearer\s+[A-Za-z0-9._~+/=-]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    r"|(?:password|passwd|secret|api[_-]?key|access[_-]?key)\s*[:=]\s*\S+"
    r")"
)

_DECISIONS = frozenset({"accepted", "rejected", "deferred"})
_LABELS = frozenset({"tp", "fp", "unknown"})
_SOURCE_INSTANCES = frozenset({"control-test", "product-import", "control-live"})


class OutcomeError(ValueError):
    """Raised when finding outcomes cannot be recorded safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_id(value: str, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise OutcomeError(f"unsafe {label}: {value!r}")
    return value


def _redact_secret_text(value: Any) -> Any:
    """Redact secret-shaped substrings in notes/lessons (beyond key-based redact_secrets)."""
    if isinstance(value, str):
        return _SECRET_TEXT.sub("[REDACTED]", value)
    if isinstance(value, dict):
        return {k: _redact_secret_text(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_secret_text(v) for v in value]
    return value


def infer_source_instance(repo_root: Path) -> str:
    """Map repo_root to Experience source_instance without claiming Captain approval."""
    root = Path(repo_root).resolve()
    if (root / "orchestrator" / "schemas" / "finding-outcome.schema.json").is_file():
        return "control-live"
    if (root / ".agent").is_dir():
        return "product-import"
    return "control-test"

def load_review_report(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise OutcomeError(f"review report not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OutcomeError(f"invalid review report JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise OutcomeError("review report must be an object")
    try:
        validate_document(data, "code-review-report.schema.json")
    except ValidationError as exc:
        raise OutcomeError(str(exc)) from exc
    return data


def load_triage_input(path: Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.is_file():
        raise OutcomeError(f"triage file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OutcomeError(f"invalid triage JSON: {exc}") from exc
    if isinstance(data, dict) and isinstance(data.get("outcomes"), list):
        rows = data["outcomes"]
    elif isinstance(data, list):
        rows = data
    else:
        raise OutcomeError("triage JSON must be a list or {\"outcomes\": [...]}")
    if not rows:
        raise OutcomeError("triage input is empty")
    dict_rows = [row for row in rows if isinstance(row, dict)]
    if not dict_rows:
        raise OutcomeError("triage input has no outcome objects")
    return dict_rows


def _default_label(decision: str, label: str | None) -> str:
    if label in _LABELS:
        return str(label)
    if decision == "accepted":
        return "tp"
    if decision == "rejected":
        return "fp"
    return "unknown"


def normalize_outcome(
    raw: dict[str, Any],
    *,
    report: dict[str, Any],
    report_path: str = "",
) -> dict[str, Any]:
    findings = {str(f.get("id")): f for f in (report.get("findings") or []) if isinstance(f, dict)}
    finding_id = str(raw.get("finding_id") or "").strip()
    if not finding_id:
        raise OutcomeError("finding_id is required")
    finding = findings.get(finding_id)
    if finding is None:
        raise OutcomeError(f"finding_id not in report: {finding_id!r}")

    decision = str(raw.get("decision") or "").strip().lower()
    if decision not in _DECISIONS:
        raise OutcomeError(f"invalid decision for {finding_id}: {decision!r}")

    skill = str(raw.get("skill") or finding.get("skill") or "code-reviewer").strip()
    label = _default_label(decision, raw.get("label"))
    notes = _redact_secret_text(str(raw.get("notes") or ""))
    run_id = str(report.get("run_id") or "")
    _safe_id(run_id, "run_id")
    _safe_id(finding_id, "finding_id")

    pack = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "finding_id": finding_id,
        "decision": decision,
        "label": label,
        "skill": skill,
        "notes": notes,
        "title": str(raw.get("title") or finding.get("title") or ""),
        "severity": str(raw.get("severity") or finding.get("severity") or ""),
        "report_path": report_path,
        "created_at": _utc_now(),
        "captain_approval": False,
    }
    try:
        validate_document(pack, "finding-outcome.schema.json")
    except ValidationError as exc:
        raise OutcomeError(str(exc)) from exc
    return _redact_secret_text(pack)


def outcome_to_experience(
    outcome: dict[str, Any],
    *,
    plan_id: str = "",
    source_instance: str = "control-test",
) -> dict[str, Any]:
    decision = outcome["decision"]
    label = outcome["label"]
    if decision == "accepted":
        exp_outcome = "success"
    elif decision == "rejected":
        exp_outcome = "failed"
    else:
        exp_outcome = "partial"

    if source_instance not in _SOURCE_INSTANCES:
        raise OutcomeError(f"invalid source_instance: {source_instance!r}")

    lesson = (
        f"Code review finding `{outcome['finding_id']}` "
        f"decision={decision} label={label}."
    )
    if outcome.get("title"):
        lesson += f" Title: {outcome['title']}."
    if outcome.get("notes"):
        lesson += f" Notes: {outcome['notes']}"

    experience = {
        "experience_id": f"exp-cr-{outcome['run_id']}-{outcome['finding_id']}"[:120],
        "plan_id": plan_id or f"code-review:{outcome['run_id']}",
        "run_id": outcome["run_id"],
        "objective": (
            f"Triage Code Reviewer finding {outcome['finding_id']} "
            f"from run {outcome['run_id']}"
        ),
        "outcome": exp_outcome,
        "source_instance": source_instance,
        "skills_used": [outcome["skill"]],
        "capabilities_exercised": ["code-review", "finding-triage"],
        "lessons": [lesson],
        "provenance": {
            "code_review_run_id": outcome["run_id"],
            "finding_id": outcome["finding_id"],
            "decision": decision,
            "label": label,
            "report_path": outcome.get("report_path") or "",
        },
        "created_at": outcome.get("created_at") or _utc_now(),
    }
    return _redact_secret_text(redact_secrets(experience))


def write_outcomes_evidence(
    repo_root: Path,
    run_id: str,
    outcomes: list[dict[str, Any]],
) -> Path:
    _safe_id(run_id, "run_id")
    out_dir = Path(repo_root) / ".agent" / "evidence" / "code-review" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "outcomes.json"
    payload = _redact_secret_text(
        redact_secrets(
            {
                "schema_version": "northstar.finding_outcomes_bundle.v1",
                "run_id": run_id,
                "created_at": _utc_now(),
                "outcomes": outcomes,
                "captain_approval": False,
            }
        )
    )
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def record_finding_outcomes(
    *,
    repo_root: Path,
    report_path: Path,
    triage_path: Path,
    plan_id: str = "",
    emit_routing_proposal: bool = False,
    proposal_notes: str = "",
    source_instance: str | None = None,
) -> dict[str, Any]:
    """Validate triage against a review report; write outcomes + Experience (+ optional proposal)."""
    root = Path(repo_root).resolve()
    report = load_review_report(report_path)
    run_id = str(report.get("run_id") or "")
    _safe_id(run_id, "run_id")
    resolved_source = source_instance or infer_source_instance(root)
    if resolved_source not in _SOURCE_INSTANCES:
        raise OutcomeError(f"invalid source_instance: {resolved_source!r}")

    raw_rows = load_triage_input(triage_path)
    outcomes: list[dict[str, Any]] = []
    for row in raw_rows:
        outcomes.append(
            normalize_outcome(
                row,
                report=report,
                report_path=str(Path(report_path)),
            )
        )

    outcomes_path = write_outcomes_evidence(root, run_id, outcomes)

    experience_paths: list[str] = []
    experiences: list[dict[str, Any]] = []
    for outcome in outcomes:
        if outcome["decision"] == "deferred":
            # Deferred findings are recorded in outcomes evidence only.
            continue
        experience = outcome_to_experience(
            outcome,
            plan_id=plan_id,
            source_instance=resolved_source,
        )
        path = write_experience(root, experience)
        experience_paths.append(str(path))
        experiences.append(experience)

    proposal_path = ""
    proposal: dict[str, Any] | None = None
    if emit_routing_proposal:
        if not experiences:
            raise OutcomeError(
                "emit_routing_proposal requires at least one non-deferred outcome"
            )
        notes = _redact_secret_text(
            proposal_notes
            or (
                "M31 proposal from Code Reviewer finding outcomes. "
                "auto_apply=false; Captain must approve before apply."
            )
        )
        proposal = build_routing_proposal(
            experiences,
            proposal_id=f"route-cr-{run_id}-{uuid4().hex[:8]}",
            notes=notes,
        )
        proposal["auto_apply"] = False
        proposal["captain_approved"] = False
        proposal["notes"] = _redact_secret_text(str(proposal.get("notes") or notes))
        proposal_path = str(write_routing_proposal(root, proposal))

    return {
        "run_id": run_id,
        "outcomes_path": str(outcomes_path),
        "outcome_count": len(outcomes),
        "experience_paths": experience_paths,
        "proposal_path": proposal_path,
        "proposal_auto_apply": False if proposal else None,
        "captain_approval": False,
        "source_instance": resolved_source,
    }
