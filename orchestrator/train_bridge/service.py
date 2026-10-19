"""Operator service for northstar train export|review (C7)."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.cognitive.git_facts import git_sha
from orchestrator.cycle.store import list_cycles
from orchestrator.providers.decision.state import redact_text
from orchestrator.schemas.validate import validate_document
from orchestrator.telemetry.store import list_experiences
from orchestrator.train_bridge.checklist import (
    ChecklistError,
    normalize_checklist,
    require_checklist_complete,
)
from orchestrator.train_bridge.enabled import require_train_bridge_enabled
from orchestrator.train_bridge.store import (
    TrainBridgeStoreError,
    load_export,
    load_export_file,
    write_export,
)

DEFAULT_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "experience"

# Extra patterns beyond decision.state.redact_text (export hand-off is stricter).
_EXTRA_SECRET_PATTERNS = (
    re.compile(r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*\S+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"(?i)authorization\s*[:=]\s*bearer\s+\S+"),
)


class TrainBridgeServiceError(ValueError):
    """Operator-facing training bridge errors."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _fixtures_allowed(*, allow_fixtures: bool) -> bool:
    if allow_fixtures:
        return True
    raw = os.environ.get("COMPASS_TRAIN_BRIDGE_FIXTURE", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _load_fixture_experiences() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not DEFAULT_FIXTURE_DIR.is_dir():
        return out
    for path in sorted(DEFAULT_FIXTURE_DIR.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        prov = dict(doc.get("provenance") or {})
        prov.setdefault("export_eligible", True)
        prov.setdefault("reviewed", True)
        prov["fixture"] = True
        doc["provenance"] = prov
        doc["_fixture_source"] = True
        out.append(doc)
    return out


def _collect_experiences(
    repo_root: Path, *, allow_fixtures: bool
) -> tuple[list[dict[str, Any]], str]:
    experiences = list_experiences(repo_root)
    if experiences:
        return experiences, "recorded"
    if _fixtures_allowed(allow_fixtures=allow_fixtures):
        fixtures = _load_fixture_experiences()
        if fixtures:
            return fixtures, "fixture"
    return [], "recorded"


def _eligible_experience(exp: dict[str, Any], *, include_unreviewed: bool) -> bool:
    if include_unreviewed:
        return True
    prov = exp.get("provenance") or {}
    if bool(prov.get("reviewed")) or bool(prov.get("captain_approved")):
        return True
    if bool(prov.get("export_eligible")):
        return True
    return False


def _eligible_cycle(cycle: dict[str, Any], *, include_unreviewed: bool) -> bool:
    if include_unreviewed:
        return True
    if bool(cycle.get("export_eligible")) or bool(cycle.get("reviewed")):
        return True
    if bool(cycle.get("learning_review_complete")):
        return True
    return False


def _redact_string(value: str, *, limit: int) -> str:
    # Apply export-stricter patterns first so "Authorization: Bearer <jwt>"
    # is fully consumed before the generic authorization:=\S+ pattern.
    cleaned = str(value or "")
    for pattern in _EXTRA_SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    cleaned = redact_text(cleaned)
    return cleaned[:limit]


def _redact_trajectory(exp: dict[str, Any], *, source: str) -> dict[str, Any]:
    return {
        "source": source,
        "experience_id": str(exp.get("experience_id") or exp.get("id") or "")[:128],
        "plan_id": str(exp.get("plan_id") or "")[:128],
        "run_id": str(exp.get("run_id") or "")[:128],
        "objective": _redact_string(str(exp.get("objective") or ""), limit=2000),
        "outcome": str(exp.get("outcome") or "")[:64],
        "skills_used": [
            _redact_string(str(s), limit=120) for s in (exp.get("skills_used") or [])
        ][:20],
        "capabilities_exercised": [
            _redact_string(str(c), limit=120)
            for c in (exp.get("capabilities_exercised") or [])
        ][:20],
        "lessons": [
            _redact_string(str(x), limit=500) for x in (exp.get("lessons") or [])
        ][:20],
        "created_at": str(exp.get("created_at") or "")[:64],
    }


def _trajectories_from_cycles(
    repo_root: Path, *, include_unreviewed: bool
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for cycle in list_cycles(repo_root):
        if str(cycle.get("status") or "") != "closed":
            continue
        if not _eligible_cycle(cycle, include_unreviewed=include_unreviewed):
            continue
        exp_id = str(cycle.get("experience_id") or "")
        traj = {
            "source": "cycle",
            "experience_id": exp_id[:128],
            "plan_id": str(cycle.get("plan_id") or "")[:128],
            "run_id": str(cycle.get("execution_run_id") or "")[:128],
            "objective": _redact_string(str(cycle.get("objective") or ""), limit=2000),
            "outcome": str(cycle.get("outcome") or "success")[:64],
            "skills_used": [
                _redact_string(str(s), limit=120)
                for s in (cycle.get("skills_used") or [])
            ][:20],
            "capabilities_exercised": [
                _redact_string(str(c), limit=120)
                for c in (cycle.get("capability_gaps") or [])
            ][:20],
            "lessons": [
                _redact_string(str(p.get("summary") or p.get("title") or ""), limit=500)
                for p in (cycle.get("draft_proposals") or [])
            ][:20],
            "created_at": str(cycle.get("updated_at") or cycle.get("created_at") or "")[
                :64
            ],
            "cycle_execution_id": str(cycle.get("execution_id") or "")[:128],
        }
        out.append(traj)
    return out


def train_export(
    repo_root: Path,
    *,
    source: str = "experiences",
    plan_id: str | None = None,
    checklist: dict[str, Any] | None = None,
    include_unreviewed: bool = False,
    allow_fixtures: bool = False,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Build and persist a training-export manifest (local hermetic hand-off)."""
    require_train_bridge_enabled()
    repo_root = Path(repo_root).resolve()
    if source not in {"experiences", "cycles"}:
        raise TrainBridgeServiceError("--from must be experiences or cycles")

    try:
        checks = normalize_checklist(checklist)
        require_checklist_complete(checks)
    except ChecklistError as exc:
        raise TrainBridgeServiceError(str(exc)) from exc

    run_mode = "recorded"
    trajectories: list[dict[str, Any]] = []
    if source == "experiences":
        experiences, run_mode = _collect_experiences(
            repo_root, allow_fixtures=allow_fixtures
        )
        for exp in experiences:
            if plan_id and str(exp.get("plan_id") or "") != plan_id:
                continue
            if not _eligible_experience(exp, include_unreviewed=include_unreviewed):
                continue
            trajectories.append(_redact_trajectory(exp, source="experience"))
    else:
        trajectories = _trajectories_from_cycles(
            repo_root, include_unreviewed=include_unreviewed
        )
        if plan_id:
            trajectories = [t for t in trajectories if t.get("plan_id") == plan_id]

    if not trajectories:
        hint = (
            "no eligible trajectories to export — record reviewed Experiences/cycles, "
            "or pass --fixture / COMPASS_TRAIN_BRIDGE_FIXTURE=1 for hermetic fixtures, "
            "or --include-unreviewed for explicit override"
        )
        raise TrainBridgeServiceError(hint)

    head_sha = git_sha(repo_root) or ""
    version = _version(repo_root)
    digest = hashlib.sha256(
        f"{source}|{len(trajectories)}|{head_sha}|{run_mode}".encode("utf-8")
    ).hexdigest()[:12]
    export_id = f"train-export-{digest}-{uuid4().hex[:6]}"
    now = _utc_now()

    manifest: dict[str, Any] = {
        "schema_version": "1",
        "export_id": export_id,
        "source": source,
        "run_mode": run_mode,
        "plan_id_filter": plan_id,
        "trajectory_count": len(trajectories),
        "trajectories": trajectories,
        "permission_checklist": checks,
        "dataset_schema_version": "northstar.training-export.v1",
        "repository_sha": head_sha,
        "northstar_version": version,
        "citations": [],
        "notes": (
            "Cognitive Core C7 training-export manifest. Local hand-off only — "
            "does not upload, train weights, or grant authority. "
            "Specialized Model ingest requires Captain approval after eval+security. "
            "ready_for_specialized_model review gates are operator attestations."
        ),
        "auto_uploaded": False,
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": now,
    }
    if head_sha:
        manifest["citations"].append(
            {"kind": "git", "ref": f"HEAD={head_sha}", "claim_kind": "observed"}
        )
    if version:
        manifest["citations"].append(
            {"kind": "version", "ref": f"VERSION={version}", "claim_kind": "observed"}
        )
    if run_mode == "fixture":
        manifest["citations"].append(
            {
                "kind": "file",
                "ref": "tests/fixtures/experience/",
                "claim_kind": "documented",
            }
        )
    manifest["citations"].append(
        {
            "kind": "file",
            "ref": "orchestrator/training/from_experience.py",
            "claim_kind": "documented",
        }
    )
    for traj in trajectories[:12]:
        eid = str(traj.get("experience_id") or "")
        if eid:
            manifest["citations"].append(
                {"kind": "experience", "ref": eid, "claim_kind": "observed"}
            )
        cid = str(traj.get("cycle_execution_id") or "")
        if cid:
            manifest["citations"].append(
                {"kind": "cycle", "ref": cid, "claim_kind": "observed"}
            )

    # Canonical store write (so review --export-id works); optional --out copy.
    store_path = write_export(repo_root, {k: v for k, v in manifest.items()})
    manifest["export_path"] = str(store_path)
    # Re-validate with export_path and rewrite canonical store.
    validate_document(manifest, "training-export-manifest.schema.json")
    store_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if out_dir is not None:
        target_root = Path(out_dir).resolve()
        target_root.mkdir(parents=True, exist_ok=True)
        alt = target_root / f"{export_id}.json"
        alt.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        manifest["export_path"] = str(alt)
        # Keep canonical store pointing at itself; alt is a copy.
        store_copy = dict(manifest)
        store_copy["export_path"] = str(store_path)
        store_path.write_text(
            json.dumps(store_copy, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    return manifest


def train_review(
    repo_root: Path,
    *,
    export_id: str = "",
    export_file: Path | None = None,
    independent_eval_complete: bool = False,
    security_review_complete: bool = False,
    captain_approval_recorded: bool = False,
) -> dict[str, Any]:
    """Captain-facing review packet for a training export."""
    require_train_bridge_enabled()
    repo_root = Path(repo_root).resolve()

    try:
        if export_file is not None:
            manifest = load_export_file(Path(export_file))
            eid = str(manifest.get("export_id") or "")
        else:
            eid = (export_id or "").strip()
            if not eid:
                raise TrainBridgeServiceError(
                    "--export-id or --export-path is required for train review"
                )
            manifest = load_export(repo_root, eid)
    except TrainBridgeStoreError as exc:
        raise TrainBridgeServiceError(str(exc)) from exc

    gates = {
        "independent_eval_complete": bool(independent_eval_complete),
        "security_review_complete": bool(security_review_complete),
        "captain_approval_recorded": bool(captain_approval_recorded),
        "export_checklist_complete": all(
            bool(v) for v in (manifest.get("permission_checklist") or {}).values()
        ),
    }
    ready = all(gates.values())

    digest = hashlib.sha256(f"review|{eid}|{ready}".encode("utf-8")).hexdigest()[:12]
    packet: dict[str, Any] = {
        "schema_version": "1",
        "review_id": f"train-review-{digest}-{uuid4().hex[:6]}",
        "export_id": eid,
        "trajectory_count": int(manifest.get("trajectory_count") or 0),
        "gates": gates,
        "ready_for_specialized_model": ready,
        "blocking_reasons": [k for k, v in gates.items() if not v],
        "repository_sha": str(manifest.get("repository_sha") or ""),
        "northstar_version": _version(repo_root),
        "citations": [
            {"kind": "export", "ref": eid, "claim_kind": "observed"},
        ],
        "notes": (
            "Captain Training Bridge review. ready_for_specialized_model reflects "
            "operator attestations for independent eval, security review, Captain "
            "approval, and complete export checklist — not cryptographic proof. "
            "This packet never uploads or changes weights."
        ),
        "auto_uploaded": False,
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }
    validate_document(packet, "training-export-review.schema.json")
    return packet
