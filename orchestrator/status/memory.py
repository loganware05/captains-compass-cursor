"""Durable Overseer artifacts under .agent/status/ (M52). Never touches PROJECT_CONTEXT."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import ValidationError, validate_document
from orchestrator.status.store import StatusStoreError, ensure_layout, status_root


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _claim_for_finding(finding: dict[str, Any]) -> str:
    return str(finding.get("claim_kind") or "observed")


def build_scope_ledger(snapshot: dict[str, Any]) -> dict[str, Any]:
    entries = []
    for finding in snapshot.get("findings") or []:
        if not isinstance(finding, dict):
            continue
        entries.append(
            {
                "entry_id": str(finding.get("finding_id") or "unknown"),
                "claim_kind": _claim_for_finding(finding),
                "summary": str(finding.get("summary") or ""),
                "severity": str(finding.get("severity") or "info"),
                "kind": str(finding.get("kind") or "unknown"),
            }
        )
    return {
        "schema_version": "1",
        "created_at": _utc_now(),
        "snapshot_id": str(snapshot.get("snapshot_id") or ""),
        "repository_sha": str(snapshot.get("repository_sha") or ""),
        "northstar_version": str(snapshot.get("northstar_version") or ""),
        "entries": entries,
        "canonical_memory_untouched": True,
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def render_system_map(snapshot: dict[str, Any]) -> str:
    findings = snapshot.get("findings") or []
    lines = [
        "# Project Overseer system map (generated)",
        "",
        "> Non-canonical Overseer artifact under `.agent/status/`.",
        "> Does **not** replace `PROJECT_CONTEXT.md`, ADRs, or `PROGRESS.md`.",
        "",
        f"- Snapshot: `{snapshot.get('snapshot_id') or ''}`",
        f"- NorthStar version (observed): `{snapshot.get('northstar_version') or ''}`",
        f"- Repository SHA (observed): `{snapshot.get('repository_sha') or ''}`",
        f"- Plan ID (documented): `{snapshot.get('active_plan_id') or ''}`",
        f"- Plan status (documented): `{snapshot.get('plan_status') or ''}`",
        f"- Skills on disk (observed): `{snapshot.get('skill_count_fs')}`",
        f"- Skills in docs (documented): `{snapshot.get('skill_count_docs')}`",
        f"- Provenance refs (observed): `{len(snapshot.get('provenance_refs') or [])}`",
        f"- Incident refs (external): `{len(snapshot.get('incident_refs') or [])}`",
        f"- Conversation refs (external): `{len(snapshot.get('conversation_refs') or [])}`",
        f"- Execution refs (observed): `{len(snapshot.get('execution_refs') or [])}`",
        f"- Research refs (external): `{len(snapshot.get('research_refs') or [])}`",
        f"- Explainer refs (external): `{len(snapshot.get('explainer_refs') or [])}`",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("- (none)")
    else:
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            claim = _claim_for_finding(finding)
            lines.append(
                f"- [{finding.get('severity')}/{claim}] "
                f"{finding.get('summary')}"
            )
    incident_refs = snapshot.get("incident_refs") or []
    conversation_refs = snapshot.get("conversation_refs") or []
    execution_refs = snapshot.get("execution_refs") or []
    research_refs = snapshot.get("research_refs") or []
    explainer_refs = snapshot.get("explainer_refs") or []
    lines.extend(["", "## Development evidence", ""])
    if (
        not incident_refs
        and not conversation_refs
        and not execution_refs
        and not research_refs
        and not explainer_refs
    ):
        lines.append(
            "- (none observed under `.agent/incidents` / "
            "`.agent/conversations` / `.agent/executions/t3` / "
            "`.agent/research/apify` / `.agent/explainers`)"
        )
    else:
        for ref in incident_refs[:10]:
            if not isinstance(ref, dict):
                continue
            lines.append(
                f"- [incident/{ref.get('severity') or 'unknown'}] "
                f"`{ref.get('packet_id')}` — {ref.get('title') or ''}"
            )
        for ref in conversation_refs[:10]:
            if not isinstance(ref, dict):
                continue
            lines.append(
                f"- [conversation/{ref.get('model_or_source') or 'external'}] "
                f"`{ref.get('trajectory_id')}`"
            )
        for ref in execution_refs[:10]:
            if not isinstance(ref, dict):
                continue
            lines.append(
                f"- [t3/{ref.get('status') or 'unknown'}] "
                f"`{ref.get('execution_id')}` plan=`{ref.get('plan_id') or ''}`"
            )
        for ref in research_refs[:10]:
            if not isinstance(ref, dict):
                continue
            lines.append(
                f"- [apify/{ref.get('mode') or 'external'}] "
                f"`{ref.get('packet_id')}` query=`{ref.get('query') or ''}`"
            )
        for ref in explainer_refs[:10]:
            if not isinstance(ref, dict):
                continue
            lines.append(
                f"- [scrimba/{ref.get('mode') or 'external'}] "
                f"`{ref.get('packet_id')}` topic=`{ref.get('topic') or ''}`"
            )
    lines.extend(
        [
            "",
            "## Authority",
            "",
            "- `approved_for_execution`: false",
            "- `authority_mutation`: false",
            "- Reconcile proposals remain proposal-only.",
            "- Incident/conversation/research/explainer refs are external; "
            "T3 refs are observed.",
            "",
        ]
    )
    return "\n".join(lines)


def write_overseer_memory(repo_root: Path, snapshot: dict[str, Any]) -> dict[str, str]:
    """Write system-map.md + scope-ledger.json under .agent/status/ only."""
    ensure_layout(repo_root)
    root = status_root(repo_root)
    ledger = build_scope_ledger(snapshot)
    try:
        validate_document(ledger, "scope-ledger.schema.json")
    except ValidationError as exc:
        raise StatusStoreError(str(exc)) from exc
    map_path = root / "system-map.md"
    ledger_path = root / "scope-ledger.json"
    map_path.write_text(render_system_map(snapshot), encoding="utf-8")
    tmp = ledger_path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(ledger, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(ledger_path)
    return {"system_map": str(map_path), "scope_ledger": str(ledger_path)}
