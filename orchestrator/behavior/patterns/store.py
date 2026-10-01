"""Persist behavior patterns and proposal-only candidates (M47)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from orchestrator.behavior.patterns.quality import PATTERN_SCHEMA_VERSION
from orchestrator.schemas.validate import ValidationError, validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class BehaviorPatternStoreError(ValueError):
    """Raised when pattern persistence is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def patterns_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evaluations" / "behavior" / "patterns"


def candidates_dir(repo_root: Path) -> Path:
    return patterns_dir(repo_root) / "candidates"


def ensure_layout(repo_root: Path) -> None:
    out = patterns_dir(repo_root)
    out.mkdir(parents=True, exist_ok=True)
    cand = candidates_dir(repo_root)
    cand.mkdir(parents=True, exist_ok=True)
    keep = out / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise BehaviorPatternStoreError(f"unsafe {label}: {value!r}")
    return value


def pattern_id_for_key(
    *,
    signal: str,
    polarity: str,
    agent: str,
    skill_id: str,
) -> str:
    """Stable deterministic id from grouping dimensions."""
    raw = f"{polarity}|{signal}|{agent}|{skill_id}"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"bpat-{h}"


def build_pattern(
    *,
    signal: str,
    polarity: str,
    agent: str,
    skill_id: str,
    evidence_evaluation_ids: list[str],
    scores: list[float],
    threshold: float,
    min_occurrence: int,
    pattern_id: str | None = None,
) -> dict[str, Any]:
    eid = pattern_id or pattern_id_for_key(
        signal=signal, polarity=polarity, agent=agent, skill_id=skill_id
    )
    _safe_id(eid, label="pattern_id")
    mean = sum(scores) / len(scores) if scores else 0.0
    summary = (
        f"{polarity} pattern on signal `{signal}` "
        f"(agent={agent or '*'}, skill={skill_id or '*'}) "
        f"seen {len(evidence_evaluation_ids)} times (min={min_occurrence})"
    )
    return {
        "pattern_id": eid,
        "signal": signal,
        "polarity": polarity,
        "agent": agent,
        "skill_id": skill_id,
        "occurrence_count": len(evidence_evaluation_ids),
        "min_occurrence": int(min_occurrence),
        "mean_score": round(mean, 4),
        "threshold": float(threshold),
        "evidence_evaluation_ids": list(evidence_evaluation_ids),
        "summary": summary,
        "schema_version": PATTERN_SCHEMA_VERSION,
        "created_at": _utc_now(),
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def build_candidate(pattern: dict[str, Any], *, candidate_id: str | None = None) -> dict[str, Any]:
    """Build proposal-only guidance; candidate_id is stable from pattern_id."""
    pid = str(pattern.get("pattern_id") or "")
    if candidate_id:
        cid = candidate_id
    elif pid.startswith("bpat-"):
        cid = f"bcand-{pid[len('bpat-'):]}"
    else:
        digest = hashlib.sha256(pid.encode("utf-8")).hexdigest()[:12]
        cid = f"bcand-{digest}"
    _safe_id(cid, label="candidate_id")
    polarity = str(pattern.get("polarity") or "negative")
    signal = str(pattern.get("signal") or "")
    if polarity == "positive":
        guidance = (
            f"Preserve successful behavior associated with `{signal}` "
            f"(agent={pattern.get('agent') or '*'}, skill={pattern.get('skill_id') or '*'})."
        )
    else:
        guidance = (
            f"Reduce friction signal `{signal}` "
            f"(agent={pattern.get('agent') or '*'}, skill={pattern.get('skill_id') or '*'})."
        )
    return {
        "candidate_id": cid,
        "pattern_id": pid,
        "kind": "behavioral-guidance",
        "summary": guidance,
        "signal": signal,
        "polarity": polarity,
        "agent": str(pattern.get("agent") or ""),
        "skill_id": str(pattern.get("skill_id") or ""),
        "evidence_evaluation_ids": list(pattern.get("evidence_evaluation_ids") or []),
        "approved_for_execution": False,
        "authority_mutation": False,
        "schema_version": PATTERN_SCHEMA_VERSION,
        "created_at": _utc_now(),
    }


def _preserve_created_at(path: Path, doc: dict[str, Any]) -> dict[str, Any]:
    """Keep first-write created_at; stamp updated_at on overwrite."""
    out = dict(doc)
    if path.is_file():
        try:
            with path.open(encoding="utf-8") as handle:
                existing = json.load(handle)
        except (OSError, json.JSONDecodeError):
            existing = None
        if isinstance(existing, dict) and existing.get("created_at"):
            out["created_at"] = str(existing["created_at"])
            out["updated_at"] = _utc_now()
    return out


def write_pattern(repo_root: Path, pattern: dict[str, Any]) -> Path:
    pid = _safe_id(str(pattern["pattern_id"]), label="pattern_id")
    ensure_layout(repo_root)
    path = patterns_dir(repo_root) / f"{pid}.json"
    payload = _preserve_created_at(path, pattern)
    try:
        validate_document(payload, "behavior-pattern.schema.json")
    except ValidationError as exc:
        raise BehaviorPatternStoreError(str(exc)) from exc
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    return path


def write_candidate(repo_root: Path, candidate: dict[str, Any]) -> Path:
    cid = _safe_id(str(candidate["candidate_id"]), label="candidate_id")
    ensure_layout(repo_root)
    path = candidates_dir(repo_root) / f"{cid}.json"
    payload = _preserve_created_at(path, candidate)
    try:
        validate_document(payload, "behavior-candidate.schema.json")
    except ValidationError as exc:
        raise BehaviorPatternStoreError(str(exc)) from exc
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    return path


def prune_stale(
    repo_root: Path,
    *,
    active_pattern_ids: set[str],
    active_candidate_ids: set[str],
) -> dict[str, list[str]]:
    """Remove pattern/candidate JSON not in the active detection set."""
    ensure_layout(repo_root)
    removed_patterns: list[str] = []
    removed_candidates: list[str] = []
    for path in sorted(patterns_dir(repo_root).glob("bpat-*.json")):
        pid = path.stem
        if pid not in active_pattern_ids:
            path.unlink(missing_ok=True)
            removed_patterns.append(pid)
    for path in sorted(candidates_dir(repo_root).glob("bcand-*.json")):
        cid = path.stem
        if cid not in active_candidate_ids:
            path.unlink(missing_ok=True)
            removed_candidates.append(cid)
    return {
        "removed_patterns": removed_patterns,
        "removed_candidates": removed_candidates,
    }


def list_patterns(repo_root: Path) -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    out: list[dict[str, Any]] = []
    for path in sorted(patterns_dir(repo_root).glob("bpat-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict):
            out.append(doc)
    return out


def load_pattern(repo_root: Path, pattern_id: str) -> dict[str, Any]:
    pid = _safe_id(pattern_id, label="pattern_id")
    path = patterns_dir(repo_root) / f"{pid}.json"
    if not path.is_file():
        raise BehaviorPatternStoreError(f"pattern not found: {pid}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "behavior-pattern.schema.json")
    return doc


def list_candidates(repo_root: Path) -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    out: list[dict[str, Any]] = []
    for path in sorted(candidates_dir(repo_root).glob("bcand-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict):
            out.append(doc)
    return out
