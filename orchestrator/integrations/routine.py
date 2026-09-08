"""End-to-end NorthStar connected routine (fixture-safe)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.branding import display_name
from orchestrator.integrations.adapters.cursor import CursorAdapter
from orchestrator.integrations.adapters.github import GitHubAdapter
from orchestrator.integrations.adapters.linear import LinearAdapter
from orchestrator.integrations.adapters.slack import SlackAdapter
from orchestrator.integrations.events import sha256_hex
from orchestrator.integrations.reconcile import persist_run, reconcile_run
from orchestrator.integrations.state_machine import (
    StateTransitionError,
    new_run,
    transition_run,
)

DEFAULT_WORKSTREAMS = [
    {"id": "M21A", "depends_on": [], "owner": "first_mate", "status": "planned"},
    {"id": "M21B", "depends_on": ["M21A"], "owner": "first_mate", "status": "planned"},
    {"id": "M21C", "depends_on": ["M21A"], "owner": "first_mate", "status": "planned"},
    {"id": "M21D", "depends_on": ["M21A"], "owner": "first_mate", "status": "planned"},
    {"id": "M21E", "depends_on": ["M21B", "M21C", "M21D"], "owner": "first_mate", "status": "planned"},
]


class NorthStarRoutineError(RuntimeError):
    """Routine blocked or failed a safety gate."""


def _adapter_for_provider(provider: str, store: Path, connected: dict[str, bool]) -> Any:
    common = {"store_dir": store / provider, "connected": connected.get(provider, True)}
    if provider == "slack":
        return SlackAdapter(**common)
    if provider == "linear":
        return LinearAdapter(**common)
    if provider == "github":
        return GitHubAdapter(**common)
    if provider == "cursor":
        return CursorAdapter(**common)
    raise NorthStarRoutineError(f"unknown provider: {provider}")


def run_northstar_routine(
    repo_root: Path,
    *,
    raw_event: dict[str, Any],
    provider: str,
    plan_id: str = "m21-northstar-connected-operations",
    captain_github_id: str = "captain-github",
    approve: bool = False,
    advance_to_review: bool = False,
    connected: dict[str, bool] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """
    Execute the NorthStar routine against fixture adapters.

    When approve=False, stops at AWAITING_CAPTAIN_APPROVAL.
    When approve=True, records canonical GitHub approval and may dispatch.
    When advance_to_review=True (and approve), drives fixture execution to REVIEW_READY.
    """
    repo_root = Path(repo_root)
    connected = connected or {
        "slack": True,
        "linear": True,
        "github": True,
        "cursor": True,
    }
    rid = run_id or f"ns-{uuid4().hex[:10]}"
    evidence = repo_root / ".agent" / "evidence" / rid
    evidence.mkdir(parents=True, exist_ok=True)
    store = evidence / "connectors"
    store.mkdir(parents=True, exist_ok=True)

    if not connected.get("github", True):
        raise NorthStarRoutineError("missing GitHub stops the entire engineering routine")

    primary = _adapter_for_provider(provider, store, connected)
    github = GitHubAdapter(store_dir=store / "github", connected=connected.get("github", True))
    # Ensure captain id used for approval is recognized.
    github.captain_ids.add(captain_github_id)
    linear = LinearAdapter(store_dir=store / "linear", connected=connected.get("linear", True))
    slack = SlackAdapter(store_dir=store / "slack", connected=connected.get("slack", True))
    cursor = CursorAdapter(store_dir=store / "cursor", connected=connected.get("cursor", True))

    event = primary.normalize_event(raw_event)
    if not primary.deduplicate(event["event_id"], event["idempotency_key"]):
        return {
            "ok": True,
            "duplicate": True,
            "product": display_name(),
            "event_id": event["event_id"],
            "message": "replay ignored; no duplicate side effects",
        }

    run = new_run(run_id=rid, origin_event=event, plan_id=plan_id)
    run["workstreams"] = list(DEFAULT_WORKSTREAMS)
    run = transition_run(run, "RECONCILING", origin=provider)
    run = transition_run(run, "PLAN_PROPOSED", origin="northstar")
    plan_body = {
        "plan_id": plan_id,
        "product": display_name(),
        "objective": (event.get("payload") or {}).get("title")
        or (event.get("payload") or {}).get("text")
        or "NorthStar objective",
        "workstreams": run["workstreams"],
    }
    plan_digest = sha256_hex(plan_body)
    run["plan_digest"] = plan_digest
    run = transition_run(
        run,
        "AWAITING_CAPTAIN_APPROVAL",
        origin="northstar",
        plan_digest=plan_digest,
    )

    github.create_or_update_work_item(run)
    linear.create_or_update_work_item(run)
    if connected.get("slack", True):
        slack.publish_transition(run, "work_received")
        slack.publish_transition(run, "plan_awaiting_approval")

    report: dict[str, Any] = {
        "ok": True,
        "product": display_name(),
        "run_id": rid,
        "state": run["state"],
        "plan_id": plan_id,
        "plan_digest": plan_digest,
        "evidence_dir": str(evidence),
        "duplicate": False,
    }

    if not approve:
        persist_run(run, evidence / "run.json")
        report["message"] = "stopped at AWAITING_CAPTAIN_APPROVAL"
        report["reconcile"] = reconcile_run(run, github=github, linear=linear, slack=slack, cursor=cursor)
        (evidence / "routine-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report

    # Canonical approval (GitHub only).
    run = github.record_canonical_approval(
        run,
        plan_id=plan_id,
        plan_digest=plan_digest,
        actor_id=captain_github_id,
        approval_ref=f"github:issue-comment:{rid}",
    )
    if not github.verify_plan_digest(run, plan_digest):
        run = transition_run(run, "BLOCKED_APPROVAL", reason="plan digest mismatch")
        persist_run(run, evidence / "run.json")
        raise NorthStarRoutineError("BLOCKED_APPROVAL: plan digest mismatch")

    packet = cursor.build_work_packet(run)
    run["work_packet"] = packet
    dispatch = cursor.dispatch(run, packet)
    if not dispatch.get("ok"):
        persist_run(run, evidence / "run.json")
        report["state"] = run["state"]
        report["work_packet"] = packet
        report["message"] = "Cursor unavailable; launch-ready work packet written"
        report["reconcile"] = reconcile_run(run, github=github, linear=linear, slack=slack, cursor=cursor)
        (evidence / "routine-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report

    run = transition_run(run, "DISPATCHED", origin="cursor")
    run = transition_run(run, "IN_PROGRESS", origin="cursor")
    if connected.get("slack", True):
        slack.publish_transition(run, "execution_started")

    if not advance_to_review:
        persist_run(run, evidence / "run.json")
        report["state"] = run["state"]
        report["work_packet"] = packet
        report["message"] = "execution started"
        report["reconcile"] = reconcile_run(run, github=github, linear=linear, slack=slack, cursor=cursor)
        (evidence / "routine-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report

    # Fixture checkpoint from the allowed agent only.
    try:
        checkpoint = cursor.accept_checkpoint(
            {
                "event_id": f"chk-{rid}",
                "agent_id": cursor.allowed_agent_id,
                "checkpoint": "validation-complete",
                "evidence_path": str(evidence),
                "state_hint": "REVIEW_READY",
            }
        )
    except StateTransitionError as exc:
        run = transition_run(
            run, "BLOCKED_AGENT_IDENTITY", reason=str(exc), origin="cursor"
        )
        persist_run(run, evidence / "run.json")
        raise NorthStarRoutineError(str(exc)) from exc

    run = transition_run(run, "VALIDATING", origin="cursor", event_digest=checkpoint["payload_digest"])
    run = transition_run(run, "REVIEW_READY", origin="northstar")
    run["references"] = {
        **(run.get("references") or {}),
        "github_pull_request": f"pr://northstar/{rid}",
    }
    github.link_artifacts(run)
    linear.reconcile(run)
    if connected.get("slack", True):
        slack.publish_transition(run, "review_ready")

    persist_run(run, evidence / "run.json")
    report["state"] = run["state"]
    report["work_packet"] = packet
    report["checkpoint"] = checkpoint["event_id"]
    report["message"] = "fixture run reached REVIEW_READY"
    report["reconcile"] = reconcile_run(run, github=github, linear=linear, slack=slack, cursor=cursor)
    (evidence / "routine-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def reconcile_northstar_run(run_path: Path, repo_root: Path | None = None) -> dict[str, Any]:
    """Reload a persisted run and re-reconcile fixture connectors."""
    from orchestrator.integrations.reconcile import load_run

    run = load_run(run_path)
    evidence = Path(run_path).parent
    store = evidence / "connectors"
    github = GitHubAdapter(store_dir=store / "github")
    linear = LinearAdapter(store_dir=store / "linear")
    slack = SlackAdapter(store_dir=store / "slack")
    cursor = CursorAdapter(store_dir=store / "cursor")
    result = reconcile_run(run, github=github, linear=linear, slack=slack, cursor=cursor)
    out = evidence / "reconcile.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
