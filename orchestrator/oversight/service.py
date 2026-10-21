"""Compose brain sync + Overseer snapshot/compare/reconcile into one oversight run."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.cognitive.enabled import brain_enabled
from orchestrator.cognitive.git_facts import git_sha
from orchestrator.cognitive.service import sync as brain_sync
from orchestrator.oversight.enabled import require_oversight_status_gate
from orchestrator.schemas.validate import validate_document
from orchestrator.status.service import compare as status_compare
from orchestrator.status.service import reconcile as status_reconcile
from orchestrator.status.service import snapshot as status_snapshot
from orchestrator.status.store import list_snapshots


class OversightServiceError(ValueError):
    """Operator-facing oversight errors."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _step(
    step_id: str,
    status: str,
    summary: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": step_id,
        "status": status,
        "summary": summary,
        "details": details or {},
    }


def _prior_snapshot_sha(repo_root: Path, *, current_snapshot_id: str) -> str | None:
    snaps = list_snapshots(repo_root)
    if not snaps:
        return None

    def _sort_key(doc: dict[str, Any]) -> str:
        return str(doc.get("created_at") or "")

    ordered = sorted(snaps, key=_sort_key, reverse=True)
    for doc in ordered:
        sid = str(doc.get("snapshot_id") or "")
        if sid and sid != current_snapshot_id:
            sha = str(doc.get("repository_sha") or "").strip()
            if sha:
                return sha
    return None


def run_oversight(
    repo_root: Path,
    *,
    since_sha: str | None = None,
    include_brain: bool | None = None,
    evidence_dir: Path | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    """Run gated read-only oversight compose and return a schema-validated report."""
    require_oversight_status_gate()
    repo_root = Path(repo_root).resolve()
    steps: list[dict[str, Any]] = []
    warnings: list[str] = []

    do_brain = brain_enabled() if include_brain is None else bool(include_brain)
    brain_synced = False
    if do_brain:
        if not brain_enabled():
            raise OversightServiceError(
                "brain sync requested but COMPASS_BRAIN_ENABLED is unset"
            )
        sync_doc = brain_sync(repo_root)
        brain_synced = True
        steps.append(
            _step(
                "brain-sync",
                "pass",
                f"brain sync freshness={sync_doc.get('freshness')}",
                {
                    "freshness": sync_doc.get("freshness"),
                    "snapshot_id": (sync_doc.get("snapshot") or {}).get("snapshot_id"),
                },
            )
        )
    else:
        steps.append(
            _step(
                "brain-sync",
                "skipped",
                "brain sync skipped (COMPASS_BRAIN_ENABLED unset)",
            )
        )

    snap_result = status_snapshot(repo_root)
    snap = snap_result.get("snapshot") or {}
    snapshot_id = str(snap.get("snapshot_id") or "") or None
    finding_count = len(snap.get("findings") or [])
    head = git_sha(repo_root) or str(snap.get("repository_sha") or "")
    steps.append(
        _step(
            "status-snapshot",
            "pass",
            f"snapshot {snapshot_id} findings={finding_count}",
            {
                "snapshot_id": snapshot_id,
                "finding_count": finding_count,
                "plan_status": snap.get("plan_status"),
                "skill_count_fs": snap.get("skill_count_fs"),
            },
        )
    )
    if snap.get("approved_for_execution") is not False or snap.get("authority_mutation") is not False:
        warnings.append("status snapshot authority flags unexpected")

    compare_status = "skipped"
    since = (since_sha or "").strip() or None
    if not since and snapshot_id:
        since = _prior_snapshot_sha(repo_root, current_snapshot_id=snapshot_id)
    if since:
        try:
            cmp = status_compare(repo_root, since=since)
            compare_status = "compared"
            steps.append(
                _step(
                    "status-compare",
                    "pass",
                    (
                        f"compared since {since[:12]} "
                        f"added={len(cmp.get('added_finding_kinds') or [])} "
                        f"resolved={len(cmp.get('resolved_finding_kinds') or [])}"
                    ),
                    {
                        "since": since,
                        "added_finding_kinds": list(cmp.get("added_finding_kinds") or []),
                        "resolved_finding_kinds": list(
                            cmp.get("resolved_finding_kinds") or []
                        ),
                    },
                )
            )
            if (
                cmp.get("approved_for_execution") is not False
                or cmp.get("authority_mutation") is not False
            ):
                warnings.append("status compare authority flags unexpected")
        except Exception as exc:  # noqa: BLE001 — record as step failure
            compare_status = "failed"
            warnings.append(f"status compare failed: {exc}")
            steps.append(
                _step(
                    "status-compare",
                    "fail",
                    f"compare failed: {exc}",
                    {"since": since},
                )
            )
    else:
        steps.append(
            _step(
                "status-compare",
                "skipped",
                "no --since SHA and no prior Overseer snapshot SHA available",
            )
        )

    recon = status_reconcile(repo_root, snapshot_id=snapshot_id or "")
    proposal = recon.get("proposal") or {}
    proposal_id = str(proposal.get("proposal_id") or "") or None
    proposal_path = str(recon.get("path") or "") or None
    action_count = len(proposal.get("actions") or [])
    applied = bool(proposal.get("applied"))
    recon_ok = (
        applied is False
        and proposal.get("approved_for_execution") is False
        and proposal.get("authority_mutation") is False
        and recon.get("applied") is False
    )
    steps.append(
        _step(
            "status-reconcile",
            "pass" if recon_ok else "fail",
            f"reconcile proposal {proposal_id} actions={action_count} applied={applied}",
            {
                "proposal_id": proposal_id,
                "proposal_path": proposal_path,
                "action_count": action_count,
                "applied": applied,
            },
        )
    )
    if not recon_ok:
        warnings.append("reconcile proposal authority/applied flags unexpected")

    fail_count = sum(1 for s in steps if s["status"] == "fail")
    if fail_count:
        overall = "fail"
    elif warnings:
        overall = "warn"
    else:
        overall = "pass"

    run_id = f"oversight-{uuid4().hex[:10]}"
    version = _version(repo_root)
    report: dict[str, Any] = {
        "schema_version": "1",
        "run_id": run_id,
        "plan_id": "read-only-persistent-oversight",
        "repository_sha": head,
        "northstar_version": version,
        "since_sha": since,
        "steps": steps,
        "brain_synced": brain_synced,
        "snapshot_id": snapshot_id,
        "compare_status": compare_status,
        "proposal_id": proposal_id,
        "proposal_path": proposal_path,
        "proposal_applied": False,
        "finding_count": finding_count,
        "action_count": action_count,
        "warnings": warnings,
        "overall_status": overall,
        "evidence_path": None,
        "notes": (
            "Read-only persistent oversight run. Compose of optional brain sync + "
            "Overseer snapshot/compare/reconcile. Reconcile proposals are never "
            "auto-applied; Captain reviews via PR if adopting suggestions."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }

    if write_evidence:
        out_root = Path(evidence_dir) if evidence_dir else (
            repo_root / ".agent" / "evidence" / "read-only-persistent-oversight"
        )
        runs_root = repo_root / ".agent" / "status" / "oversight-runs"
        out_root.mkdir(parents=True, exist_ok=True)
        runs_root.mkdir(parents=True, exist_ok=True)
        json_path = out_root / f"{run_id}.json"
        report["evidence_path"] = str(json_path)
        validate_document(report, "oversight-run.schema.json")
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        json_path.write_text(payload, encoding="utf-8")
        (runs_root / f"{run_id}.json").write_text(payload, encoding="utf-8")
        (out_root / "LATEST.json").write_text(
            json.dumps({"run_id": run_id, "path": str(json_path)}, indent=2) + "\n",
            encoding="utf-8",
        )
        md_lines = [
            "# Oversight Run Summary",
            "",
            f"- run_id: `{run_id}`",
            f"- overall_status: **{overall}**",
            f"- repository_sha: `{head}`",
            f"- brain_synced: `{brain_synced}`",
            f"- snapshot_id: `{snapshot_id}`",
            f"- proposal_id: `{proposal_id}`",
            f"- proposal_applied: `false`",
            "",
            "## Steps",
            "",
        ]
        for step in steps:
            md_lines.append(
                f"- `{step['id']}` — {step['status']}: {step['summary']}"
            )
        if warnings:
            md_lines.extend(["", "## Warnings", ""])
            for w in warnings:
                md_lines.append(f"- {w}")
        md_lines.append("")
        (out_root / "SUMMARY.md").write_text("\n".join(md_lines), encoding="utf-8")
    else:
        validate_document(report, "oversight-run.schema.json")

    return report
