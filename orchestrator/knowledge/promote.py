"""Propose procedure promotions from knowledge items — staging + PR only."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from orchestrator.knowledge.store import list_knowledge_items, procedures_dir
from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
MIN_CONFIDENCE = 0.7


class ProcedurePromotionError(ValueError):
    """Raised when procedure promotion fails."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluate_gates(items: list[dict]) -> dict[str, bool]:
    if not items:
        return {"has_items": False, "confidence_met": False, "captain_approved_met": False}
    confidence_ok = all(float(i.get("confidence") or 0) >= MIN_CONFIDENCE for i in items)
    captain_ok = any(i.get("captain_approved") for i in items) or all(
        i.get("kind") in {"decision", "procedure"} for i in items
    )
    return {
        "has_items": True,
        "confidence_met": confidence_ok,
        "captain_approved_met": captain_ok,
    }


def gates_all_passed(gates: dict[str, bool]) -> bool:
    return all(gates.values())


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:80] or "procedure"


def build_procedure_proposal(
    items: list[dict],
    *,
    procedure_title: str,
    proposal_id: str | None = None,
    notes: str = "",
) -> dict:
    gates = evaluate_gates(items)
    if not gates_all_passed(gates):
        failed = [k for k, ok in gates.items() if not ok]
        raise ProcedurePromotionError(f"procedure gates failed: {', '.join(failed)}")
    return {
        "proposal_id": proposal_id or f"proc-{uuid4().hex[:12]}",
        "kind": "procedure-promotion",
        "knowledge_item_ids": [str(i["item_id"]) for i in items],
        "procedure_title": procedure_title,
        "gates_passed": gates,
        "staging_paths": {},
        "landing_mode": "staging_and_pr_only",
        "captain_approval_required": True,
        "notes": notes
        or "Staging draft only. Open Captain-reviewed PR to land reusable procedure.",
        "created_at": _utc_now(),
    }


def write_procedure_proposal(repo_root: Path, proposal: dict, items: list[dict]) -> Path:
    if proposal.get("landing_mode") != "staging_and_pr_only":
        raise ProcedurePromotionError("landing_mode must be staging_and_pr_only")
    pid = str(proposal["proposal_id"])
    if not _SAFE_ID.match(pid):
        raise ProcedurePromotionError(f"unsafe proposal_id: {pid!r}")
    title = str(proposal["procedure_title"])
    slug = _slug(title)
    staging = procedures_dir(repo_root) / "staging" / slug
    staging.mkdir(parents=True, exist_ok=True)
    playbook = staging / "playbook.md"
    lines = [
        f"# Procedure: {title}",
        "",
        "Staging draft — Captain PR required before use as live playbook.",
        "",
        "## Source knowledge items",
        "",
    ]
    for item in items:
        lines.append(f"- `{item['item_id']}` — {item.get('title', '')}")
    lines.extend(["", "## Steps", "", "1. *(Captain to refine after review)*", ""])
    playbook.write_text("\n".join(lines), encoding="utf-8")

    proposal = dict(proposal)
    proposal["staging_paths"] = {
        "playbook_markdown": str(playbook.relative_to(Path(repo_root))),
    }
    validate_document(proposal, "procedure-promotion.schema.json")

    out_dir = procedures_dir(repo_root) / "proposals"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pid}.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(proposal, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return out_path


def select_items_by_ids(repo_root: Path, item_ids: list[str]) -> list[dict]:
    by_id = {str(i["item_id"]): i for i in list_knowledge_items(repo_root)}
    missing = [iid for iid in item_ids if iid not in by_id]
    if missing:
        raise ProcedurePromotionError(f"unknown knowledge items: {missing}")
    return [by_id[iid] for iid in item_ids]
