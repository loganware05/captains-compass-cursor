"""Policy lifecycle promotion with fail-closed gates (M50)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.behavior.instructions.store import (
    InstructionStoreError,
    load_instruction,
    write_instruction,
)
from orchestrator.behavior.policy.gates import (
    PolicyGateError,
    require_captain_approved,
    require_prompt_eval_pass,
    require_proven_evidence,
    require_shadow_present,
)
from orchestrator.behavior.policy.shadow import PolicyShadowError, run_shadow
from orchestrator.behavior.policy.states import can_transition
from orchestrator.behavior.policy.store import (
    PolicyStoreError,
    _utc_now,
    load_policy,
    policy_id_for_instruction,
    write_event,
    write_evidence_summary,
    write_policy,
)


class PolicyPromoteError(ValueError):
    """Raised when promotion fails closed."""


def ensure_policy_for_instruction(
    repo_root: Path,
    instruction_id: str,
    *,
    title: str = "",
) -> dict[str, Any]:
    """Create or load a Policy wrapper for an instruction (starts at candidate)."""
    try:
        instr = load_instruction(repo_root, instruction_id)
    except InstructionStoreError as exc:
        raise PolicyPromoteError(str(exc)) from exc
    pid = str(instr.get("policy_id") or "") or policy_id_for_instruction(instruction_id)
    try:
        return load_policy(repo_root, pid)
    except PolicyStoreError:
        pass
    state = str(instr.get("approval_state") or "candidate")
    if state == "draft":
        state = "candidate"
    if state not in {
        "candidate",
        "sandbox_evaluated",
        "shadowed",
        "approved",
        "active",
        "proven",
        "retired",
    }:
        state = "candidate"
    policy = {
        "policy_id": pid,
        "title": title or str(instr.get("title") or instruction_id),
        "instruction_ids": [instruction_id],
        "lifecycle_state": state if state != "draft" else "candidate",
        "agent": str(instr.get("agent") or ""),
        "skill_id": str(instr.get("skill_id") or ""),
        "task_type": str(instr.get("task_type") or ""),
        "model_hint": str(instr.get("model_hint") or ""),
        "proven_evaluation_ids": [],
        "evidence_paths": [],
        "schema_version": "1",
        "created_at": _utc_now(),
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    write_policy(repo_root, policy)
    instr["policy_id"] = pid
    if instr.get("approval_state") == "draft":
        instr["approval_state"] = "candidate"
    write_instruction(repo_root, instr)
    return policy


def _sync_instruction_states(repo_root: Path, policy: dict[str, Any]) -> None:
    state = str(policy.get("lifecycle_state") or "candidate")
    pid = str(policy.get("policy_id") or "")
    for iid in policy.get("instruction_ids") or []:
        try:
            instr = load_instruction(repo_root, str(iid))
        except InstructionStoreError:
            continue
        instr["approval_state"] = state
        instr["policy_id"] = pid
        write_instruction(repo_root, instr)


def promote_policy(
    repo_root: Path,
    *,
    to_state: str,
    policy_id: str = "",
    instruction_id: str = "",
    prompt_eval_report_id: str = "",
    captain_approved: bool = False,
    notes: str = "",
) -> dict[str, Any]:
    """Advance a Policy to ``to_state`` under evidence + Captain gates."""
    if not policy_id and not instruction_id:
        raise PolicyPromoteError("require --policy-id or --instruction-id")
    if instruction_id and not policy_id:
        policy = ensure_policy_for_instruction(repo_root, instruction_id)
        policy_id = str(policy["policy_id"])
    else:
        try:
            policy = load_policy(repo_root, policy_id)
        except PolicyStoreError as exc:
            raise PolicyPromoteError(str(exc)) from exc

    from_state = str(policy.get("lifecycle_state") or "candidate")
    if not can_transition(from_state, to_state):
        raise PolicyPromoteError(
            f"illegal transition {from_state!r} → {to_state!r}"
        )

    try:
        require_captain_approved(to_state, captain_approved=captain_approved)
    except PolicyGateError as exc:
        raise PolicyPromoteError(str(exc)) from exc

    if to_state == "sandbox_evaluated":
        report_id = prompt_eval_report_id or str(policy.get("prompt_eval_report_id") or "")
        try:
            report = require_prompt_eval_pass(repo_root, report_id)
        except PolicyGateError as exc:
            raise PolicyPromoteError(str(exc)) from exc
        policy["prompt_eval_report_id"] = str(report["report_id"])
        # Prefer first case candidate hash if present
        cases = report.get("cases") or []
        if cases and isinstance(cases[0], dict) and cases[0].get("candidate_hash"):
            policy["prompt_bundle_hash"] = str(cases[0]["candidate_hash"])

    if to_state == "shadowed":
        try:
            shadow = run_shadow(repo_root, policy_id)
        except PolicyShadowError as exc:
            raise PolicyPromoteError(str(exc)) from exc
        policy["shadow_report_id"] = str(shadow["shadow_id"])
        policy["prompt_bundle_hash"] = str(shadow.get("candidate_hash") or "")

    if to_state == "approved":
        try:
            require_shadow_present(policy)
        except PolicyGateError as exc:
            raise PolicyPromoteError(str(exc)) from exc
        policy["captain_approved_at"] = _utc_now()

    if to_state == "active":
        if not policy.get("captain_approved_at"):
            policy["captain_approved_at"] = _utc_now()

    if to_state == "proven":
        try:
            eval_ids = require_proven_evidence(repo_root, policy)
        except PolicyGateError as exc:
            raise PolicyPromoteError(str(exc)) from exc
        policy["proven_evaluation_ids"] = eval_ids

    policy["lifecycle_state"] = to_state
    policy["approved_for_execution"] = False
    policy["authority_mutation"] = False
    write_policy(repo_root, policy)
    _sync_instruction_states(repo_root, policy)

    event_id = "pevt-" + hashlib.sha256(
        f"{policy_id}|{from_state}|{to_state}|{uuid4().hex}".encode("utf-8")
    ).hexdigest()[:12]
    event = {
        "event_id": event_id,
        "policy_id": policy_id,
        "from_state": from_state,
        "to_state": to_state,
        "prompt_eval_report_id": str(policy.get("prompt_eval_report_id") or ""),
        "shadow_report_id": str(policy.get("shadow_report_id") or ""),
        "evidence_paths": list(policy.get("evidence_paths") or []),
        "captain_approved": bool(captain_approved),
        "notes": notes,
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    write_event(repo_root, event)
    write_evidence_summary(
        repo_root,
        {
            "policy_id": policy_id,
            "lifecycle_state": to_state,
            "from_state": from_state,
            "event_id": event_id,
            "prompt_eval_report_id": policy.get("prompt_eval_report_id") or "",
            "shadow_report_id": policy.get("shadow_report_id") or "",
            "approved_for_execution": False,
            "authority_mutation": False,
        },
    )
    return {"status": "promoted", "policy": policy, "event": event}
