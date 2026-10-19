"""Operator service for northstar rea investigate (C6)."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.cognitive.git_facts import git_sha
from orchestrator.rea.checklist import (
    ChecklistError,
    normalize_checklist,
    require_checklist_complete,
)
from orchestrator.rea.enabled import require_rea_enabled
from orchestrator.schemas.validate import validate_document

MODES = (
    "native",
    "js-electron",
    "dotnet",
    "browser",
    "android",
    "network-capture",
)

DEFAULT_FIXTURE = Path(__file__).resolve().parents[2] / (
    "tests/fixtures/rea-evidence/sample-packet.json"
)


class ReaServiceError(ValueError):
    """Operator-facing REA errors."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _hash_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_fixture(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ReaServiceError(f"REA fixture not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def investigate(
    repo_root: Path,
    *,
    target: str,
    question: str,
    mode: str = "native",
    allow_live: bool = False,
    checklist: dict[str, Any] | None = None,
    fixture_path: Path | None = None,
) -> dict[str, Any]:
    """Build a schema-validated REA evidence packet (hermetic by default)."""
    require_rea_enabled()
    repo_root = Path(repo_root).resolve()
    tgt = (target or "").strip()
    q = (question or "").strip()
    if not tgt:
        raise ReaServiceError("--target is required for rea investigate")
    if not q:
        raise ReaServiceError("--question is required for rea investigate")
    if mode not in MODES:
        raise ReaServiceError(
            f"invalid --mode {mode!r}; expected one of: {', '.join(MODES)}"
        )

    try:
        checks = normalize_checklist(checklist)
    except ChecklistError as exc:
        raise ReaServiceError(str(exc)) from exc

    # Speculative / forbidden claim patterns — always refuse.
    forbidden = (
        "private pretraining",
        "hidden optimizer",
        "recover training data",
        "reconstruct training corpus",
    )
    ql = q.lower()
    if any(f in ql for f in forbidden):
        raise ReaServiceError(
            "question refuses speculative recovery of private training data / "
            "hidden optimizer details — out of scope for REA evidence"
        )

    head_sha = git_sha(repo_root) or ""
    version = _version(repo_root)
    now = _utc_now()
    digest = hashlib.sha256(f"{tgt}|{q}|{mode}".encode("utf-8")).hexdigest()[:12]
    packet_id = f"rea-{digest}-{uuid4().hex[:6]}"

    if allow_live:
        try:
            require_checklist_complete(checks)
        except ChecklistError as exc:
            raise ReaServiceError(str(exc)) from exc
        return _live_or_unavailable_packet(
            repo_root=repo_root,
            packet_id=packet_id,
            target=tgt,
            question=q,
            mode=mode,
            checks=checks,
            head_sha=head_sha,
            version=version,
            now=now,
        )

    # Hermetic default
    fixture = Path(fixture_path) if fixture_path else DEFAULT_FIXTURE
    raw = _load_fixture(fixture)
    observations = list(raw.get("observations") or [])
    # Ensure claim kinds are valid; force hypotheses labeled correctly.
    cleaned_obs: list[dict[str, Any]] = []
    for item in observations:
        kind = str(item.get("claim_kind") or "hypothesis")
        if kind not in {"observed", "hypothesis"}:
            kind = "hypothesis"
        cleaned_obs.append(
            {
                "claim_kind": kind,
                "text": str(item.get("text") or ""),
                "confidence": float(item.get("confidence") or 0.0),
            }
        )
    if not cleaned_obs:
        cleaned_obs.append(
            {
                "claim_kind": "hypothesis",
                "text": "Fixture contained no observations.",
                "confidence": 0.0,
            }
        )

    artifact_hash = str(raw.get("artifact_hash") or "") or _hash_text(
        json.dumps({"target": tgt, "question": q, "mode": mode}, sort_keys=True)
    )
    commands = list(raw.get("commands") or ["fixture:replay"])
    uncertainties = list(raw.get("uncertainties") or [])
    if not uncertainties:
        uncertainties.append("Hermetic fixture — not a live REA execution.")

    packet: dict[str, Any] = {
        "schema_version": "1",
        "packet_id": packet_id,
        "target": tgt,
        "question": q,
        "mode": mode,
        "run_mode": "fixture",
        "permission_checklist": checks,
        "tool_name": str(raw.get("tool_name") or "rea-fixture"),
        "tool_version": str(raw.get("tool_version") or "fixture-1"),
        "commands": commands,
        "artifact_hash": artifact_hash,
        "observations": cleaned_obs,
        "uncertainties": uncertainties,
        "repository_sha": head_sha,
        "northstar_version": version,
        "fixture_path": str(fixture),
        "live_attempted": False,
        "live_available": False,
        "citations": [
            {"kind": "fixture", "ref": str(fixture), "claim_kind": "observed"},
        ],
        "notes": (
            "Cognitive Core C6 REA evidence packet (hermetic fixture). "
            "Hypotheses are not repository facts. "
            "Live REA requires --allow-live and a complete permission checklist."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": now,
    }
    if head_sha:
        packet["citations"].append(
            {"kind": "git", "ref": f"HEAD={head_sha}", "claim_kind": "observed"}
        )
    if version:
        packet["citations"].append(
            {"kind": "version", "ref": f"VERSION={version}", "claim_kind": "observed"}
        )
    validate_document(packet, "rea-evidence-packet.schema.json")
    return packet


def _live_or_unavailable_packet(
    *,
    repo_root: Path,
    packet_id: str,
    target: str,
    question: str,
    mode: str,
    checks: dict[str, bool],
    head_sha: str,
    version: str,
    now: str,
) -> dict[str, Any]:
    """Attempt live REA only if binary present; otherwise record unavailable."""
    rea_bin = shutil.which("rea") or shutil.which("rea-cli")
    target_path = Path(target)
    artifact_hash = _hash_file(target_path) if target_path.is_file() else _hash_text(target)

    if not rea_bin:
        packet: dict[str, Any] = {
            "schema_version": "1",
            "packet_id": packet_id,
            "target": target,
            "question": question,
            "mode": mode,
            "run_mode": "live_unavailable",
            "permission_checklist": checks,
            "tool_name": "rea",
            "tool_version": "unavailable",
            "commands": ["live:skipped — REA binary not found on PATH"],
            "artifact_hash": artifact_hash,
            "observations": [
                {
                    "claim_kind": "hypothesis",
                    "text": (
                        "Live REA binary not available; no binary analysis performed. "
                        "Checklist was complete but execution could not start."
                    ),
                    "confidence": 0.0,
                }
            ],
            "uncertainties": [
                "REA CLI not installed or not on PATH",
                "No live observations captured",
            ],
            "repository_sha": head_sha,
            "northstar_version": version,
            "fixture_path": None,
            "live_attempted": True,
            "live_available": False,
            "citations": [
                {"kind": "target", "ref": target, "claim_kind": "observed"},
            ],
            "notes": (
                "Live REA requested but binary unavailable. "
                "No speculative conclusions recorded as facts. Authority flags locked false."
            ),
            "approved_for_execution": False,
            "authority_mutation": False,
            "generated_at": now,
        }
        if head_sha:
            packet["citations"].append(
                {"kind": "git", "ref": f"HEAD={head_sha}", "claim_kind": "observed"}
            )
        validate_document(packet, "rea-evidence-packet.schema.json")
        return packet

    # Binary present: still do not auto-execute arbitrary targets in this milestone.
    # Record a governed stub observation — full REA spawn is out of CI scope.
    packet = {
        "schema_version": "1",
        "packet_id": packet_id,
        "target": target,
        "question": question,
        "mode": mode,
        "run_mode": "live_stub",
        "permission_checklist": checks,
        "tool_name": "rea",
        "tool_version": f"detected:{Path(rea_bin).name}",
        "commands": [
            f"# detected {rea_bin}",
            "# live execution stub — Captain must approve explicit REA invoke outside CI",
        ],
        "artifact_hash": artifact_hash,
        "observations": [
            {
                "claim_kind": "observed",
                "text": f"REA binary detected at {rea_bin}; no auto-execution performed.",
                "confidence": 1.0,
            },
            {
                "claim_kind": "hypothesis",
                "text": (
                    "Full live REA invoke remains operator-supervised; "
                    "this packet only records detection + checklist."
                ),
                "confidence": 0.2,
            },
        ],
        "uncertainties": [
            "Auto-execution of REA against arbitrary targets is disabled in v1.65.0",
        ],
        "repository_sha": head_sha,
        "northstar_version": version,
        "fixture_path": None,
        "live_attempted": True,
        "live_available": True,
        "citations": [
            {"kind": "target", "ref": target, "claim_kind": "observed"},
            {"kind": "tool", "ref": rea_bin, "claim_kind": "observed"},
        ],
        "notes": (
            "Live REA binary detected; auto-execution withheld. "
            "Authority flags locked false."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": now,
    }
    if head_sha:
        packet["citations"].append(
            {"kind": "git", "ref": f"HEAD={head_sha}", "claim_kind": "observed"}
        )
    validate_document(packet, "rea-evidence-packet.schema.json")
    return packet
