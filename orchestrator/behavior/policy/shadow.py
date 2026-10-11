"""Shadow compose compare — would-have-changed without apply (M50)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from orchestrator.behavior.instructions.composer import compose_prompt_bundle
from orchestrator.behavior.instructions.store import (
    InstructionStoreError,
    load_instruction,
    write_instruction,
)
from orchestrator.behavior.policy.store import (
    PolicyStoreError,
    load_policy,
    write_shadow,
)


class PolicyShadowError(ValueError):
    """Raised when shadow compare fails closed."""


def _shadow_id(policy_id: str, baseline_hash: str, candidate_hash: str) -> str:
    material = f"{policy_id}|{baseline_hash}|{candidate_hash}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
    return f"pshadow-{digest}"


def run_shadow(
    repo_root: Path,
    policy_id: str,
    *,
    agent: str = "",
    skill_id: str = "",
    task_type: str = "",
    model_hint: str = "",
) -> dict[str, Any]:
    """Compare baseline compose vs would-be Active include for the Policy.

    Never sets applied=true. Does not mutate live Active state.
    """
    try:
        policy = load_policy(repo_root, policy_id)
    except PolicyStoreError as exc:
        raise PolicyShadowError(str(exc)) from exc

    instruction_ids = [str(x) for x in (policy.get("instruction_ids") or []) if str(x)]
    if not instruction_ids:
        raise PolicyShadowError(f"policy {policy_id!r} has no instruction_ids")

    agent = agent or str(policy.get("agent") or "")
    skill_id = skill_id or str(policy.get("skill_id") or "")
    task_type = task_type or str(policy.get("task_type") or "")
    model_hint = model_hint or str(policy.get("model_hint") or "")

    # Snapshot + temporarily mark linked instructions active for candidate compose.
    originals: list[dict[str, Any]] = []
    try:
        for iid in instruction_ids:
            instr = load_instruction(repo_root, iid)
            originals.append(dict(instr))
        baseline = compose_prompt_bundle(
            repo_root,
            agent=agent,
            skill_id=skill_id,
            task_type=task_type,
            model_hint=model_hint,
            persist=False,
            include_proposals=False,
            include_active=False,
            seed_if_empty=True,
        )
        for iid in instruction_ids:
            instr = load_instruction(repo_root, iid)
            instr["approval_state"] = "active"
            instr["policy_id"] = policy_id
            write_instruction(repo_root, instr)
        candidate = compose_prompt_bundle(
            repo_root,
            agent=agent,
            skill_id=skill_id,
            task_type=task_type,
            model_hint=model_hint,
            persist=False,
            include_proposals=False,
            include_active=True,
            seed_if_empty=True,
        )
    except (InstructionStoreError, PolicyStoreError) as exc:
        raise PolicyShadowError(str(exc)) from exc
    finally:
        for instr in originals:
            try:
                write_instruction(repo_root, instr)
            except InstructionStoreError:
                pass

    baseline_hash = str(baseline.get("prompt_bundle_hash") or "")
    candidate_hash = str(candidate.get("prompt_bundle_hash") or "")
    would_have = baseline_hash != candidate_hash
    b_ids = list(baseline.get("instruction_ids") or [])
    c_ids = list(candidate.get("instruction_ids") or [])
    added = sorted(set(c_ids) - set(b_ids))
    removed = sorted(set(b_ids) - set(c_ids))
    diff_summary = json.dumps(
        {"added_instruction_ids": added, "removed_instruction_ids": removed},
        sort_keys=True,
    )
    report = {
        "shadow_id": _shadow_id(policy_id, baseline_hash, candidate_hash),
        "policy_id": policy_id,
        "instruction_ids": instruction_ids,
        "baseline_hash": baseline_hash,
        "candidate_hash": candidate_hash,
        "baseline_instruction_ids": b_ids,
        "candidate_instruction_ids": c_ids,
        "would_have_changed": would_have,
        "diff_summary": diff_summary,
        "applied": False,
        "agent": agent,
        "skill_id": skill_id,
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    write_shadow(repo_root, report)
    return report
