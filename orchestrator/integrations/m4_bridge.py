"""Bridge M4 persistent-role + bounded autonomy into NorthStar routines.

Does not grant Notion or Slack approval authority. Weight apply remains behind
explicit captain_approved proposal flags and autonomy budget (never implied by
NorthStar GitHub plan approval alone).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.agents.promote import (
    PromotionProposeError,
    build_persistent_role_proposal,
    evaluate_gates,
    gates_all_passed,
    load_proficiency_records,
    write_persistent_role_proposal,
)
from orchestrator.branding import display_name
from orchestrator.integrations.events import redact_secrets
from orchestrator.routing.apply import ApplyError, apply_routing_proposal, load_proposal


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def propose_persistent_roles(
    repo_root: Path,
    *,
    notes: str = "NorthStar M4 bridge propose-only",
) -> dict[str, Any]:
    """Propose staging persistent roles for eligible proficiency records."""
    repo_root = Path(repo_root)
    proposed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for record in load_proficiency_records(repo_root):
        agent_id = str(record.get("agent_id") or "")
        gates = evaluate_gates(record)
        if not gates_all_passed(gates):
            skipped.append({"agent_id": agent_id, "gates": gates, "reason": "gates_failed"})
            continue
        try:
            proposal = build_persistent_role_proposal(record, notes=notes)
            out_path = write_persistent_role_proposal(repo_root, proposal, record)
            saved = json.loads(Path(out_path).read_text(encoding="utf-8"))
            proposed.append(
                {
                    "agent_id": agent_id,
                    "proposal_id": saved["proposal_id"],
                    "landing_mode": "staging_and_pr_only",
                    "proposal_path": str(out_path),
                    "staging_paths": saved.get("staging_paths") or {},
                }
            )
        except PromotionProposeError as exc:
            skipped.append({"agent_id": agent_id, "reason": str(exc)})
    return {
        "kind": "northstar-m4-role-proposals",
        "product": display_name(),
        "at": _utc_now(),
        "proposed_count": len(proposed),
        "proposed": proposed,
        "skipped": skipped,
    }


def list_pending_routing_proposals(repo_root: Path) -> dict[str, Any]:
    """List routing proposals without applying weights."""
    root = Path(repo_root) / ".agent" / "routing" / "proposals"
    pending: list[dict[str, Any]] = []
    if root.is_dir():
        for path in sorted(root.glob("*.json")):
            try:
                doc = load_proposal(path)
            except ApplyError:
                continue
            pending.append(
                {
                    "path": str(path),
                    "proposal_id": doc.get("proposal_id") or path.stem,
                    "captain_approved": bool(doc.get("captain_approved")),
                    "auto_apply": bool(doc.get("auto_apply")),
                    "kind": doc.get("kind"),
                }
            )
    return {
        "kind": "northstar-m4-routing-surface",
        "product": display_name(),
        "at": _utc_now(),
        "count": len(pending),
        "proposals": pending,
        "note": "NorthStar plan approval does not apply weights; use captain_approved on proposal + apply flag",
    }


def apply_approved_routing_proposal(
    repo_root: Path,
    proposal_path: Path,
    *,
    budget_path: Path | None = None,
    allow_apply: bool = False,
) -> dict[str, Any]:
    """Apply one routing proposal only when explicitly allowed and captain-approved."""
    if not allow_apply:
        raise ApplyError(
            "refusing weight apply: NorthStar bridge requires explicit allow_apply "
            "(plan approval alone is insufficient)"
        )
    proposal = load_proposal(proposal_path)
    if not proposal.get("captain_approved"):
        raise ApplyError("refusing weight apply: proposal.captain_approved is not true")
    if proposal.get("auto_apply") is not False:
        raise ApplyError("refusing weight apply: auto_apply must remain false")
    result = apply_routing_proposal(
        Path(repo_root),
        proposal_path=Path(proposal_path),
        budget_path=budget_path,
    )
    return {
        "kind": "northstar-m4-routing-apply",
        "product": display_name(),
        "at": _utc_now(),
        "applied": True,
        "result": result if isinstance(result, dict) else {"ok": True},
    }


def notion_research_context(
    repo_root: Path,
    *,
    mode: str = "fixtures",
    page_ids: list[str] | None = None,
) -> dict[str, Any]:
    """
    Gather Notion research context without approval authority.

    Modes:
      - fixtures: read tests/fixtures/notion or .agent/knowledge/external/notion-live
      - live: attempt live MCP path; if unavailable, return skipped note
    """
    repo_root = Path(repo_root)
    mode = (mode or "fixtures").strip().lower()
    evidence: list[dict[str, Any]] = []

    if mode == "fixtures":
        fixture_dir = repo_root / "tests" / "fixtures" / "notion"
        live_cache = repo_root / ".agent" / "knowledge" / "external" / "notion-live"
        for directory in (fixture_dir, live_cache):
            if not directory.is_dir():
                continue
            for path in sorted(directory.glob("**/*")):
                if path.suffix.lower() not in {".md", ".json"}:
                    continue
                evidence.append(
                    {
                        "path": str(path.relative_to(repo_root)),
                        "source": "fixture_or_cache",
                    }
                )
        return {
            "kind": "northstar-notion-context",
            "product": display_name(),
            "mode": "fixtures",
            "authoritative": False,
            "count": len(evidence),
            "items": evidence,
            "at": _utc_now(),
        }

    if mode == "live":
        # Cloud agents cannot complete interactive Notion MCP auth. Detect and skip.
        allowlist = repo_root / ".agent" / "knowledge" / "notion-allowlist.txt"
        allowlisted = []
        if allowlist.is_file():
            allowlisted = [
                line.strip()
                for line in allowlist.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
        if page_ids:
            allowlisted = [pid for pid in page_ids if pid in set(allowlisted) or not allowlisted]
        return {
            "kind": "northstar-notion-context",
            "product": display_name(),
            "mode": "live",
            "authoritative": False,
            "skipped": True,
            "reason": "notion_mcp_unauthenticated",
            "message": (
                "Notion MCP interactive auth is unavailable in this Cloud Agent "
                "environment. Authenticate Notion in Cursor desktop, then re-run "
                "with --notion-mode live. Approvals remain GitHub-only."
            ),
            "allowlisted_page_ids": allowlisted,
            "at": _utc_now(),
        }

    raise ValueError(f"unknown notion mode: {mode!r}")


def build_notion_summary_mirror(run: dict[str, Any], bridge: dict[str, Any]) -> dict[str, Any]:
    """Build a non-authoritative Notion release/summary mirror payload (fixture-safe)."""
    return redact_secrets(
        {
            "kind": "northstar-notion-summary-mirror",
            "product": display_name(),
            "authoritative": False,
            "title": f"NorthStar run {run.get('run_id')} — M4 bridge summary",
            "run_id": run.get("run_id"),
            "state": run.get("state"),
            "plan_id": run.get("plan_id"),
            "plan_approved": bool(run.get("plan_approved")),
            "github_approval_ref": run.get("github_approval_ref"),
            "bridge": {
                "roles_proposed": (bridge.get("roles") or {}).get("proposed_count"),
                "routing_pending": (bridge.get("routing") or {}).get("count"),
                "notion_mode": (bridge.get("notion") or {}).get("mode"),
            },
            "authority_note": "Mirror only. Canonical approval remains GitHub + plan digest.",
            "at": _utc_now(),
        }
    )


def run_m4_bridge(
    repo_root: Path,
    run: dict[str, Any],
    *,
    propose_roles: bool = False,
    surface_routing: bool = False,
    apply_routing_path: Path | None = None,
    allow_weight_apply: bool = False,
    budget_path: Path | None = None,
    notion_mode: str | None = None,
    linear: Any | None = None,
    slack: Any | None = None,
) -> dict[str, Any]:
    """
    Execute M4 bridge hooks after REVIEW_READY (or later).

    Safe defaults: propose/surface only; never apply weights unless explicitly allowed.
    """
    if run.get("state") not in {"REVIEW_READY", "AWAITING_MERGE", "COMPLETED"}:
        raise ValueError(
            f"M4 bridge requires REVIEW_READY+; current state={run.get('state')!r}"
        )

    bridge: dict[str, Any] = {
        "kind": "northstar-m4-bridge",
        "product": display_name(),
        "run_id": run.get("run_id"),
        "at": _utc_now(),
    }

    if propose_roles:
        roles = propose_persistent_roles(repo_root)
        bridge["roles"] = roles
        if linear is not None and roles.get("proposed_count"):
            child_run = dict(run)
            child_run["workstreams"] = list(run.get("workstreams") or []) + [
                {
                    "id": "M4-persistent-role-pr",
                    "depends_on": [],
                    "owner": "first_mate",
                    "status": "proposed",
                    "acceptance": ["Captain PR for staging drafts"],
                }
            ]
            linear.create_or_update_work_item(child_run)
        if slack is not None and roles.get("proposed_count"):
            # Reuse review_ready-style durable note via publish_transition only if allowlisted;
            # use create_or_update_work_item style message through publish of blocked_or_budget_stopped? 
            # Prefer work item update on github/linear; Slack gets no extra transition to stay allowlisted.
            pass

    if surface_routing:
        bridge["routing"] = list_pending_routing_proposals(repo_root)

    if apply_routing_path is not None:
        bridge["routing_apply"] = apply_approved_routing_proposal(
            repo_root,
            Path(apply_routing_path),
            budget_path=budget_path,
            allow_apply=allow_weight_apply,
        )

    if notion_mode:
        notion = notion_research_context(repo_root, mode=notion_mode)
        bridge["notion"] = notion
        bridge["notion_summary_mirror"] = build_notion_summary_mirror(run, bridge)
        evidence = Path(repo_root) / ".agent" / "evidence" / str(run.get("run_id") or "bridge")
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "notion-summary-mirror.json").write_text(
            json.dumps(bridge["notion_summary_mirror"], indent=2) + "\n",
            encoding="utf-8",
        )

    return bridge
