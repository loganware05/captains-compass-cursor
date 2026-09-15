"""Aggregate Code Reviewer finding outcomes into a precision ledger (M33 / B5).

Precision dashboards are evidence-only. Optional invocation-priority proposals are
always proposal-only (auto_apply=false). Never originates Captain approval.
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

SCHEMA_VERSION = "northstar.precision_ledger.v1"
DEFAULT_MIN_SAMPLE = 5
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
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
_SOURCE_INSTANCES = frozenset({"control-test", "product-import", "control-live"})


class PrecisionError(ValueError):
    """Raised when a precision ledger cannot be built safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_id(value: str, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise PrecisionError(f"unsafe {label}: {value!r}")
    return value


def _redact_secret_text(value: Any) -> Any:
    if isinstance(value, str):
        return _SECRET_TEXT.sub("[REDACTED]", value)
    if isinstance(value, dict):
        return {k: _redact_secret_text(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_secret_text(v) for v in value]
    return value


def infer_source_instance(repo_root: Path) -> str:
    root = Path(repo_root).resolve()
    if (root / "orchestrator" / "schemas" / "precision-ledger.schema.json").is_file():
        return "control-live"
    if (root / ".agent").is_dir():
        return "product-import"
    return "control-test"


def _infer_key_kind(skill: str) -> str:
    """Best-effort classification; B5 treats all outcome skills as skill keys."""
    lowered = skill.lower()
    if "heuristic" in lowered:
        return "heuristic"
    if lowered in {"security-review", "adversarial-reviewer", "accessibility-review", "test-engineer"}:
        return "specialist"
    return "skill"


def load_outcomes_bundle(path: Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.is_file():
        raise PrecisionError(f"outcomes file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PrecisionError(f"invalid outcomes JSON: {exc}") from exc

    if isinstance(data, dict) and isinstance(data.get("outcomes"), list):
        rows = data["outcomes"]
    elif isinstance(data, list):
        rows = data
    else:
        raise PrecisionError("outcomes JSON must be a list or {\"outcomes\": [...]}")

    dict_rows = [row for row in rows if isinstance(row, dict)]
    if not dict_rows:
        raise PrecisionError("outcomes input is empty")
    return dict_rows


def collect_outcome_paths(*, outcomes: Path | None = None, outcomes_dir: Path | None = None) -> list[Path]:
    paths: list[Path] = []
    if outcomes is not None:
        paths.append(Path(outcomes))
    if outcomes_dir is not None:
        root = Path(outcomes_dir)
        if not root.is_dir():
            raise PrecisionError(f"outcomes dir not found: {root}")
        paths.extend(sorted(root.rglob("outcomes.json")))
    # De-dupe while preserving order
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    if not unique:
        raise PrecisionError("provide --outcomes and/or --outcomes-dir with at least one file")
    return unique


def aggregate_entries(outcome_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for row in outcome_rows:
        skill = str(row.get("skill") or "").strip()
        if not skill:
            raise PrecisionError(
                f"unknown skill key for finding {row.get('finding_id')!r}: empty skill"
            )
        _safe_id(skill, "skill")
        decision = str(row.get("decision") or "").strip().lower()
        if decision not in _DECISIONS:
            raise PrecisionError(f"invalid decision for {row.get('finding_id')!r}: {decision!r}")

        bucket = buckets.setdefault(
            skill,
            {
                "key": skill,
                "key_kind": _infer_key_kind(skill),
                "accepted": 0,
                "rejected": 0,
                "deferred": 0,
                "decided": 0,
                "precision": None,
                "source_run_ids": [],
                "finding_ids": [],
            },
        )
        bucket[decision] = int(bucket[decision]) + 1
        finding_id = str(row.get("finding_id") or "").strip()
        if finding_id and finding_id not in bucket["finding_ids"]:
            bucket["finding_ids"].append(finding_id)
        run_id = str(row.get("run_id") or "").strip()
        if run_id and run_id not in bucket["source_run_ids"]:
            bucket["source_run_ids"].append(run_id)

    entries: list[dict[str, Any]] = []
    for skill in sorted(buckets):
        bucket = buckets[skill]
        decided = int(bucket["accepted"]) + int(bucket["rejected"])
        bucket["decided"] = decided
        if decided == 0:
            bucket["precision"] = None
        else:
            bucket["precision"] = round(int(bucket["accepted"]) / decided, 4)
        bucket["source_run_ids"] = sorted(bucket["source_run_ids"])
        bucket["finding_ids"] = sorted(bucket["finding_ids"])
        entries.append(bucket)
    return entries


def build_precision_ledger(
    outcome_rows: list[dict[str, Any]],
    *,
    ledger_id: str | None = None,
    plan_id: str = "b5-precision-ledger",
    source_outcome_paths: list[str] | None = None,
    min_sample_for_proposal: int = DEFAULT_MIN_SAMPLE,
) -> dict[str, Any]:
    if not outcome_rows:
        raise PrecisionError("cannot aggregate empty outcomes")
    if min_sample_for_proposal < 1:
        raise PrecisionError("min_sample_for_proposal must be >= 1")

    lid = _safe_id(ledger_id or f"precision-{uuid4().hex[:12]}", "ledger_id")
    entries = aggregate_entries(outcome_rows)
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "ledger_id": lid,
        "created_at": _utc_now(),
        "plan_id": plan_id or "b5-precision-ledger",
        "source_outcome_paths": list(source_outcome_paths or []),
        "min_sample_for_proposal": int(min_sample_for_proposal),
        "entries": entries,
        "captain_approval": False,
        "locks": {
            "auto_apply": False,
            "captain_approved": False,
        },
    }
    try:
        validate_document(ledger, "precision-ledger.schema.json")
    except ValidationError as exc:
        raise PrecisionError(str(exc)) from exc
    return _redact_secret_text(redact_secrets(ledger))


def render_dashboard_markdown(ledger: dict[str, Any]) -> str:
    lines = [
        f"# Precision dashboard — `{ledger['ledger_id']}`",
        "",
        f"Created: {ledger['created_at']}",
        f"Plan: `{ledger.get('plan_id') or ''}`",
        f"Min sample for proposal: {ledger['min_sample_for_proposal']}",
        "",
        "| Skill / specialist | Kind | Accepted | Rejected | Deferred | Decided | Precision |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for entry in ledger.get("entries") or []:
        precision = entry.get("precision")
        precision_s = "—" if precision is None else f"{float(precision):.1%}"
        lines.append(
            "| {key} | {kind} | {acc} | {rej} | {def_} | {dec} | {prec} |".format(
                key=entry["key"],
                kind=entry["key_kind"],
                acc=entry["accepted"],
                rej=entry["rejected"],
                def_=entry["deferred"],
                dec=entry["decided"],
                prec=precision_s,
            )
        )
    lines.extend(
        [
            "",
            "## Locks",
            "",
            "- `captain_approval=false` (ledger never originates Captain approval)",
            "- `auto_apply=false` / `captain_approved=false` (no silent reputation mutation)",
            "- Deferred findings are excluded from the precision denominator",
            "",
        ]
    )
    return "\n".join(lines)


def _entry_experience_outcome(entry: dict[str, Any]) -> str:
    """Map a ledger entry to an Experience outcome without inventing success for FPs."""
    accepted = int(entry.get("accepted") or 0)
    rejected = int(entry.get("rejected") or 0)
    if accepted > 0 and rejected == 0:
        return "success"
    if rejected > 0 and accepted == 0:
        return "failed"
    if accepted > 0 and rejected > 0:
        return "partial"
    return "partial"


def ledger_to_experiences(
    ledger: dict[str, Any],
    *,
    plan_id: str = "",
    source_instance: str = "control-test",
) -> list[dict[str, Any]]:
    """One Experience per decided skill key (never blanket-success across skills)."""
    if source_instance not in _SOURCE_INSTANCES:
        raise PrecisionError(f"invalid source_instance: {source_instance!r}")

    experiences: list[dict[str, Any]] = []
    for entry in ledger.get("entries") or []:
        decided = int(entry.get("decided") or 0)
        if decided <= 0:
            continue
        key = str(entry["key"])
        precision = entry.get("precision")
        precision_s = "n/a" if precision is None else f"{float(precision):.1%}"
        lesson = (
            f"Precision ledger `{ledger['ledger_id']}` skill `{key}`: "
            f"precision={precision_s} "
            f"(accepted={entry['accepted']} rejected={entry['rejected']} "
            f"deferred={entry['deferred']})."
        )
        experience = {
            "experience_id": f"exp-precision-{ledger['ledger_id']}-{key}"[:120],
            "plan_id": plan_id or str(ledger.get("plan_id") or "b5-precision-ledger"),
            "run_id": str(ledger["ledger_id"]),
            "objective": (
                f"Aggregate Code Reviewer precision for skill {key} "
                f"in ledger {ledger['ledger_id']}"
            ),
            "outcome": _entry_experience_outcome(entry),
            "source_instance": source_instance,
            "skills_used": [key],
            "capabilities_exercised": ["code-review", "precision-ledger"],
            "lessons": [_redact_secret_text(lesson)],
            "provenance": {
                "ledger_id": ledger["ledger_id"],
                "skill": key,
                "accepted": int(entry["accepted"]),
                "rejected": int(entry["rejected"]),
                "deferred": int(entry["deferred"]),
                "decided": decided,
                "precision": precision,
            },
            "created_at": ledger.get("created_at") or _utc_now(),
        }
        experiences.append(_redact_secret_text(redact_secrets(experience)))
    return experiences


def proposal_eligible_entries(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    min_sample = int(ledger.get("min_sample_for_proposal") or DEFAULT_MIN_SAMPLE)
    eligible: list[dict[str, Any]] = []
    for entry in ledger.get("entries") or []:
        decided = int(entry.get("decided") or 0)
        if decided >= min_sample and entry.get("precision") is not None:
            eligible.append(entry)
    return eligible


def build_priority_proposal(
    ledger: dict[str, Any],
    *,
    proposal_notes: str = "",
) -> dict[str, Any]:
    """Build a proposal-only RoutingProposal from ledger precision.

    Skills below min_sample_for_proposal are omitted (no invented priority).
    """
    min_sample = int(ledger.get("min_sample_for_proposal") or DEFAULT_MIN_SAMPLE)
    eligible_entries = proposal_eligible_entries(ledger)
    if not eligible_entries:
        raise PrecisionError(
            f"insufficient sample for priority proposal "
            f"(need decided >= {min_sample} for at least one skill)"
        )

    synthetic: list[dict[str, Any]] = []
    for entry in eligible_entries:
        # Map precision to synthetic Experience outcomes for delta math:
        # high precision → success-heavy; low → failed-heavy.
        accepted = int(entry["accepted"])
        rejected = int(entry["rejected"])
        for i in range(accepted):
            synthetic.append(
                {
                    "experience_id": f"syn-{entry['key']}-tp-{i}",
                    "outcome": "success",
                    "skills_used": [entry["key"]],
                }
            )
        for i in range(rejected):
            synthetic.append(
                {
                    "experience_id": f"syn-{entry['key']}-fp-{i}",
                    "outcome": "failed",
                    "skills_used": [entry["key"]],
                }
            )

    notes = _redact_secret_text(
        proposal_notes
        or (
            "M33 / B5 precision-ledger priority proposal. "
            "auto_apply=false; Captain must approve before apply."
        )
    )
    proposal = build_routing_proposal(
        synthetic,
        proposal_id=f"route-precision-{ledger['ledger_id']}-{uuid4().hex[:8]}",
        notes=notes,
    )
    proposal["auto_apply"] = False
    proposal["captain_approved"] = False
    proposal["notes"] = _redact_secret_text(str(proposal.get("notes") or notes))
    return proposal


def write_precision_evidence(
    repo_root: Path,
    ledger: dict[str, Any],
    *,
    dashboard_md: str,
) -> dict[str, Path]:
    _safe_id(str(ledger["ledger_id"]), "ledger_id")
    out_dir = Path(repo_root) / ".agent" / "evidence" / "precision" / str(ledger["ledger_id"])
    out_dir.mkdir(parents=True, exist_ok=True)

    ledger_path = out_dir / "precision-ledger.json"
    dashboard_md_path = out_dir / "dashboard.md"
    dashboard_json_path = out_dir / "dashboard.json"

    ledger_path.write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    dashboard_md_path.write_text(dashboard_md, encoding="utf-8")
    dashboard_json = {
        "ledger_id": ledger["ledger_id"],
        "created_at": ledger["created_at"],
        "plan_id": ledger.get("plan_id"),
        "entries": ledger.get("entries") or [],
        "captain_approval": False,
        "locks": ledger.get("locks") or {"auto_apply": False, "captain_approved": False},
    }
    dashboard_json_path.write_text(
        json.dumps(_redact_secret_text(redact_secrets(dashboard_json)), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return {
        "dir": out_dir,
        "ledger": ledger_path,
        "dashboard_md": dashboard_md_path,
        "dashboard_json": dashboard_json_path,
    }


def aggregate_precision(
    *,
    repo_root: Path,
    outcomes: Path | None = None,
    outcomes_dir: Path | None = None,
    plan_id: str = "b5-precision-ledger",
    ledger_id: str | None = None,
    min_sample_for_proposal: int = DEFAULT_MIN_SAMPLE,
    write_experience_lesson: bool = True,
    emit_priority_proposal: bool = False,
    proposal_notes: str = "",
    source_instance: str | None = None,
) -> dict[str, Any]:
    """Load outcomes, write ledger + dashboard (+ optional Experience / proposal)."""
    root = Path(repo_root).resolve()
    paths = collect_outcome_paths(outcomes=outcomes, outcomes_dir=outcomes_dir)

    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(load_outcomes_bundle(path))

    ledger = build_precision_ledger(
        rows,
        ledger_id=ledger_id,
        plan_id=plan_id,
        source_outcome_paths=[str(p) for p in paths],
        min_sample_for_proposal=min_sample_for_proposal,
    )

    # Fail closed before durable writes when a priority proposal was requested
    # but no skill meets the sample floor.
    proposal: dict[str, Any] | None = None
    if emit_priority_proposal:
        proposal = build_priority_proposal(ledger, proposal_notes=proposal_notes)

    dashboard_md = render_dashboard_markdown(ledger)
    written = write_precision_evidence(root, ledger, dashboard_md=dashboard_md)

    resolved_source = source_instance or infer_source_instance(root)
    experience_paths: list[str] = []
    if write_experience_lesson:
        for experience in ledger_to_experiences(
            ledger,
            plan_id=plan_id,
            source_instance=resolved_source,
        ):
            experience_paths.append(str(write_experience(root, experience)))

    proposal_path = ""
    if proposal is not None:
        proposal_path = str(write_routing_proposal(root, proposal))

    return {
        "ledger_id": ledger["ledger_id"],
        "ledger_path": str(written["ledger"]),
        "dashboard_md_path": str(written["dashboard_md"]),
        "dashboard_json_path": str(written["dashboard_json"]),
        "evidence_dir": str(written["dir"]),
        "entry_count": len(ledger["entries"]),
        "experience_paths": experience_paths,
        "experience_path": experience_paths[0] if experience_paths else "",
        "proposal_path": proposal_path,
        "proposal_auto_apply": False if proposal_path else None,
        "captain_approval": False,
        "source_instance": resolved_source,
        "min_sample_for_proposal": min_sample_for_proposal,
    }
