"""Captain-gated apply of skill-improvement proposals (M20)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.learning.drafts import skill_drafts_dir
from orchestrator.learning.similarity import EXCLUDED_IMPROVEMENT_TARGETS, _SAFE_SLUG

MARKER_BEGIN = "<!-- compass-learned-from-stars:begin -->"
MARKER_END = "<!-- compass-learned-from-stars:end -->"


class ImprovementApplyError(ValueError):
    """Raised when improvement apply fails closed."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def applied_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "learning-applied"


def load_improvement_proposal(path: Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict) or doc.get("kind") != "skill-improvement-proposal":
        raise ImprovementApplyError("file is not a skill-improvement-proposal")
    return doc


def _learned_section(proposal: dict) -> str:
    slug = proposal.get("target_skill_slug")
    notes = ""
    changes = proposal.get("suggested_changes") or []
    if changes and isinstance(changes[0], dict):
        notes = str(changes[0].get("source_notes") or changes[0].get("rationale") or "")
    return (
        f"\n{MARKER_BEGIN}\n"
        f"## Learned from categorized Stars (Captain-applied)\n\n"
        f"- Target Skill: `{slug}`\n"
        f"- Candidate: `{proposal.get('candidate_id')}`\n"
        f"- Similarity: `{proposal.get('similarity')}`\n"
        f"- Category: `{proposal.get('star_category') or 'other'}`\n"
        f"- Applied at: `{_utc_now()}`\n\n"
        f"{notes}\n\n"
        f"Do not clone or execute the starred repository. Review this lesson "
        f"before treating it as procedure.\n"
        f"{MARKER_END}\n"
    )


def _merge_learned_section(existing: str, section: str) -> str:
    if MARKER_BEGIN in existing and MARKER_END in existing:
        pattern = re.compile(
            re.escape(MARKER_BEGIN) + r".*?" + re.escape(MARKER_END),
            re.DOTALL,
        )
        return pattern.sub(section.strip(), existing)
    return existing.rstrip() + "\n" + section


def apply_skill_improvement_proposal(
    repo_root: Path,
    proposal_path: Path,
    *,
    captain_approved: bool,
    apply_live: bool = False,
    control_root: Path | None = None,
) -> dict:
    """
    Apply an improvement proposal.

    Default: write an improved SKILL.md draft under skill-drafts (never live).
    With apply_live=True and captain_approved=True: append learned section to
    the live Skill and write an audit record.
    """
    repo_root = Path(repo_root).resolve()
    control = Path(control_root or repo_root).resolve()
    if not captain_approved:
        raise ImprovementApplyError("apply requires --captain-approved")

    proposal = load_improvement_proposal(proposal_path)
    if proposal.get("approved_for_execution") is not False:
        raise ImprovementApplyError("proposal must keep approved_for_execution=false")
    if proposal.get("auto_apply") is True:
        raise ImprovementApplyError("refuse auto_apply=true proposals")

    slug = str(proposal.get("target_skill_slug") or "")
    if not _SAFE_SLUG.match(slug):
        raise ImprovementApplyError(f"invalid target skill slug: {slug!r}")
    if slug in EXCLUDED_IMPROVEMENT_TARGETS:
        raise ImprovementApplyError(
            f"refuse apply to excluded/meta Skill {slug!r}"
        )

    live_skill = control / ".cursor" / "skills" / slug / "SKILL.md"
    if not live_skill.is_file():
        raise ImprovementApplyError(f"live Skill not found: {live_skill}")

    original = live_skill.read_text(encoding="utf-8")
    section = _learned_section(proposal)
    improved = _merge_learned_section(original, section)

    draft_slug = f"{slug}-from-learning"
    out_dir = skill_drafts_dir(repo_root, draft_slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    draft_md = out_dir / "SKILL.md"
    draft_md.write_text(improved, encoding="utf-8")
    (out_dir / "source-proposal.json").write_text(
        json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    live_written = False
    if apply_live:
        live_skill.write_text(improved, encoding="utf-8")
        live_written = True

    audit = {
        "kind": "skill-improvement-applied",
        "applied_at": _utc_now(),
        "target_skill_slug": slug,
        "candidate_id": proposal.get("candidate_id"),
        "proposal_path": str(proposal_path),
        "draft_skill_md": str(draft_md),
        "apply_live": apply_live,
        "live_written": live_written,
        "captain_approved": True,
        "approved_for_execution": False,
        "auto_apply": False,
        "notes": (
            "Captain-gated apply. Live mutation only when --apply-live was set. "
            "Still not an auto-install of new Skills."
        ),
    }
    audit_dir = applied_dir(repo_root)
    audit_dir.mkdir(parents=True, exist_ok=True)
    skip_id = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(proposal.get("candidate_id") or "applied")).strip("-")
    audit_path = audit_dir / f"{slug}-{skip_id}.json"
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    audit["audit_path"] = str(audit_path)
    return audit
