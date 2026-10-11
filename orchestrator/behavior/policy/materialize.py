"""Proposal-only materialize drafts for Active Policies (M50).

Never copies into .cursor/. Captain must open a PR from the proposal tree.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.behavior.instructions.store import load_instruction
from orchestrator.behavior.policy.store import (
    PolicyStoreError,
    _write_json,
    ensure_layout,
    load_policy,
    materialize_dir,
)
from orchestrator.providers.decision.state import redact_text


class PolicyMaterializeError(ValueError):
    """Raised when materialize proposal generation fails closed."""


def materialize_proposal(repo_root: Path, policy_id: str) -> dict[str, Any]:
    try:
        policy = load_policy(repo_root, policy_id)
    except PolicyStoreError as exc:
        raise PolicyMaterializeError(str(exc)) from exc
    state = str(policy.get("lifecycle_state") or "")
    if state not in {"active", "proven", "approved"}:
        raise PolicyMaterializeError(
            f"materialize-proposal requires approved|active|proven, got {state!r}"
        )
    ensure_layout(repo_root)
    out_dir = materialize_dir(repo_root) / policy_id
    out_dir.mkdir(parents=True, exist_ok=True)

    instructions: list[dict[str, Any]] = []
    for iid in policy.get("instruction_ids") or []:
        instr = load_instruction(repo_root, str(iid))
        body = redact_text(str(instr.get("body") or ""))
        md_name = f"{iid}.md"
        (out_dir / md_name).write_text(
            f"# {instr.get('title') or iid}\n\n"
            f"<!-- proposal-only; not live .cursor/ content -->\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
        instructions.append(
            {
                "instruction_id": iid,
                "title": instr.get("title"),
                "body_file": md_name,
                "approval_state": instr.get("approval_state"),
            }
        )

    manifest = {
        "policy_id": policy_id,
        "lifecycle_state": state,
        "instruction_ids": list(policy.get("instruction_ids") or []),
        "instructions": instructions,
        "target_hint": ".cursor/ (Captain PR only — never auto-copied)",
        "applied": False,
        "approved_for_execution": False,
        "authority_mutation": False,
        "notes": (
            "Proposal-only materialization. Open a Captain-reviewed PR to copy "
            "selected content into .cursor/ if desired. M50 never auto-writes."
        ),
    }
    _write_json(out_dir / "manifest.json", manifest)
    readme = (
        "# Materialize proposal (M50)\n\n"
        "This directory is a **proposal only**. NorthStar will not copy these "
        "files into `.cursor/` automatically.\n"
    )
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    return {
        "status": "materialized_proposal",
        "path": str(out_dir),
        "manifest": manifest,
        "applied": False,
    }
