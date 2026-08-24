"""Live GitHub Stars Technology Intelligence provider (starred repos only, M7)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from orchestrator.providers.technology_intelligence import CandidateCapability
from orchestrator.providers.technology_intelligence.mapper import (
    candidate_from_stars_shaped,
    repo_record_from_github_api,
)
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates

_TOKEN = re.compile(r"[a-z0-9]{3,}", re.I)
_DEFAULT_LIMIT = 100
_DEFAULT_TOP_N = 10


def _tokenize(text: str) -> set[str]:
    return {match.group(0).lower() for match in _TOKEN.finditer(text)}


def _score_repo(objective_tokens: set[str], repo: dict) -> float:
    if not objective_tokens:
        return 0.0
    haystack = " ".join(
        [
            str(repo.get("full_name") or ""),
            str(repo.get("description") or ""),
            " ".join(str(t) for t in repo.get("topics") or []),
        ]
    ).lower()
    repo_tokens = _tokenize(haystack)
    overlap = len(objective_tokens & repo_tokens)
    if overlap == 0:
        return 0.0
    return overlap / len(objective_tokens)


def gh_available() -> bool:
    return shutil.which("gh") is not None


def gh_authenticated() -> bool:
    if not gh_available():
        return False
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def fetch_starred_repos(*, limit: int = _DEFAULT_LIMIT) -> list[dict]:
    """Fetch starred repositories via gh API. Returns [] when gh unavailable."""
    if not gh_authenticated():
        return []
    per_page = min(max(limit, 1), 100)
    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "user/starred",
                "-f",
                f"per_page={per_page}",
                "-f",
                "page=1",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0 or not result.stdout.strip():
        return []
    payload = json.loads(result.stdout)
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


class GithubStarsTechnologyIntelligenceProvider:
    """Live TI from Captain's GitHub starred repositories (explicit opt-in)."""

    def __init__(
        self,
        *,
        fetch_starred: Callable[..., list[dict]] | None = None,
        limit: int = _DEFAULT_LIMIT,
        top_n: int = _DEFAULT_TOP_N,
    ) -> None:
        self._fetch_starred = fetch_starred or fetch_starred_repos
        self.limit = limit
        self.top_n = top_n

    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        del context
        raw_repos = self._fetch_starred(limit=self.limit)
        if not raw_repos:
            return []
        objective_tokens = _tokenize(objective)
        ranked: list[tuple[float, dict]] = []
        for repo in raw_repos:
            score = _score_repo(objective_tokens, repo)
            if score <= 0 and objective_tokens:
                continue
            ranked.append((score if objective_tokens else 1.0, repo))
        ranked.sort(key=lambda pair: (-pair[0], str(pair[1].get("full_name") or "")))
        selected = [repo for _, repo in ranked[: self.top_n]] if objective_tokens else raw_repos[: self.top_n]

        candidates: list[CandidateCapability] = []
        for repo in selected:
            shaped = repo_record_from_github_api(repo)
            candidates.append(candidate_from_stars_shaped(shaped))
        docs = [item.to_dict() for item in candidates]
        validate_ti_candidates(docs)
        return candidates


def load_recorded_starred_fixtures(fixtures_dir: Path) -> list[dict]:
    """Load golden recorded starred-repo payloads for offline tests."""
    path = fixtures_dir / "starred-repos.json"
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []
