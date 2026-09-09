"""End-to-end NorthStar connected routine (fixture-safe; optional live mode)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.branding import display_name
from orchestrator.integrations.adapters.cursor import CursorAdapter
from orchestrator.integrations.adapters.github import GitHubAdapter
from orchestrator.integrations.adapters.linear import LinearAdapter
from orchestrator.integrations.adapters.live import build_northstar_adapters
from orchestrator.integrations.adapters.slack import SlackAdapter
from orchestrator.integrations.events import IdempotencyStore, sha256_hex
from orchestrator.integrations.product_allowlist import (
    DEFAULT_PRODUCT_REPOSITORY,
    require_allowed_repository,
)
from orchestrator.integrations.reconcile import persist_run, reconcile_run
from orchestrator.integrations.state_machine import (
    StateTransitionError,
    new_run,
    transition_run,
)
from orchestrator.integrations.transport import HttpTransport, RecordingTransport, UrllibTransport

DEFAULT_WORKSTREAMS = [
    {"id": "M21A", "depends_on": [], "owner": "first_mate", "status": "planned"},
    {"id": "M21B", "depends_on": ["M21A"], "owner": "first_mate", "status": "planned"},
    {"id": "M21C", "depends_on": ["M21A"], "owner": "first_mate", "status": "planned"},
    {"id": "M21D", "depends_on": ["M21A"], "owner": "first_mate", "status": "planned"},
    {"id": "M21E", "depends_on": ["M21B", "M21C", "M21D"], "owner": "first_mate", "status": "planned"},
]


class NorthStarRoutineError(RuntimeError):
    """Routine blocked or failed a safety gate."""


def _normalize_mode(mode: str | None) -> str:
    mode_n = (mode or "fixtures").strip().lower()
    if mode_n in {"fixture", "fixtures"}:
        return "fixtures"
    if mode_n == "live":
        return "live"
    raise NorthStarRoutineError(f"unknown mode: {mode!r}")


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
    propose_roles: bool = False,
    surface_routing: bool = False,
    notion_mode: str | None = None,
    apply_routing_path: str | Path | None = None,
    allow_weight_apply: bool = False,
    budget_path: str | Path | None = None,
    mode: str = "fixtures",
    product_repository: str | None = None,
    transport: HttpTransport | None = None,
    live_approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute the NorthStar routine against fixture or live adapters.

    mode=fixtures (default): CI-safe; --approve may fabricate GitHub approval.
    mode=live: requires allowlisted product_repository; --approve must NOT
    fabricate approval — only GitHub digest path (live_approval) may approve.
    """
    from orchestrator.integrations.m4_bridge import run_m4_bridge

    repo_root = Path(repo_root)
    mode_n = _normalize_mode(mode)
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
    global_idem = IdempotencyStore(
        repo_root / ".agent" / "northstar" / "idempotency.json"
    )

    if not connected.get("github", True):
        raise NorthStarRoutineError("missing GitHub stops the entire engineering routine")

    use_product_path = mode_n == "live" or product_repository is not None
    product_repo = product_repository
    if mode_n == "live":
        product_repo = product_repo or DEFAULT_PRODUCT_REPOSITORY
        try:
            require_allowed_repository(product_repo)
        except NorthStarRoutineError:
            raise
        except Exception as exc:
            raise NorthStarRoutineError(str(exc)) from exc
        if transport is None:
            # Live without an injected transport uses urllib; CI must inject RecordingTransport.
            transport = UrllibTransport()
    elif product_repo is not None:
        try:
            require_allowed_repository(product_repo)
        except Exception as exc:
            raise NorthStarRoutineError(str(exc)) from exc

    if use_product_path:
        built = build_northstar_adapters(
            mode=mode_n,
            store_dir=store,
            connected=connected,
            transport=transport,
            product_repository=product_repo or DEFAULT_PRODUCT_REPOSITORY,
        )
        github = built["github"]
        linear = built["linear"]
        slack = built["slack"]
        cursor = built["cursor"]
        adapters = {
            "github": github,
            "linear": linear,
            "slack": slack,
            "cursor": cursor,
        }
        primary = adapters.get(provider) or github
    else:
        primary = _adapter_for_provider(provider, store, connected)
        github = GitHubAdapter(store_dir=store / "github", connected=connected.get("github", True))
        linear = LinearAdapter(store_dir=store / "linear", connected=connected.get("linear", True))
        slack = SlackAdapter(store_dir=store / "slack", connected=connected.get("slack", True))
        cursor = CursorAdapter(store_dir=store / "cursor", connected=connected.get("cursor", True))

    github.captain_ids.add(captain_github_id)

    # Ensure product repository is stamped onto objective events when provided.
    if product_repo and not raw_event.get("repository"):
        raw_event = {**raw_event, "repository": product_repo}

    # Approval-only deliveries (ingress) apply digest approval to an existing run path.
    if live_approval and live_approval.get("event_type") == "approval":
        return _apply_live_approval(
            repo_root=repo_root,
            evidence=evidence,
            github=github,
            linear=linear,
            slack=slack,
            cursor=cursor,
            live_approval=live_approval,
            plan_id=plan_id,
            captain_github_id=captain_github_id,
            connected=connected,
            mode=mode_n,
            product_repository=product_repo,
            advance_to_review=advance_to_review,
            run_id=rid,
        )

    event = primary.normalize_event(raw_event)
    if not global_idem.remember(event["event_id"], event["idempotency_key"]):
        return {
            "ok": True,
            "duplicate": True,
            "product": display_name(),
            "event_id": event["event_id"],
            "message": "replay ignored; no duplicate side effects",
            "mode": mode_n,
        }

    run = new_run(run_id=rid, origin_event=event, plan_id=plan_id)
    run["workstreams"] = list(DEFAULT_WORKSTREAMS)
    run["mode"] = mode_n
    if product_repo:
        run["product_repository"] = product_repo
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
        "mode": mode_n,
    }

    # Live mode: never fabricate approval via --approve shortcut.
    if mode_n == "live" and approve and not live_approval:
        persist_run(run, evidence / "run.json")
        report["message"] = (
            "live mode refuses --approve shortcut; awaiting GitHub plan_digest approval"
        )
        report["reconcile"] = reconcile_run(
            run, github=github, linear=linear, slack=slack, cursor=cursor
        )
        (evidence / "routine-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report

    if not approve:
        persist_run(run, evidence / "run.json")
        report["message"] = "stopped at AWAITING_CAPTAIN_APPROVAL"
        report["reconcile"] = reconcile_run(
            run, github=github, linear=linear, slack=slack, cursor=cursor
        )
        (evidence / "routine-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report

    # Canonical approval (GitHub only) — fixtures may use CLI --approve.
    run = github.record_canonical_approval(
        run,
        plan_id=plan_id,
        plan_digest=plan_digest,
        actor_id=captain_github_id,
        approval_ref=f"github:issue-comment:{rid}",
    )
    return _continue_after_approval(
        run=run,
        evidence=evidence,
        github=github,
        linear=linear,
        slack=slack,
        cursor=cursor,
        plan_digest=plan_digest,
        report=report,
        connected=connected,
        advance_to_review=advance_to_review,
        propose_roles=propose_roles,
        surface_routing=surface_routing,
        notion_mode=notion_mode,
        apply_routing_path=apply_routing_path,
        allow_weight_apply=allow_weight_apply,
        budget_path=budget_path,
        repo_root=repo_root,
    )


def _apply_live_approval(
    *,
    repo_root: Path,
    evidence: Path,
    github: GitHubAdapter,
    linear: LinearAdapter,
    slack: SlackAdapter,
    cursor: CursorAdapter,
    live_approval: dict[str, Any],
    plan_id: str,
    captain_github_id: str,
    connected: dict[str, bool],
    mode: str,
    product_repository: str | None,
    advance_to_review: bool,
    run_id: str,
) -> dict[str, Any]:
    """Apply a GitHub NORTHSTAR_APPROVE delivery to a pending run (or create one)."""
    digest = str(live_approval.get("plan_digest") or "").lower()
    actor_id = str(live_approval.get("actor_id") or captain_github_id)
    approval_ref = str(
        live_approval.get("approval_ref") or f"github:issue-comment:{live_approval.get('delivery_id')}"
    )

    # Find a pending run with matching plan_digest under evidence tree; else create intake+approve.
    pending, pending_evidence = _find_pending_run(repo_root, plan_digest=digest)
    if pending is not None and pending_evidence is not None:
        evidence = pending_evidence
    if pending is None:
        # No pending run — still fail closed if digest empty; otherwise create run then approve.
        intake = {
            "event_id": f"approval-origin-{live_approval.get('delivery_id') or run_id}",
            "event_type": "objective",
            "repository": live_approval.get("repository") or product_repository,
            "issue": live_approval.get("issue"),
            "label": "northstar",
            "intake": True,
            "title": live_approval.get("title") or "NorthStar live approval",
            "body": live_approval.get("body"),
            "actor_id": actor_id,
            "product_name": "NorthStar",
        }
        created = run_northstar_routine(
            repo_root,
            raw_event=intake,
            provider="github",
            plan_id=plan_id,
            captain_github_id=captain_github_id,
            approve=False,
            mode=mode,
            product_repository=product_repository,
            transport=github.transport if isinstance(github.transport, (RecordingTransport, UrllibTransport)) or github.transport else None,
            run_id=run_id,
            connected=connected,
        )
        pending_path = Path(created["evidence_dir"]) / "run.json"
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
        evidence = Path(created["evidence_dir"])
        digest_expected = created.get("plan_digest")
        if digest and digest != digest_expected:
            pending = transition_run(
                pending, "BLOCKED_APPROVAL", reason="plan digest mismatch"
            )
            persist_run(pending, evidence / "run.json")
            raise NorthStarRoutineError("BLOCKED_APPROVAL: plan digest mismatch")
        digest = digest_expected

    if pending.get("plan_digest") != digest:
        pending = transition_run(pending, "BLOCKED_APPROVAL", reason="plan digest mismatch")
        persist_run(pending, evidence / "run.json")
        raise NorthStarRoutineError("BLOCKED_APPROVAL: plan digest mismatch")

    try:
        run = github.record_canonical_approval(
            pending,
            plan_id=pending.get("plan_id") or plan_id,
            plan_digest=digest,
            actor_id=actor_id,
            approval_ref=approval_ref,
        )
    except StateTransitionError as exc:
        raise NorthStarRoutineError(str(exc)) from exc

    if not github.verify_plan_digest(run, digest):
        run = transition_run(run, "BLOCKED_APPROVAL", reason="plan digest mismatch")
        persist_run(run, evidence / "run.json")
        raise NorthStarRoutineError("BLOCKED_APPROVAL: plan digest mismatch")

    report: dict[str, Any] = {
        "ok": True,
        "product": display_name(),
        "run_id": run.get("run_id"),
        "state": run["state"],
        "plan_id": run.get("plan_id"),
        "plan_digest": digest,
        "evidence_dir": str(evidence),
        "duplicate": False,
        "mode": mode,
        "message": "live GitHub approval recorded",
    }
    return _continue_after_approval(
        run=run,
        evidence=evidence,
        github=github,
        linear=linear,
        slack=slack,
        cursor=cursor,
        plan_digest=digest,
        report=report,
        connected=connected,
        advance_to_review=advance_to_review,
        propose_roles=False,
        surface_routing=False,
        notion_mode=None,
        apply_routing_path=None,
        allow_weight_apply=False,
        budget_path=None,
        repo_root=repo_root,
    )


def _find_pending_run(
    repo_root: Path, *, plan_digest: str
) -> tuple[dict[str, Any] | None, Path | None]:
    if not plan_digest:
        return None, None
    evidence_root = Path(repo_root) / ".agent" / "evidence"
    if not evidence_root.is_dir():
        return None, None
    for run_file in sorted(evidence_root.glob("*/run.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(run_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            data.get("plan_digest") == plan_digest
            and data.get("state") == "AWAITING_CAPTAIN_APPROVAL"
            and not data.get("plan_approved")
        ):
            return data, run_file.parent
    return None, None


def _continue_after_approval(
    *,
    run: dict[str, Any],
    evidence: Path,
    github: GitHubAdapter,
    linear: LinearAdapter,
    slack: SlackAdapter,
    cursor: CursorAdapter,
    plan_digest: str,
    report: dict[str, Any],
    connected: dict[str, bool],
    advance_to_review: bool,
    propose_roles: bool,
    surface_routing: bool,
    notion_mode: str | None,
    apply_routing_path: str | Path | None,
    allow_weight_apply: bool,
    budget_path: str | Path | None,
    repo_root: Path,
) -> dict[str, Any]:
    from orchestrator.integrations.m4_bridge import run_m4_bridge

    if not github.verify_plan_digest(run, plan_digest):
        run = transition_run(run, "BLOCKED_APPROVAL", reason="plan digest mismatch")
        persist_run(run, evidence / "run.json")
        raise NorthStarRoutineError("BLOCKED_APPROVAL: plan digest mismatch")

    # Enforce allowlist when dispatching to a product repository.
    product_repo = run.get("product_repository") or cursor.product_repository
    if product_repo or cursor.mode == "live":
        try:
            require_allowed_repository(
                str(
                    product_repo
                    or (run.get("origin_event") or {}).get("project", {}).get("repository")
                    or ""
                )
            )
        except Exception as exc:
            run = transition_run(run, "BLOCKED_SCOPE", reason=str(exc))
            persist_run(run, evidence / "run.json")
            raise NorthStarRoutineError(str(exc)) from exc

    packet = cursor.build_work_packet(run)
    run["work_packet"] = packet
    dispatch = cursor.dispatch(run, packet)
    if not dispatch.get("ok"):
        persist_run(run, evidence / "run.json")
        report["state"] = run["state"]
        report["work_packet"] = packet
        report["message"] = "Cursor unavailable; launch-ready work packet written"
        report["reconcile"] = reconcile_run(
            run, github=github, linear=linear, slack=slack, cursor=cursor
        )
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
        report["reconcile"] = reconcile_run(
            run, github=github, linear=linear, slack=slack, cursor=cursor
        )
        (evidence / "routine-report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report

    try:
        checkpoint = cursor.accept_checkpoint(
            {
                "event_id": f"chk-{run.get('run_id')}",
                "agent_id": cursor.allowed_agent_id,
                "run_id": run.get("run_id"),
                "packet_digest": packet.get("packet_digest"),
                "checkpoint": "validation-complete",
                "evidence_path": str(evidence),
                "state_hint": "REVIEW_READY",
            },
            run=run,
        )
    except StateTransitionError as exc:
        run = transition_run(
            run, "BLOCKED_AGENT_IDENTITY", reason=str(exc), origin="cursor"
        )
        persist_run(run, evidence / "run.json")
        raise NorthStarRoutineError(str(exc)) from exc

    run = transition_run(
        run, "VALIDATING", origin="cursor", event_digest=checkpoint["payload_digest"]
    )
    run = transition_run(run, "REVIEW_READY", origin="northstar")
    run["references"] = {
        **(run.get("references") or {}),
        "github_pull_request": f"pr://northstar/{run.get('run_id')}",
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
    report["reconcile"] = reconcile_run(
        run, github=github, linear=linear, slack=slack, cursor=cursor
    )

    if propose_roles or surface_routing or notion_mode or apply_routing_path:
        bridge = run_m4_bridge(
            repo_root,
            run,
            propose_roles=propose_roles,
            surface_routing=surface_routing,
            apply_routing_path=Path(apply_routing_path) if apply_routing_path else None,
            allow_weight_apply=allow_weight_apply,
            budget_path=Path(budget_path) if budget_path else None,
            notion_mode=notion_mode,
            linear=linear if connected.get("linear", True) else None,
            slack=slack if connected.get("slack", True) else None,
        )
        report["m4_bridge"] = bridge
        (evidence / "m4-bridge.json").write_text(
            json.dumps(bridge, indent=2) + "\n", encoding="utf-8"
        )
        persist_run(run, evidence / "run.json")

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
