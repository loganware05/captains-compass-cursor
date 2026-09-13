"""Orchestrate detect → investigate → verify → report for NorthStar Code Reviewer."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.review.candidates import generate_heuristic_candidates, load_candidates_json
from orchestrator.review.detect import detect
from orchestrator.review.investigate import investigate
from orchestrator.review.report import ReportError, build_report, write_report
from orchestrator.review.specialists import compose_specialist_candidates
from orchestrator.review.verify import DEFAULT_MIN_CONFIDENCE, verify_findings

_VALID_CANDIDATE_MODES = frozenset(
    {"specialists", "heuristics", "specialists+heuristics", "fixtures"}
)


class ReviewError(ValueError):
    """Raised when the code review pipeline cannot complete safely."""


def _git_diff(repo_root: Path, base: str, head: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--no-ext-diff", f"{base}...{head}"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise ReviewError(f"git diff failed: {exc}") from exc
    if proc.returncode != 0:
        proc2 = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--no-ext-diff", base, head],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc2.returncode != 0:
            err = (proc.stderr or proc2.stderr or "").strip()
            raise ReviewError(f"git diff failed: {err or proc.returncode}")
        return proc2.stdout
    return proc.stdout


def run_code_review(
    *,
    repo_root: Path,
    run_id: str | None = None,
    base_ref: str = "",
    head_ref: str = "HEAD",
    diff_text: str | None = None,
    diff_file: Path | None = None,
    changed_paths: list[str] | None = None,
    plan_path: Path | None = None,
    intent_json: Path | None = None,
    candidates_path: Path | None = None,
    candidates_mode: str = "specialists",
    plan_id: str = "",
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    hermetic: bool = True,
    post_github_draft: bool = False,
    github_repo: str = "",
    pull_number: int = 0,
    github_allowlist: Path | None = None,
    severity_floor: str | None = None,
    github_commit_id: str | None = None,
    github_token: str | None = None,
    github_http_client: Any | None = None,
) -> dict[str, Any]:
    """Run the hermetic code-review pipeline and write evidence under the repo.

    Default ``candidates_mode`` is ``specialists`` (M28). Passing ``candidates_path``
    forces the fixtures source for hermetic CI. ``intent_json`` (M29) supplies a
    normalized intent pack without requiring a hand-written temp plan.
    ``post_github_draft`` (M30) is opt-in and allowlist-gated; default remains
    evidence-only. Model invocation remains disabled.
    """
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise ReviewError(f"repo_root is not a directory: {root}")

    mode = (candidates_mode or "specialists").strip().lower()
    if mode not in _VALID_CANDIDATE_MODES:
        raise ReviewError(
            f"invalid candidates_mode {candidates_mode!r}; "
            f"expected one of {sorted(_VALID_CANDIDATE_MODES)}"
        )

    if diff_text is None:
        if diff_file is not None:
            diff_text = Path(diff_file).read_text(encoding="utf-8", errors="replace")
        elif base_ref:
            diff_text = _git_diff(root, base_ref, head_ref or "HEAD")
        else:
            diff_text = ""

    resolved_plan = plan_path
    if resolved_plan is None and intent_json is None:
        for candidate in (
            root / "IMPLEMENTATION_PLAN.md",
            root / "INTENT_PACK.md",
            root / "docs" / "IMPLEMENTATION_PLAN.md",
            root / ".agent" / "intent" / "current.json",
        ):
            if candidate.is_file():
                if candidate.suffix.lower() == ".json":
                    intent_json = candidate
                else:
                    resolved_plan = candidate
                break

    detection = detect(
        repo_root=root,
        changed_paths=changed_paths,
        diff_text=diff_text or "",
        plan_path=resolved_plan,
        intent_json=intent_json,
    )
    context_pack = investigate(
        repo_root=root,
        detection=detection,
        diff_text=diff_text or "",
    )

    specialist_skills: list[str] = []
    if candidates_path is not None or mode == "fixtures":
        if candidates_path is None:
            raise ReviewError("candidates_mode=fixtures requires candidates_path")
        candidates = load_candidates_json(Path(candidates_path))
        candidates_source = "fixtures"
    elif mode == "heuristics":
        candidates = generate_heuristic_candidates(
            detection=detection,
            context_pack=context_pack,
        )
        candidates_source = "heuristics"
    else:
        include_heuristics = mode == "specialists+heuristics"
        candidates, specialist_skills, candidates_source = compose_specialist_candidates(
            detection=detection,
            context_pack=context_pack,
            include_heuristics=include_heuristics,
        )

    if hermetic is False:
        raise ReviewError(
            "non-hermetic/model invocation is not enabled "
            "(Captain lock: hermetic CI / no model in default path)"
        )

    findings = verify_findings(candidates, min_confidence=min_confidence)
    rid = run_id or f"cr-{uuid4().hex[:12]}"
    skills = list(detection.get("skills_suggested") or [])
    for skill in specialist_skills:
        if skill not in skills:
            skills.append(skill)
    github_draft_meta: dict[str, Any] | None = None
    github_posted = False
    if post_github_draft:
        from orchestrator.review.github_draft import post_if_allowed, write_draft_evidence

        if not github_repo or pull_number <= 0:
            raise ReviewError(
                "post_github_draft requires github_repo (owner/name) and pull_number"
            )
        draft_result = post_if_allowed(
            report={
                "run_id": rid,
                "summary": {"domains": list(detection.get("domains") or [])},
                "provenance": {"candidates_source": candidates_source},
            },
            findings=findings,
            repo_slug=github_repo,
            pull_number=int(pull_number),
            allowlist_path=github_allowlist,
            repo_root=root,
            severity_floor=severity_floor,
            commit_id=github_commit_id,
            token=github_token,
            http_client=github_http_client,
        )
        write_draft_evidence(root, rid, draft_result)
        github_posted = bool(draft_result.get("posted"))
        github_draft_meta = {
            "posted": github_posted,
            "reason": draft_result.get("reason"),
            "review_id": draft_result.get("review_id"),
            "state": draft_result.get("state"),
            "html_url": draft_result.get("html_url"),
            "evidence": draft_result.get("evidence") or {},
        }

    report = build_report(
        run_id=rid,
        repository=str(root),
        findings=findings,
        domains=list(detection.get("domains") or []),
        skills_invoked=skills,
        intent_artifact=str((detection.get("intent") or {}).get("plan_path") or ""),
        base_ref=base_ref,
        head_ref=head_ref,
        plan_id=plan_id,
        hermetic=True,
        candidates_source=candidates_source,
        github_review_posted=github_posted,
        github_draft=github_draft_meta,
    )
    try:
        path = write_report(root, report, context_pack=context_pack)
    except ReportError as exc:
        raise ReviewError(str(exc)) from exc

    return {
        "run_id": rid,
        "report_path": str(path),
        "report": report,
        "detection": detection,
        "findings": findings,
        "candidates_source": candidates_source,
        "specialist_skills": specialist_skills,
        "github_draft": github_draft_meta,
    }
