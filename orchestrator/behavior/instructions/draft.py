"""Draft instruction proposals from M47 behavior candidates (M48)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.behavior.instructions.store import build_instruction, write_instruction
from orchestrator.behavior.patterns.store import list_candidates


def draft_from_candidates(repo_root: Path) -> dict[str, Any]:
    """Convert M47 bcand-* guidance into draft instruction proposals."""
    candidates = list_candidates(repo_root)
    written: list[str] = []
    for candidate in candidates:
        summary = str(candidate.get("summary") or "").strip()
        if not summary:
            continue
        signal = str(candidate.get("signal") or "")
        polarity = str(candidate.get("polarity") or "negative")
        agent = str(candidate.get("agent") or "")
        skill_id = str(candidate.get("skill_id") or "")
        pattern_id = str(candidate.get("pattern_id") or "")
        candidate_id = str(candidate.get("candidate_id") or "")
        title = f"{polarity}-{signal or 'signal'}"
        body = (
            f"Proposed behavioral guidance (draft; not active).\n"
            f"Signal: {signal}\n"
            f"Polarity: {polarity}\n"
            f"Guidance: {summary}\n"
        )
        instruction = build_instruction(
            title=title,
            body=body,
            scope="proposal",
            agent=agent,
            skill_id=skill_id,
            source_candidate_ids=[candidate_id] if candidate_id else [],
            evidence_pattern_ids=[pattern_id] if pattern_id else [],
            approval_state="draft",
        )
        path = write_instruction(repo_root, instruction)
        written.append(str(path))
    return {
        "status": "drafted",
        "candidate_count": len(candidates),
        "instruction_count": len(written),
        "instructions": written,
    }
