"""Train Skill drafts from Experience samples (product → control)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from orchestrator.schemas.validate import validate_document

_SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ExperienceTrainingError(ValueError):
    """Raised when Experience → Skill draft training fails."""


def load_experience_file(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "experience.schema.json")
    return doc


def suggest_skill_slug(experience: dict) -> str:
    skills = experience.get("skills_used") or []
    if skills:
        base = str(skills[0]).strip().lower().replace("_", "-")
        if _SAFE_SLUG.match(base):
            return f"{base}-from-experience"
    plan = str(experience.get("plan_id", "experience")).lower()
    plan = re.sub(r"[^a-z0-9]+", "-", plan).strip("-") or "experience"
    return f"{plan}-skill"


def draft_skill_markdown(experience: dict, skill_slug: str) -> str:
    objective = experience.get("objective") or "(no objective recorded)"
    lessons = experience.get("lessons") or []
    lesson_lines = "\n".join(f"- {item}" for item in lessons) or "- (none recorded)"
    skills = ", ".join(experience.get("skills_used") or []) or "(none)"
    return (
        f"---\n"
        f"name: {skill_slug}\n"
        f"description: Draft Skill trained from Experience {experience.get('experience_id')}\n"
        f"---\n\n"
        f"# {skill_slug}\n\n"
        f"## Use this Skill when\n\n"
        f"Replaying lessons from a prior successful workstream.\n\n"
        f"## Origin Experience\n\n"
        f"- Experience ID: `{experience.get('experience_id')}`\n"
        f"- Plan ID: `{experience.get('plan_id')}`\n"
        f"- Outcome: `{experience.get('outcome')}`\n"
        f"- Source instance: `{experience.get('source_instance')}`\n"
        f"- Skills used: {skills}\n\n"
        f"## Objective\n\n{objective}\n\n"
        f"## Lessons\n\n{lesson_lines}\n\n"
        f"## Procedure\n\n"
        f"1. Review lessons and provenance with the Captain.\n"
        f"2. Adapt steps to the current repository context.\n"
        f"3. Run control-repo doctor/tests before proposing promotion.\n"
        f"4. Stop for Captain approval before copying into `.cursor/skills/`.\n\n"
        f"## Prohibited actions\n\n"
        f"- Do not auto-merge this draft into live Skills\n"
        f"- Do not treat product Experiences as approved Compass Skills until tested\n"
    )


def draft_capability_yaml(experience: dict, skill_slug: str) -> str:
    caps = experience.get("capabilities_exercised") or ["experience-derived-procedure"]
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
            f"  from_experience: {experience.get('experience_id')}",
            "  captain_approval_required: true",
            "notes: Draft from experience-skill-training — requires Captain-approved PR",
            "",
        ]
    )
    return "\n".join(lines)


def train_skill_from_experience(
    control_repo_root: Path,
    experience_path: Path,
    *,
    skill_slug: str | None = None,
) -> dict[str, Path]:
    """
    Import an Experience (often from a product repo) and write a Skill draft
    under the control repo staging area for local testing before Captain PR.
    """
    experience = load_experience_file(experience_path)
    slug = skill_slug or suggest_skill_slug(experience)
    if not _SAFE_SLUG.match(slug):
        raise ExperienceTrainingError(f"invalid skill slug: {slug!r}")

    out_dir = (
        Path(control_repo_root)
        / ".agent"
        / "capabilities"
        / "candidates"
        / "skill-drafts"
        / slug
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    skill_md = out_dir / "SKILL.md"
    capability_yaml = out_dir / "capability.yaml"
    experience_copy = out_dir / "source-experience.json"

    skill_md.write_text(draft_skill_markdown(experience, slug), encoding="utf-8")
    capability_yaml.write_text(draft_capability_yaml(experience, slug), encoding="utf-8")
    experience_copy.write_text(
        json.dumps(experience, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "skill_md": skill_md,
        "capability_yaml": capability_yaml,
        "source_experience": experience_copy,
    }
