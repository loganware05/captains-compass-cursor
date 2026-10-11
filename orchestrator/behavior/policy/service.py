"""Operator service layer for northstar policy (M50)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from orchestrator.behavior.enabled import require_policy_promote_enabled
from orchestrator.behavior.policy.materialize import (
    PolicyMaterializeError,
    materialize_proposal,
)
from orchestrator.behavior.policy.promote import (
    PolicyPromoteError,
    ensure_policy_for_instruction,
    promote_policy,
)
from orchestrator.behavior.policy.shadow import PolicyShadowError, run_shadow
from orchestrator.behavior.policy.store import (
    PolicyStoreError,
    list_policies,
    load_policy,
)


class PolicyServiceError(ValueError):
    """Operator-facing policy errors."""


def list_registry(repo_root: Path) -> dict[str, Any]:
    require_policy_promote_enabled()
    policies = list_policies(repo_root)
    return {"policy_count": len(policies), "policies": policies}


def show_policy(repo_root: Path, policy_id: str) -> dict[str, Any]:
    require_policy_promote_enabled()
    try:
        policy = load_policy(repo_root, policy_id)
    except PolicyStoreError as exc:
        raise PolicyServiceError(str(exc)) from exc
    return {"policy": policy}


def create_from_instruction(repo_root: Path, instruction_id: str) -> dict[str, Any]:
    require_policy_promote_enabled()
    try:
        policy = ensure_policy_for_instruction(repo_root, instruction_id)
    except PolicyPromoteError as exc:
        raise PolicyServiceError(str(exc)) from exc
    return {"status": "created", "policy": policy}


def promote(
    repo_root: Path,
    *,
    to_state: str,
    policy_id: str = "",
    instruction_id: str = "",
    prompt_eval_report_id: str = "",
    captain_approved: bool = False,
    notes: str = "",
) -> dict[str, Any]:
    require_policy_promote_enabled()
    try:
        return promote_policy(
            repo_root,
            to_state=to_state,
            policy_id=policy_id,
            instruction_id=instruction_id,
            prompt_eval_report_id=prompt_eval_report_id,
            captain_approved=captain_approved,
            notes=notes,
        )
    except PolicyPromoteError as exc:
        raise PolicyServiceError(str(exc)) from exc


def shadow(
    repo_root: Path,
    policy_id: str,
    *,
    agent: str = "",
    skill_id: str = "",
) -> dict[str, Any]:
    require_policy_promote_enabled()
    try:
        report = run_shadow(
            repo_root, policy_id, agent=agent, skill_id=skill_id
        )
    except PolicyShadowError as exc:
        raise PolicyServiceError(str(exc)) from exc
    return {"status": "shadowed", "report": report, "applied": False}


def materialize(repo_root: Path, policy_id: str) -> dict[str, Any]:
    require_policy_promote_enabled()
    try:
        return materialize_proposal(repo_root, policy_id)
    except PolicyMaterializeError as exc:
        raise PolicyServiceError(str(exc)) from exc


def export_policies_csv(repo_root: Path, dest: Path) -> Path:
    require_policy_promote_enabled()
    policies = list_policies(repo_root)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "policy_id",
        "lifecycle_state",
        "title",
        "prompt_eval_report_id",
        "shadow_report_id",
        "prompt_bundle_hash",
        "approved_for_execution",
    ]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for policy in policies:
            writer.writerow({k: policy.get(k, "") for k in fieldnames})
    return dest
