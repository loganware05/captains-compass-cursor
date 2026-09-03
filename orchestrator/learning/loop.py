"""Orchestrate the Captain-gated skill learning loop (M19)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.learning.drafts import write_unified_skill_draft
from orchestrator.learning.export import (
    LearningExportError,
    export_categorized_to_staging,
)
from orchestrator.learning.sandbox_harness import run_fixture_sandbox_harness
from orchestrator.learning.similarity import (
    DEFAULT_SIMILARITY_THRESHOLD,
    find_similar_skills,
    write_improvement_proposal,
)
from orchestrator.providers.technology_intelligence.github_stars_provider import (
    fetch_starred_repos,
    load_recorded_starred_fixtures,
)
from orchestrator.providers.technology_intelligence.stars_categorization import (
    run_batch_categorization,
)
from orchestrator.providers.technology_intelligence.ti_cache import read_ti_cache


class LearningLoopError(ValueError):
    """Raised when the skill learning loop fails closed."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def learning_runs_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "learning-runs"


def _load_source_repos(repo_root: Path, source: str, *, limit: int = 100) -> tuple[list[dict], str]:
    source = (source or "fixtures").strip().lower()
    if source == "fixtures":
        fixtures = repo_root / "tests" / "fixtures" / "ti" / "github-stars-recorded"
        repos = load_recorded_starred_fixtures(fixtures)
        if not repos:
            # Allow control_root fixtures when repo_root is a temp product copy
            control_fixtures = (
                Path(__file__).resolve().parents[2]
                / "tests"
                / "fixtures"
                / "ti"
                / "github-stars-recorded"
            )
            repos = load_recorded_starred_fixtures(control_fixtures)
        return repos, "fixtures:github-stars-recorded"
    if source == "live":
        repos = fetch_starred_repos(limit=limit)
        if not repos:
            raise LearningLoopError("gh unavailable or not authenticated for --source live")
        return repos, "gh api user/starred"
    if source in ("ti-cache", "cache"):
        repos = read_ti_cache(repo_root)
        if not repos:
            raise LearningLoopError("ti-cache empty; run refresh-ti-cache.sh first")
        return repos, "ti-cache:starred-repos.json"
    raise LearningLoopError(f"unsupported source: {source!r} (use fixtures|ti-cache|live)")


def run_skill_learning_loop(
    repo_root: Path,
    *,
    objective: str,
    source: str = "fixtures",
    top_n: int = 3,
    category_filter: str | None = None,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    control_root: Path | None = None,
    run_id: str | None = None,
    skip_categorize: bool = False,
) -> dict:
    """
    Run the explicit skill learning loop and stop before live Skill install.

    Steps:
      1. Categorize Stars (unless skip_categorize)
      2. Export top-N candidates to staging
      3. For each: similarity check → improvement proposal and/or new draft
      4. Fixture sandbox harness → SANDBOX_TESTED + evidence
      5. Write learning-run report; never write .cursor/skills/ drafts as live
    """
    repo_root = Path(repo_root).resolve()
    control = Path(control_root or repo_root).resolve()
    if not objective.strip():
        raise LearningLoopError("objective is required")

    if not skip_categorize:
        try:
            repos, src_label = _load_source_repos(repo_root, source)
        except LearningLoopError:
            raise
        except Exception as exc:  # pragma: no cover
            raise LearningLoopError(str(exc)) from exc
        labels = (
            control
            / "tests"
            / "fixtures"
            / "ti"
            / "github-stars-labels"
            / "manual-labels.json"
        )
        if not labels.is_file():
            labels = None
        run_batch_categorization(
            repo_root,
            repos,
            labels_path=labels,
            source=src_label,
        )

    try:
        exported = export_categorized_to_staging(
            repo_root,
            objective,
            top_n=top_n,
            category_filter=category_filter,
        )
    except LearningExportError as exc:
        raise LearningLoopError(str(exc)) from exc

    results: list[dict] = []
    for item in exported:
        candidate = item["candidate"]
        repo = item["repo"]
        draft_slug = item["skill_slug"]
        similar = find_similar_skills(
            control,
            candidate,
            repo=repo,
            threshold=similarity_threshold,
        )

        entry: dict = {
            "candidate_id": item["candidate_id"],
            "full_name": item["full_name"],
            "star_category": item["star_category"],
            "staging_path": item["staging_path"],
            "similar_skills": similar,
            "mode": "improve-existing" if similar else "draft-new",
        }

        if similar:
            # Prefer improving the top match; still emit a draft for review.
            top = similar[0]
            entry["target_skill_slug"] = top["skill_slug"]
            drafts = write_unified_skill_draft(repo_root, candidate, draft_slug)
            harness = run_fixture_sandbox_harness(
                repo_root,
                candidate,
                skill_slug=draft_slug,
                control_root=control,
            )
            proposal = write_improvement_proposal(
                repo_root,
                candidate,
                top,
                evidence_paths=[harness["report_path"], harness["summary_path"]],
            )
            entry["improvement_proposal"] = str(proposal)
            entry["draft"] = {k: str(v) for k, v in drafts.items()}
            entry["harness"] = harness
        else:
            drafts = write_unified_skill_draft(repo_root, candidate, draft_slug)
            harness = run_fixture_sandbox_harness(
                repo_root,
                candidate,
                skill_slug=draft_slug,
                control_root=control,
            )
            entry["draft"] = {k: str(v) for k, v in drafts.items()}
            entry["harness"] = harness
            entry["skill_slug"] = draft_slug

        results.append(entry)

    run_id = run_id or f"learning-{_utc_now().replace(':', '').replace('-', '')}"
    out_dir = learning_runs_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "kind": "skill-learning-run",
        "run_id": run_id,
        "ran_at": _utc_now(),
        "objective": objective,
        "source": source,
        "top_n": top_n,
        "category_filter": category_filter,
        "similarity_threshold": similarity_threshold,
        "approved_for_execution": False,
        "captain_approval_required_for_live_skills": True,
        "auto_install": False,
        "candidate_count": len(results),
        "results": results,
        "notes": (
            "Staging + evidence only. Promote live Skills with "
            "promote-candidate.sh --captain-approved after Captain review."
        ),
    }
    report_path = out_dir / f"{run_id}.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path)
    return report
