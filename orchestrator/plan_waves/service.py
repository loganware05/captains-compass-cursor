"""Wave ledger init / status / advance / continue-after-merge."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.plan_waves.errors import PlanWavesError
from orchestrator.plan_waves.gh_pr import GhPrView, require_merged_pr
from orchestrator.plan_waves.parse import (
    parse_waves_from_plan,
    require_approved_plan,
    revision_hash,
)
from orchestrator.schemas.validate import validate_document

SCHEMA_NAME = "wave-ledger.schema.json"
SCHEMA_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def plans_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "plans"


def ledger_path(repo_root: Path, plan_id: str) -> Path:
    return plans_dir(repo_root) / plan_id / "wave-ledger.json"


def _validate(ledger: dict[str, Any]) -> None:
    validate_document(ledger, SCHEMA_NAME)


def _write_ledger(repo_root: Path, plan_id: str, ledger: dict[str, Any]) -> Path:
    _validate(ledger)
    path = ledger_path(repo_root, plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_wave_ledger(repo_root: Path, plan_id: str) -> dict[str, Any]:
    path = ledger_path(repo_root, plan_id)
    if not path.is_file():
        raise PlanWavesError(f"wave ledger missing: {path}")
    ledger = json.loads(path.read_text(encoding="utf-8"))
    if ledger.get("plan_id") != plan_id:
        raise PlanWavesError(
            f"ledger plan_id {ledger.get('plan_id')!r} != requested {plan_id!r}"
        )
    _validate(ledger)
    return ledger


def _next_pending_index(waves: list[dict[str, Any]]) -> int | None:
    for idx, wave in enumerate(waves):
        if wave.get("status") in ("pending", "in_progress", "open"):
            return idx
    return None


def _derive_next_action(ledger: dict[str, Any]) -> str:
    if ledger.get("pause_between_waves"):
        return "paused"
    waves = ledger["waves"]
    idx = _next_pending_index(waves)
    if idx is None:
        return "settle_complete"
    wave = waves[idx]
    status = wave.get("status")
    if status == "open":
        return "await_merge"
    if status == "merged":
        return "continue_after_merge"
    return "implement_wave"


def _refresh_derived(ledger: dict[str, Any]) -> None:
    waves = ledger["waves"]
    idx = _next_pending_index(waves)
    ledger["active_wave_id"] = waves[idx]["wave_id"] if idx is not None else None
    ledger["next_action"] = _derive_next_action(ledger)
    if ledger["next_action"] == "settle_complete":
        ledger["plan_status"] = "COMPLETE"
    elif ledger["next_action"] == "paused":
        ledger["plan_status"] = "PAUSED"
    elif ledger["plan_status"] not in ("REFUSED",):
        ledger["plan_status"] = "IN_PROGRESS"
    ledger["updated_at"] = _utc_now()


def init_wave_ledger(
    repo_root: Path,
    *,
    plan_id: str,
    from_path: Path | None = None,
    pause_between_waves: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    plan_path = Path(from_path) if from_path else Path(repo_root) / "IMPLEMENTATION_PLAN.md"
    if not plan_path.is_file():
        raise PlanWavesError(f"plan document missing: {plan_path}")
    text = plan_path.read_text(encoding="utf-8")
    require_approved_plan(text, plan_id)
    rev = revision_hash(text)
    path = ledger_path(repo_root, plan_id)
    if path.is_file() and not force:
        existing = load_wave_ledger(repo_root, plan_id)
        return {
            "ok": True,
            "action": "exists",
            "path": str(path),
            "ledger": existing,
        }
    parsed = parse_waves_from_plan(text)
    waves = []
    for entry in parsed:
        waves.append(
            {
                "wave_id": entry["wave_id"],
                "title": entry["title"],
                "status": "pending",
                "pr_url": None,
                "merged_sha": None,
                "merged_at": None,
                "optional": bool(entry.get("optional")),
            }
        )
    if waves:
        waves[0]["status"] = "in_progress"
    now = _utc_now()
    ledger: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": plan_id,
        "approved_revision": rev,
        "plan_status": "IN_PROGRESS",
        "created_at": now,
        "updated_at": now,
        "pause_between_waves": bool(pause_between_waves),
        "next_thread_id": None,
        "next_action": "implement_wave",
        "active_wave_id": waves[0]["wave_id"] if waves else None,
        "waves": waves,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_merge": False,
    }
    _refresh_derived(ledger)
    written = _write_ledger(repo_root, plan_id, ledger)
    return {"ok": True, "action": "init", "path": str(written), "ledger": ledger}


def wave_ledger_status(repo_root: Path, plan_id: str) -> dict[str, Any]:
    ledger = load_wave_ledger(repo_root, plan_id)
    idx = _next_pending_index(ledger["waves"])
    next_wave = ledger["waves"][idx] if idx is not None else None
    return {
        "ok": True,
        "plan_id": plan_id,
        "plan_status": ledger["plan_status"],
        "approved_revision": ledger["approved_revision"],
        "next_action": ledger["next_action"],
        "active_wave_id": ledger.get("active_wave_id"),
        "next_wave": next_wave,
        "remaining_count": sum(
            1
            for w in ledger["waves"]
            if w.get("status") in ("pending", "in_progress", "open", "merged")
        ),
        "pause_between_waves": ledger.get("pause_between_waves", False),
        "next_thread_id": ledger.get("next_thread_id"),
        "ledger": ledger,
    }


def _find_wave_for_pr(ledger: dict[str, Any], pr_url: str) -> int:
    """Prefer exact pr_url match; else first open/in_progress/pending non-complete."""
    normalized = (pr_url or "").rstrip("/")
    for idx, wave in enumerate(ledger["waves"]):
        existing = (wave.get("pr_url") or "").rstrip("/")
        if existing and existing == normalized:
            return idx
    idx = _next_pending_index(ledger["waves"])
    if idx is None:
        raise PlanWavesError("no remaining waves — refuse advance (settle/complete)")
    return idx


def advance_wave(
    repo_root: Path,
    *,
    plan_id: str,
    pr_url: str,
    gh_pr_view: GhPrView | None = None,
) -> dict[str, Any]:
    ledger = load_wave_ledger(repo_root, plan_id)
    if ledger.get("pause_between_waves"):
        raise PlanWavesError(
            "pause_between_waves=true — Captain opt-in pause; refuse auto-continue"
        )
    merge = require_merged_pr(pr_url, gh_pr_view=gh_pr_view)
    idx = _find_wave_for_pr(ledger, merge["pr_url"])
    wave = ledger["waves"][idx]

    # Idempotent: same merged_sha already recorded
    if (
        wave.get("merged_sha")
        and wave.get("merged_sha") == merge["merged_sha"]
        and wave.get("status") in ("merged", "complete")
    ):
        _refresh_derived(ledger)
        next_idx = _next_pending_index(ledger["waves"])
        return {
            "ok": True,
            "action": "idempotent",
            "merged": merge,
            "completed_wave": wave,
            "next_wave": ledger["waves"][next_idx] if next_idx is not None else None,
            "next_action": ledger["next_action"],
            "resume_prompt": _resume_prompt(plan_id, ledger, next_idx),
            "ledger": ledger,
        }

    if wave.get("status") == "complete" and wave.get("merged_sha") != merge["merged_sha"]:
        # Already complete under different SHA — try next pending
        nxt = _next_pending_index(ledger["waves"])
        if nxt is None:
            raise PlanWavesError("no remaining waves — refuse advance (settle/complete)")
        idx = nxt
        wave = ledger["waves"][idx]

    wave["pr_url"] = merge["pr_url"]
    wave["merged_sha"] = merge["merged_sha"]
    wave["merged_at"] = merge["merged_at"]
    wave["status"] = "complete"
    _refresh_derived(ledger)
    _write_ledger(repo_root, plan_id, ledger)

    next_idx = _next_pending_index(ledger["waves"])
    next_wave = ledger["waves"][next_idx] if next_idx is not None else None
    if next_wave and next_wave.get("status") == "pending":
        next_wave["status"] = "in_progress"
        _refresh_derived(ledger)
        _write_ledger(repo_root, plan_id, ledger)
        next_wave = ledger["waves"][next_idx]

    return {
        "ok": True,
        "action": "advanced",
        "merged": merge,
        "completed_wave": wave,
        "next_wave": next_wave,
        "next_action": ledger["next_action"],
        "resume_prompt": _resume_prompt(plan_id, ledger, next_idx),
        "ledger": ledger,
    }


def _resume_prompt(
    plan_id: str, ledger: dict[str, Any], next_idx: int | None
) -> str:
    if next_idx is None:
        return (
            f"Plan {plan_id}: no remaining waves. Allow T3 settle / completion report. "
            "Do not auto-merge. Do not forge APPROVED on a new plan."
        )
    wave = ledger["waves"][next_idx]
    return (
        f"Plan {plan_id} APPROVED revision {ledger['approved_revision']}: "
        f"continue wave {wave['wave_id']} ({wave['title']}) without re-asking Approve. "
        "Unsettle this thread if settled; if unsettle fails, create a continuation "
        "thread and record next_thread_id. Hard stops: budget, scope expand, failed "
        "validation, security-sensitive surface, pause_between_waves. "
        "Never auto-merge; never forge plan APPROVED."
    )


def continue_after_merge(
    repo_root: Path,
    *,
    plan_id: str,
    pr_url: str,
    plan_path: Path | None = None,
    gh_pr_view: GhPrView | None = None,
) -> dict[str, Any]:
    """Refuse unless plan APPROVED, PR MERGED, and waves remain (or idempotent)."""
    doc = Path(plan_path) if plan_path else Path(repo_root) / "IMPLEMENTATION_PLAN.md"
    if not doc.is_file():
        raise PlanWavesError(f"plan document missing: {doc}")
    text = doc.read_text(encoding="utf-8")
    require_approved_plan(text, plan_id)

    if not ledger_path(repo_root, plan_id).is_file():
        init_wave_ledger(repo_root, plan_id=plan_id, from_path=doc)

    status_before = wave_ledger_status(repo_root, plan_id)
    if status_before["next_action"] == "settle_complete":
        raise PlanWavesError("no remaining waves — refuse continue-after-merge")
    if status_before["pause_between_waves"]:
        raise PlanWavesError(
            "pause_between_waves=true — Captain opt-in pause; refuse auto-continue"
        )

    result = advance_wave(
        repo_root, plan_id=plan_id, pr_url=pr_url, gh_pr_view=gh_pr_view
    )
    if result.get("next_wave") is None and result.get("action") != "idempotent":
        # Final wave just completed — ok, emit settle prompt
        pass
    elif result.get("next_wave") is None and status_before["remaining_count"] <= 1:
        pass

    result["status_before"] = {
        "next_action": status_before["next_action"],
        "active_wave_id": status_before["active_wave_id"],
        "remaining_count": status_before["remaining_count"],
    }
    result["command"] = "continue-after-merge"
    return result
