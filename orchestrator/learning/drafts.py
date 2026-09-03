"""Unified Skill draft emitter for Stars candidates (M19)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from orchestrator.registry.yaml_simple import load_simple_yaml

_SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class LearningDraftError(ValueError):
    """Raised when Skill draft emission fails."""


def skill_drafts_dir(repo_root: Path, skill_slug: str) -> Path:
    return (
        Path(repo_root)
        / ".agent"
        / "capabilities"
        / "candidates"
        / "skill-drafts"
        / skill_slug
    )


def draft_skill_markdown_from_candidate(candidate: dict, skill_slug: str) -> str:
    category = str((candidate.get("provenance") or {}).get("star_category") or "")
    notes = str(candidate.get("notes") or "(no notes)")
    caps = ", ".join(candidate.get("capabilities_provided") or []) or "(none inferred)"
    signal = str(candidate.get("discovery_signal") or "")
    source = candidate.get("source") if isinstance(candidate.get("source"), dict) else {}
    return (
        f"---\n"
        f"name: {skill_slug}\n"
        f"description: Draft Skill from categorized Stars candidate {candidate.get('id')}\n"
        f"---\n\n"
        f"# {skill_slug}\n\n"
        f"## Use this Skill when\n\n"
        f"Applying lessons derived from a categorized GitHub Stars discovery signal "
        f"(category `{category or 'other'}`).\n\n"
        f"## Origin candidate\n\n"
        f"- Candidate ID: `{candidate.get('id')}`\n"
        f"- Discovery signal: `{signal}`\n"
        f"- Source path: `{source.get('path')}`\n"
        f"- Provenance URL: `{source.get('provenance_url')}`\n"
        f"- Star category: `{category or 'other'}`\n"
        f"- Capabilities: {caps}\n\n"
        f"## Notes from discovery\n\n{notes}\n\n"
        f"## Procedure\n\n"
        f"1. Review provenance and category with the Captain.\n"
        f"2. Adapt steps to the current repository context — do not clone or execute "
        f"the starred repository.\n"
        f"3. Run control-repo `./scripts/doctor.sh` and tests before proposing promotion.\n"
        f"4. Stop for Captain approval before copying into `.cursor/skills/`.\n\n"
        f"## Prohibited actions\n\n"
        f"- Do not auto-merge this draft into live Skills\n"
        f"- Do not set `approved_for_execution: true`\n"
        f"- Do not clone or execute external starred repositories from this draft\n"
    )


def draft_capability_yaml_from_candidate(candidate: dict, skill_slug: str) -> str:
    caps = list(candidate.get("capabilities_provided") or [])
    if not caps:
        category = str((candidate.get("provenance") or {}).get("star_category") or "other")
        caps = [f"stars-{category}-procedure"]
    lines = [
        f"id: {skill_slug}",
        'version: "0.1.0"',
        "kind: skill",
        "source:",
        "  type: compass-skill",
        f"  path: .cursor/skills/{skill_slug}/SKILL.md",
        "lifecycle_stage: AVAILABLE_SKILL",
        "capabilities_provided:",
    ]
    for cap in caps:
        lines.append(f"  - {cap}")
    lines.extend(
        [
            "security_sensitivity: medium",
            "provenance:",
            "  inferred: false",
            f"  from_candidate: {candidate.get('id')}",
            f"  discovery_signal: {candidate.get('discovery_signal') or ''}",
            "  captain_approval_required: true",
            "notes: Draft from skill-learning-loop — requires Captain-approved PR",
            "",
        ]
    )
    return "\n".join(lines)


def write_unified_skill_draft(
    repo_root: Path,
    candidate: dict,
    skill_slug: str,
) -> dict[str, Path]:
    """Write SKILL.md + capability.yaml + source candidate under skill-drafts/."""
    if not _SAFE_SLUG.match(skill_slug):
        raise LearningDraftError(f"invalid skill slug: {skill_slug!r}")
    if candidate.get("approved_for_execution") is not False:
        raise LearningDraftError("candidates must keep approved_for_execution=false")

    out_dir = skill_drafts_dir(repo_root, skill_slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    skill_md = out_dir / "SKILL.md"
    capability_yaml = out_dir / "capability.yaml"
    source_candidate = out_dir / "source-candidate.json"

    skill_md.write_text(
        draft_skill_markdown_from_candidate(candidate, skill_slug), encoding="utf-8"
    )
    yaml_text = draft_capability_yaml_from_candidate(candidate, skill_slug)
    load_simple_yaml(yaml_text)
    capability_yaml.write_text(yaml_text, encoding="utf-8")
    source_candidate.write_text(
        json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "skill_md": skill_md,
        "capability_yaml": capability_yaml,
        "source_candidate": source_candidate,
    }
