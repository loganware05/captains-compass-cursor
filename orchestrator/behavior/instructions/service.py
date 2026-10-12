"""Orchestrate proposal-only instruction registry operations (M48)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from orchestrator.behavior.enabled import require_instructions_enabled
from orchestrator.behavior.instructions.composer import compose_prompt_bundle
from orchestrator.behavior.instructions.draft import draft_from_candidates
from orchestrator.behavior.instructions.store import (
    InstructionStoreError,
    list_bundles,
    list_instructions,
    load_instruction,
    seed_global_operating_brief,
)


class InstructionServiceError(ValueError):
    """Operator-facing instruction errors."""


def list_registry(repo_root: Path) -> dict[str, Any]:
    require_instructions_enabled()
    seed_global_operating_brief(repo_root)
    instructions = list_instructions(repo_root)
    bundles = list_bundles(repo_root)
    return {
        "instruction_count": len(instructions),
        "bundle_count": len(bundles),
        "instructions": instructions,
        "bundles": bundles,
    }


def show_instruction(repo_root: Path, instruction_id: str) -> dict[str, Any]:
    require_instructions_enabled()
    try:
        instruction = load_instruction(repo_root, instruction_id)
    except InstructionStoreError as exc:
        raise InstructionServiceError(str(exc)) from exc
    related = [
        b
        for b in list_bundles(repo_root)
        if instruction_id in (b.get("instruction_ids") or [])
    ]
    return {"instruction": instruction, "bundles": related}


def compose(
    repo_root: Path,
    *,
    agent: str = "",
    skill_id: str = "",
    task_type: str = "",
    model_hint: str = "",
    execution_id: str = "",
) -> dict[str, Any]:
    require_instructions_enabled()
    try:
        seed_global_operating_brief(repo_root)
        bundle = compose_prompt_bundle(
            repo_root,
            agent=agent,
            skill_id=skill_id,
            task_type=task_type,
            model_hint=model_hint,
            persist=True,
        )
    except InstructionStoreError as exc:
        raise InstructionServiceError(str(exc)) from exc
    result: dict[str, Any] = {"status": "composed", "bundle": bundle}
    # M54: best-effort provenance when gated and execution_id present
    eid = (execution_id or "").strip()
    if eid:
        try:
            from orchestrator.behavior.enabled import provenance_enabled
            from orchestrator.behavior.provenance.service import (
                build_provenance_record,
            )
            from orchestrator.behavior.provenance.store import write_provenance

            if provenance_enabled():
                record = build_provenance_record(
                    repo_root,
                    execution_id=eid,
                    packet={
                        "execution_id": eid,
                        "agent": agent,
                        "skill_ids": [skill_id] if skill_id else [],
                        "prompt_bundle_hash": str(
                            bundle.get("prompt_bundle_hash") or ""
                        ),
                        "model": model_hint or "",
                    },
                )
                path = write_provenance(repo_root, record)
                result["provenance"] = {
                    "status": "captured",
                    "provenance": record,
                    "path": str(path),
                }
        except Exception:
            pass
    return result


def draft_candidates(repo_root: Path) -> dict[str, Any]:
    require_instructions_enabled()
    return draft_from_candidates(repo_root)


def export_instructions_csv(repo_root: Path, dest: Path) -> Path:
    require_instructions_enabled()
    instructions = list_instructions(repo_root)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "instruction_id",
        "scope",
        "title",
        "approval_state",
        "agent",
        "skill_id",
        "task_type",
        "created_at",
        "approved_for_execution",
    ]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for instruction in instructions:
            writer.writerow({k: instruction.get(k, "") for k in fieldnames})
    return dest
