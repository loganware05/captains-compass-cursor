"""NorthStar B4 repair loop — FIND→PROVE→FIX→TEST→SUBMIT (hermetic MVP).

Never auto-merges. Dispatch to live agents requires explicit Captain authorization.
Default path is dry-run evidence only.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.integrations.events import redact_secrets
from orchestrator.integrations.product_allowlist import PRODUCT_DISPATCH_ALLOWLIST
from orchestrator.review.github_draft import (
    load_allowlist,
    resolve_allowlist_path,
    severity_meets_floor,
)
from orchestrator.review.outcomes import load_review_report
from orchestrator.routing.agent_router import (
    RouteObjective,
    decision_to_dict,
    load_registry,
    route_agents,
)
from orchestrator.routing.cloud_wakeability_probe import (
    build_cloud_wakeability_probe,
    load_cloud_agents_payload,
)

SCHEMA_VERSION = "northstar.repair_run.v1"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class RepairError(ValueError):
    """Raised when a repair run cannot proceed safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_id(value: str, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise RepairError(f"unsafe {label}: {value!r}")
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(redact_secrets(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def find_finding(report: dict[str, Any], finding_id: str) -> dict[str, Any]:
    for finding in report.get("findings") or []:
        if isinstance(finding, dict) and str(finding.get("id")) == finding_id:
            return finding
    raise RepairError(f"finding_id not in report: {finding_id!r}")


def prove_finding(
    finding: dict[str, Any],
    *,
    severity_floor: str = "medium",
) -> dict[str, Any]:
    """PROVE gate — refuse unverified / below-floor / evidence-less findings."""
    status = str(finding.get("status") or "").strip().lower()
    severity = str(finding.get("severity") or "info")
    evidence_paths = finding.get("evidence_paths") or []
    reasons: list[str] = []

    if status != "verified":
        reasons.append(f"finding status is {status!r}, require verified")
    if not severity_meets_floor(severity, severity_floor):
        reasons.append(
            f"severity {severity!r} below floor {severity_floor!r}"
        )
    if not isinstance(evidence_paths, list) or not evidence_paths:
        reasons.append("finding has no evidence_paths")

    ok = not reasons
    return {
        "ok": ok,
        "finding_id": finding.get("id"),
        "status": status,
        "severity": severity,
        "severity_floor": severity_floor,
        "evidence_paths": evidence_paths if isinstance(evidence_paths, list) else [],
        "reasons": reasons,
        "checked_at": _utc_now(),
    }


def build_repair_objective(
    *,
    report: dict[str, Any],
    finding: dict[str, Any],
    target_repository: str,
) -> dict[str, Any]:
    skill = str(finding.get("skill") or "code-reviewer")
    return {
        "title": (
            f"Repair verified finding {finding.get('id')}: {finding.get('title')}"
        ),
        "category": "repair",
        "target_repository": target_repository,
        "required_skills": ["review-fix-loop", skill, "testing-validation"],
        "skill_scope": "sandbox",
        "context_agent_id": None,
        "finding_id": finding.get("id"),
        "code_review_run_id": report.get("run_id"),
        "suggested_fix": finding.get("suggested_fix") or "",
    }


def build_fix_plan(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "repair-fix-plan",
        "finding_id": finding.get("id"),
        "title": finding.get("title"),
        "suggested_fix": finding.get("suggested_fix") or "",
        "files_hint": finding.get("evidence_paths") or [],
        "mode": "dry-run",
        "applied": False,
        "notes": (
            "Hermetic B4 MVP records the fix plan only. "
            "No product files are modified in dry-run."
        ),
        "created_at": _utc_now(),
    }


def build_test_plan(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "repair-test-plan",
        "finding_id": finding.get("id"),
        "commands": [
            "./scripts/doctor.sh",
            "PYTHONPATH=. python3 -m unittest tests.orchestrator.test_m32_repair_loop -v",
        ],
        "mode": "dry-run",
        "executed": False,
        "notes": "Record intended validation; hermetic default does not execute product tests.",
        "created_at": _utc_now(),
    }


def build_pr_metadata(
    *,
    finding: dict[str, Any],
    run_id: str,
    target_repository: str,
    prepare_pr: bool,
) -> dict[str, Any]:
    branch = f"cursor/repair-{finding.get('id')}-{run_id}"[:80]
    title = f"fix: address verified finding {finding.get('id')}"
    body = (
        f"## Finding\n\n"
        f"- id: `{finding.get('id')}`\n"
        f"- title: {finding.get('title')}\n"
        f"- severity: {finding.get('severity')}\n\n"
        f"## Suggested fix\n\n{finding.get('suggested_fix') or '(none)'}\n\n"
        f"## Rollback\n\nRevert this PR. Repair run id: `{run_id}`.\n\n"
        f"**auto_merge: false** — human review required.\n"
    )
    allowlisted = target_repository in PRODUCT_DISPATCH_ALLOWLIST
    return {
        "kind": "repair-pr-metadata",
        "draft": True,
        "auto_merge": False,
        "branch": branch,
        "title": title,
        "body": body,
        "base": "main",
        "target_repository": target_repository,
        "allowlisted": allowlisted,
        "prepare_pr_requested": prepare_pr,
        "created": False,
        "merged": False,
        "notes": (
            "Evidence-only by default. Even with --prepare-pr, this MVP never merges "
            "and only records draft PR metadata unless an allowlisted live path is later approved."
        ),
        "created_at": _utc_now(),
    }


def _route_dispatch(
    *,
    objective: dict[str, Any],
    registry_path: Path | None,
    cloud_agents_path: Path | None,
) -> dict[str, Any]:
    if registry_path is None or not Path(registry_path).is_file():
        return {
            "router_version": "northstar.agent_router.v1",
            "dispatch_ready": False,
            "selected_agent_id": None,
            "notes": "No agent registry provided; packet is informational only.",
            "objective": objective,
            "agents": [],
        }

    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    agents = load_registry(registry)
    route_obj = RouteObjective(
        title=str(objective["title"]),
        category=str(objective.get("category") or "repair"),
        target_repository=str(objective.get("target_repository") or ""),
        required_skills=list(objective.get("required_skills") or []),
        skill_scope=str(objective.get("skill_scope") or "sandbox"),
        context_agent_id=objective.get("context_agent_id"),
    )
    probe = None
    prefer_probe = False
    if cloud_agents_path and Path(cloud_agents_path).is_file():
        payload = json.loads(Path(cloud_agents_path).read_text(encoding="utf-8"))
        cloud_agents = load_cloud_agents_payload(payload)
        probe = build_cloud_wakeability_probe(cloud_agents)
        prefer_probe = True
    decision = route_agents(agents, route_obj, probe=probe, prefer_probe=prefer_probe)
    return decision_to_dict(decision)


def start_repair(
    *,
    repo_root: Path,
    report_path: Path,
    finding_id: str,
    severity_floor: str = "medium",
    target_repository: str = "",
    registry_path: Path | None = None,
    cloud_agents_path: Path | None = None,
    captain_approve_dispatch: bool = False,
    prepare_pr: bool = False,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Run FIND→PROVE→(plan FIX/TEST)→SUBMIT metadata. Never auto-merges."""
    root = Path(repo_root).resolve()
    report = load_review_report(report_path)
    finding = find_finding(report, finding_id)
    _safe_id(str(finding_id), "finding_id")

    review_run_id = str(report.get("run_id") or "unknown-run")
    _safe_id(review_run_id, "run_id")
    repair_run_id = f"repair-{review_run_id}-{finding_id}"[:120]
    _safe_id(repair_run_id.replace("/", "-"), "repair_run_id")

    out_dir = root / ".agent" / "evidence" / "repair" / repair_run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    repo_slug = (
        target_repository.strip()
        or str(report.get("repository") or "")
        or "loganware05/captain-compass-sandbox"
    )

    intake = {
        "schema_version": SCHEMA_VERSION,
        "repair_run_id": repair_run_id,
        "code_review_run_id": review_run_id,
        "finding_id": finding_id,
        "report_path": str(report_path),
        "repository": repo_slug,
        "dry_run": dry_run,
        "captain_approve_dispatch": bool(captain_approve_dispatch),
        "prepare_pr": bool(prepare_pr),
        "auto_merge": False,
        "created_at": _utc_now(),
    }
    _write_json(out_dir / "intake.json", intake)

    prove = prove_finding(finding, severity_floor=severity_floor)
    _write_json(out_dir / "prove.json", prove)
    if not prove["ok"]:
        summary = {
            "repair_run_id": repair_run_id,
            "ok": False,
            "stage": "prove",
            "reasons": prove["reasons"],
            "evidence_dir": str(out_dir),
            "auto_merge": False,
            "captain_approval": False,
        }
        _write_json(out_dir / "result.json", summary)
        raise RepairError("; ".join(prove["reasons"]))

    # Allowlist awareness (sandbox first) — refuse prepare_pr for non-allowlisted.
    allowlist_path = resolve_allowlist_path(root)
    allowlist = load_allowlist(allowlist_path)
    github_allowlisted = any(
        str(r.get("repo") if isinstance(r, dict) else r) == repo_slug
        for r in (allowlist.get("repos") or [])
    )
    product_allowlisted = repo_slug in PRODUCT_DISPATCH_ALLOWLIST

    objective = build_repair_objective(
        report=report,
        finding=finding,
        target_repository=repo_slug,
    )
    _write_json(out_dir / "objective.json", objective)

    dispatch = _route_dispatch(
        objective=objective,
        registry_path=registry_path,
        cloud_agents_path=cloud_agents_path,
    )
    dispatch_authorized = bool(
        captain_approve_dispatch and dispatch.get("dispatch_ready")
    )
    packet = {
        "kind": "northstar-repair-dispatch-packet",
        "repair_run_id": repair_run_id,
        "dispatch_authorized": dispatch_authorized,
        "captain_approve_dispatch": bool(captain_approve_dispatch),
        "live_dispatch_invoked": False,
        "routing": dispatch,
        "created_at": _utc_now(),
        "notes": (
            "Packet written for Captain review. Live Cursor dispatch is never invoked "
            "on the hermetic default path."
        ),
    }
    _write_json(out_dir / "dispatch-packet.json", packet)

    fix_plan = build_fix_plan(finding)
    test_plan = build_test_plan(finding)
    _write_json(out_dir / "fix-plan.json", fix_plan)
    _write_json(out_dir / "test-plan.json", test_plan)

    if prepare_pr and not (product_allowlisted or github_allowlisted):
        raise RepairError(
            f"prepare_pr refused: repository not allowlisted: {repo_slug!r}"
        )

    pr_meta = build_pr_metadata(
        finding=finding,
        run_id=repair_run_id,
        target_repository=repo_slug,
        prepare_pr=prepare_pr,
    )
    # Hard lock: never mark merged; never create real PR in hermetic MVP.
    pr_meta["created"] = False
    pr_meta["merged"] = False
    pr_meta["auto_merge"] = False
    _write_json(out_dir / "pr-metadata.json", pr_meta)

    summary_md = (
        f"# Repair run `{repair_run_id}`\n\n"
        f"- Finding: `{finding_id}` ({finding.get('severity')}, {finding.get('status')})\n"
        f"- PROVE: ok\n"
        f"- Dispatch authorized: `{dispatch_authorized}`\n"
        f"- Draft PR metadata written; auto_merge=false; merged=false\n"
        f"- Dry-run: `{dry_run}`\n"
    )
    (out_dir / "SUMMARY.md").write_text(summary_md, encoding="utf-8")

    result = {
        "ok": True,
        "repair_run_id": repair_run_id,
        "evidence_dir": str(out_dir),
        "finding_id": finding_id,
        "dispatch_authorized": dispatch_authorized,
        "dispatch_ready": bool(dispatch.get("dispatch_ready")),
        "prepare_pr": bool(prepare_pr),
        "pr_created": False,
        "merged": False,
        "auto_merge": False,
        "dry_run": dry_run,
        "captain_approval": False,
        "stage": "submit-metadata",
    }
    _write_json(out_dir / "result.json", result)
    return result
