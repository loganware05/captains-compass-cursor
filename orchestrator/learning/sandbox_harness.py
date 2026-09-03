"""Fixture-safe sandbox candidate harness for skill learning (M19)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.promotion.advance import advance_lifecycle, write_staging_candidate


class SandboxHarnessError(ValueError):
    """Raised when sandbox candidate harness fails closed."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evidence_dir(repo_root: Path, candidate_id: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in candidate_id)
    return Path(repo_root) / ".agent" / "evidence" / "candidate-sandbox-test" / safe


def run_fixture_sandbox_harness(
    repo_root: Path,
    candidate: dict,
    *,
    skill_slug: str,
    control_root: Path | None = None,
    promote_to_sandbox_tested: bool = True,
) -> dict:
    """
    Validate a staged candidate + draft Skill without cloning external repos.

    Checks:
    - approved_for_execution is false
    - draft SKILL.md + capability.yaml exist under skill-drafts
    - new from-stars-* drafts are not installed under .cursor/skills/

    When promote_to_sandbox_tested is False (e.g. --source live), evidence is
    written but lifecycle stays below SANDBOX_TESTED until Captain security review.
    """
    control = Path(control_root or repo_root).resolve()
    repo_root = Path(repo_root).resolve()
    skills_root = (control / ".cursor" / "skills").resolve()
    if repo_root == skills_root or skills_root in repo_root.parents:
        raise SandboxHarnessError("refuse --repo-root under .cursor/skills/")

    if candidate.get("approved_for_execution") is not False:
        raise SandboxHarnessError(
            "harness refuses candidates with approved_for_execution!=false"
        )

    draft_dir = (
        repo_root
        / ".agent"
        / "capabilities"
        / "candidates"
        / "skill-drafts"
        / skill_slug
    )
    skill_md = draft_dir / "SKILL.md"
    capability_yaml = draft_dir / "capability.yaml"
    if not skill_md.is_file() or not capability_yaml.is_file():
        raise SandboxHarnessError(
            f"missing unified draft under {draft_dir} (SKILL.md + capability.yaml required)"
        )

    live_target = control / ".cursor" / "skills" / skill_slug
    if skill_slug.startswith("from-stars-") and live_target.is_dir():
        raise SandboxHarnessError(
            f"refuse live Skill path for new draft slug: {live_target}"
        )

    evid = evidence_dir(repo_root, str(candidate.get("id") or skill_slug))
    evid.mkdir(parents=True, exist_ok=True)
    report = {
        "kind": "candidate-sandbox-test",
        "harness_kind": "fixture-file-checks",
        "ran_at": _utc_now(),
        "candidate_id": candidate.get("id"),
        "skill_slug": skill_slug,
        "passed": True,
        "approved_for_execution": False,
        "promote_to_sandbox_tested": promote_to_sandbox_tested,
        "checks": {
            "draft_skill_md": str(skill_md),
            "draft_capability_yaml": str(capability_yaml),
            "live_skill_absent_for_new_draft": not (
                skill_slug.startswith("from-stars-") and live_target.is_dir()
            ),
        },
        "notes": (
            "Fixture harness only — no external clone/exec; "
            "Captain approval required before live Skill install"
        ),
    }
    report_path = evid / "sandbox-test.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary_path = evid / "summary.md"
    summary_path.write_text(
        f"# Candidate sandbox test — `{candidate.get('id')}`\n\n"
        f"- Passed: true\n"
        f"- Harness: fixture-file-checks\n"
        f"- Skill slug: `{skill_slug}`\n"
        f"- Evidence: `{report_path}`\n"
        f"- Live install: **not performed** (Captain gate)\n",
        encoding="utf-8",
    )

    evidence_paths = [str(report_path), str(summary_path)]
    stage = "SANDBOX_TESTED" if promote_to_sandbox_tested else "ANALYZED"
    staging = write_staging_candidate(
        repo_root,
        candidate,
        target_stage=stage,
        evidence_paths=evidence_paths if promote_to_sandbox_tested else None,
        skill_slug=skill_slug,
    )
    if promote_to_sandbox_tested:
        advance_lifecycle(
            candidate,
            target_stage="SANDBOX_TESTED",
            evidence_paths=evidence_paths,
            skill_slug=skill_slug,
            repo_root=repo_root,
        )
    return {
        "passed": True,
        "evidence_dir": str(evid),
        "report_path": str(report_path),
        "summary_path": str(summary_path),
        "staging_candidate": str(staging),
        "lifecycle_stage": stage,
        "harness_kind": "fixture-file-checks",
    }
