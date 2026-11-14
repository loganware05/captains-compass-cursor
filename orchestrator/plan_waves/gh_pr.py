"""GitHub PR merge verification via `gh` (injectable for tests)."""

from __future__ import annotations

import json
import re
import subprocess
from typing import Any, Callable

from orchestrator.plan_waves.errors import PlanWavesError

PR_URL_RE = re.compile(
    r"https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)",
    re.IGNORECASE,
)


def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
    match = PR_URL_RE.search((pr_url or "").strip())
    if not match:
        raise PlanWavesError(f"could not parse GitHub PR URL: {pr_url!r}")
    return match.group("owner"), match.group("repo"), int(match.group("number"))


def default_gh_pr_view(owner: str, repo: str, number: int) -> dict[str, Any]:
    cmd = [
        "gh",
        "pr",
        "view",
        str(number),
        "--repo",
        f"{owner}/{repo}",
        "--json",
        "state,mergedAt,mergeCommit,url",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise PlanWavesError("gh CLI not found — install/authenticate gh") from exc
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "gh failed").strip()
        raise PlanWavesError(f"gh pr view failed: {err}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise PlanWavesError("gh pr view returned invalid JSON") from exc


GhPrView = Callable[[str, str, int], dict[str, Any]]


def require_merged_pr(
    pr_url: str,
    *,
    gh_pr_view: GhPrView | None = None,
) -> dict[str, Any]:
    """Return merge facts or raise if PR is not MERGED."""
    owner, repo, number = parse_pr_url(pr_url)
    viewer = gh_pr_view or default_gh_pr_view
    data = viewer(owner, repo, number)
    state = str(data.get("state") or "").upper()
    merged_at = data.get("mergedAt")
    merge_commit = data.get("mergeCommit") or {}
    sha = ""
    if isinstance(merge_commit, dict):
        sha = str(merge_commit.get("oid") or merge_commit.get("sha") or "")
    elif isinstance(merge_commit, str):
        sha = merge_commit
    if state != "MERGED" or not merged_at:
        raise PlanWavesError(
            f"PR is not MERGED (state={state or 'unknown'}) — refuse continue-after-merge"
        )
    if not sha:
        raise PlanWavesError("MERGED PR missing mergeCommit oid — refuse advance")
    return {
        "pr_url": data.get("url") or pr_url,
        "state": "MERGED",
        "merged_at": str(merged_at),
        "merged_sha": sha,
        "owner": owner,
        "repo": repo,
        "number": number,
    }
