"""PICCO prompt composer over the instruction registry (M48)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.behavior.instructions.store import (
    InstructionStoreError,
    _utc_now,
    bundle_id_for_hash,
    find_bundle_for_context,
    hash_prompt_bundle_content,
    list_instructions,
    seed_global_operating_brief,
    write_bundle,
)
from orchestrator.providers.decision.state import redact_text

DEFAULT_PERSONA = (
    "You are a NorthStar engineering agent operating under Captain authority. "
    "Evidence and approval gates outrank improvisation."
)
DEFAULT_CONSTRAINTS = [
    "Never set approved_for_execution or weaken Captain approval gates.",
    "Never mutate Skills, routing, Policies, or .cursor/ guidance without an explicit apply path.",
    "Fail closed on missing evidence, provider errors, or authority ambiguity.",
]
DEFAULT_OUTPUT = (
    "Produce concrete, evidence-backed engineering artifacts. "
    "Cite tests, paths, and acceptance criteria when claiming completion."
)


def _select_instructions(
    repo_root: Path,
    *,
    agent: str = "",
    skill_id: str = "",
    task_type: str = "",
    model_hint: str = "",
    include_proposals: bool = True,
) -> list[dict[str, Any]]:
    entries = list_instructions(repo_root)
    selected: list[dict[str, Any]] = []
    for entry in entries:
        scope = str(entry.get("scope") or "")
        if scope == "global":
            selected.append(entry)
            continue
        if scope == "agent" and agent and entry.get("agent") == agent:
            selected.append(entry)
            continue
        if scope == "task-type" and task_type and entry.get("task_type") == task_type:
            selected.append(entry)
            continue
        if scope == "model" and model_hint and entry.get("model_hint") == model_hint:
            selected.append(entry)
            continue
        if scope == "proposal" and include_proposals:
            if agent and entry.get("agent") and entry.get("agent") != agent:
                continue
            if skill_id and entry.get("skill_id") and entry.get("skill_id") != skill_id:
                continue
            selected.append(entry)
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for entry in selected:
        iid = str(entry.get("instruction_id") or "")
        if not iid or iid in seen:
            continue
        seen.add(iid)
        out.append(entry)
    return out


def compose_prompt_bundle(
    repo_root: Path,
    *,
    agent: str = "",
    skill_id: str = "",
    task_type: str = "",
    model_hint: str = "",
    persist: bool = True,
    include_proposals: bool = True,
    seed_if_empty: bool = True,
) -> dict[str, Any]:
    """Compose a deterministic PICCO bundle. Never injects into live prompts."""
    selected = _select_instructions(
        repo_root,
        agent=agent,
        skill_id=skill_id,
        task_type=task_type,
        model_hint=model_hint,
        include_proposals=include_proposals,
    )
    if not selected and seed_if_empty:
        seed_global_operating_brief(repo_root)
        selected = _select_instructions(
            repo_root,
            agent=agent,
            skill_id=skill_id,
            task_type=task_type,
            model_hint=model_hint,
            include_proposals=include_proposals,
        )
    if not selected:
        raise InstructionStoreError("no instructions available to compose")

    instruction_texts = [
        redact_text(str(e.get("body") or "").strip()) for e in selected
    ]
    instruction_texts = [t for t in instruction_texts if t]
    instruction_ids = [str(e["instruction_id"]) for e in selected if e.get("instruction_id")]

    bundle: dict[str, Any] = {
        "persona": DEFAULT_PERSONA,
        "instructions": instruction_texts,
        "context": {
            "agent": agent,
            "skill_id": skill_id,
            "task_type": task_type,
            "model_hint": model_hint,
        },
        "constraints": list(DEFAULT_CONSTRAINTS),
        "output": DEFAULT_OUTPUT,
        "instruction_ids": instruction_ids,
        "agent": agent,
        "skill_id": skill_id,
        "task_type": task_type,
        "model_hint": model_hint,
        "schema_version": "1",
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    digest = hash_prompt_bundle_content(bundle)
    bundle["prompt_bundle_hash"] = digest
    bundle["bundle_id"] = bundle_id_for_hash(digest)
    bundle["created_at"] = _utc_now()
    if persist:
        write_bundle(repo_root, bundle)
    return bundle


def prompt_bundle_hash_for_packet(repo_root: Path, packet: dict[str, Any]) -> str:
    """Resolve an existing composed bundle hash for evaluate (record-only).

    Does not seed the registry, does not persist new bundles, and ignores
    proposal drafts so evaluate remains observe-only relative to M48 state.
    """
    agent = str(packet.get("agent") or "")
    skills = [str(s) for s in (packet.get("skill_ids") or []) if str(s)]
    skill_id = skills[0] if skills else ""
    existing = find_bundle_for_context(repo_root, agent=agent, skill_id=skill_id)
    if existing and existing.get("prompt_bundle_hash"):
        return str(existing["prompt_bundle_hash"])
    return ""
