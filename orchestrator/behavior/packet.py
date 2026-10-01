"""Normalize ExecutionRun (+ optional evidence refs) into a bounded eval packet."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from orchestrator.behavior.signals import SCHEMA_VERSION
from orchestrator.telemetry.store import load_execution_run

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class BehaviorPacketError(ValueError):
    """Raised when an evaluation packet cannot be built safely."""


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise BehaviorPacketError(f"unsafe {label}: {value!r}")
    return value


def _read_version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip() or "unknown"
    return "unknown"


def _git_sha(repo_root: Path) -> str:
    head = repo_root / ".git" / "HEAD"
    if not head.is_file():
        return ""
    raw = head.read_text(encoding="utf-8").strip()
    if raw.startswith("ref:"):
        ref = raw.split(" ", 1)[1].strip()
        ref_path = repo_root / ".git" / ref
        if ref_path.is_file():
            return ref_path.read_text(encoding="utf-8").strip()
        return ""
    return raw


def _compact_diff_meta(provenance: dict[str, Any]) -> dict[str, Any]:
    """Keep path/ID refs only — never full diffs or secrets."""
    allowed = ("issue", "branch", "worktree", "commits", "pull_request", "files_changed")
    out: dict[str, Any] = {}
    for key in allowed:
        if key in provenance:
            out[key] = provenance[key]
    # Cap commits list
    commits = out.get("commits")
    if isinstance(commits, list):
        out["commits"] = [str(c) for c in commits[:20]]
    files = out.get("files_changed")
    if isinstance(files, list):
        out["files_changed"] = [str(f) for f in files[:50]]
    return out


def _evidence_refs(repo_root: Path, run: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    run_id = str(run.get("run_id") or "")
    if run_id:
        refs.append({"kind": "execution_run", "path": f".agent/runs/{run_id}.json"})
    experience_id = str(run.get("experience_id") or "")
    if experience_id:
        refs.append({"kind": "experience", "path": f".agent/experience/{experience_id}.json"})
    else:
        # Best-effort: find experience with matching run_id
        exp_dir = repo_root / ".agent" / "experience"
        if exp_dir.is_dir():
            for path in sorted(exp_dir.glob("*.json")):
                try:
                    with path.open(encoding="utf-8") as handle:
                        doc = json.load(handle)
                except (OSError, json.JSONDecodeError):
                    continue
                if isinstance(doc, dict) and doc.get("run_id") == run_id:
                    refs.append({"kind": "experience", "path": f".agent/experience/{path.name}"})
                    break
    plan_id = str(run.get("plan_id") or "")
    if plan_id:
        refs.append({"kind": "plan_id", "path": plan_id})
    return refs


def packet_content_hash(packet: dict[str, Any]) -> str:
    payload = {
        "execution_id": packet.get("execution_id"),
        "task_id": packet.get("task_id"),
        "objective": packet.get("objective"),
        "outcome": packet.get("outcome"),
        "skill_ids": packet.get("skill_ids"),
        "agents": packet.get("agents"),
        "repository_sha": packet.get("repository_sha"),
        "evidence": packet.get("evidence"),
        "diff_meta": packet.get("diff_meta"),
        "schema_version": packet.get("schema_version"),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def build_evaluation_packet(
    repo_root: Path,
    execution_id: str,
    *,
    plan_ref: str = "",
) -> dict[str, Any]:
    """Load ExecutionRun and produce a bounded, schema-oriented packet."""
    root = Path(repo_root).resolve()
    eid = _safe_id(execution_id, label="execution_id")
    run = load_execution_run(root, eid)
    agents = [str(a) for a in (run.get("agents") or [])]
    skills = [str(s) for s in (run.get("skills") or [])]
    models = [str(m) for m in (run.get("models") or [])]
    provenance = dict(run.get("provenance") or {})
    repo_sha = _git_sha(root)
    if not repo_sha:
        commits = provenance.get("commits")
        if isinstance(commits, list) and commits:
            repo_sha = str(commits[0])
    packet: dict[str, Any] = {
        "execution_id": eid,
        "task_id": str(run.get("task_id") or ""),
        "plan_id": str(run.get("plan_id") or ""),
        "plan_ref": plan_ref or str(run.get("plan_id") or ""),
        "objective": str(run.get("objective") or ""),
        "outcome": str(run.get("outcome") or ""),
        "agents": agents,
        "agent": agents[0] if agents else "",
        "models": models,
        "model": models[0] if models else "",
        "skill_ids": skills,
        "repository_sha": repo_sha,
        "northstar_version": _read_version(root),
        "diff_meta": _compact_diff_meta(provenance),
        "evidence": _evidence_refs(root, run),
        "schema_version": SCHEMA_VERSION,
    }
    packet["content_hash"] = packet_content_hash(packet)
    return packet


def list_pending_execution_ids(repo_root: Path, *, ledger_execution_ids: set[str]) -> list[str]:
    """Return completed execution run IDs not yet present in the behavior ledger."""
    runs_dir = Path(repo_root) / ".agent" / "runs"
    if not runs_dir.is_dir():
        return []
    pending: list[str] = []
    for path in sorted(runs_dir.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(doc, dict):
            continue
        run_id = str(doc.get("run_id") or path.stem)
        outcome = str(doc.get("outcome") or "")
        if outcome in {"pending"}:
            continue
        if run_id in ledger_execution_ids:
            continue
        pending.append(run_id)
    return pending
