"""Offline TI cache for starred repositories (M8)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from orchestrator.providers.technology_intelligence import CandidateCapability
from orchestrator.providers.technology_intelligence.github_stars_provider import (
    _DEFAULT_TOP_N,
    discover_candidates_from_records,
    fetch_starred_repos,
)

_DEFAULT_LIMIT = 100


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ti_cache_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "intelligence" / "ti-cache"


def ti_cache_path(repo_root: Path) -> Path:
    return ti_cache_dir(repo_root) / "starred-repos.json"


def read_ti_cache(repo_root: Path) -> list[dict]:
    """Load cached GitHub API-shaped starred repo records."""
    path = ti_cache_path(repo_root)
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        records = payload.get("records")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
    return []


def write_ti_cache(repo_root: Path, records: list[dict]) -> Path:
    """Write starred repo cache with metadata envelope."""
    cache_dir = ti_cache_dir(repo_root)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = ti_cache_path(repo_root)
    envelope = {
        "refreshed_at": _utc_now(),
        "source": "gh api user/starred",
        "record_count": len(records),
        "records": records,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(envelope, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def refresh_ti_cache(repo_root: Path, *, limit: int = _DEFAULT_LIMIT) -> Path:
    """Fetch live starred repos via gh and persist to cache. Fail closed without auth."""
    records = fetch_starred_repos(limit=limit)
    if not records:
        raise RuntimeError("TI cache refresh failed: gh unavailable or not authenticated")
    return write_ti_cache(repo_root, records)


def resolve_repo_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).resolve()
    override = os.environ.get("COMPASS_REPO_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path.cwd().resolve()


class CachedGithubStarsTechnologyIntelligenceProvider:
    """Read-only TI from offline starred-repo cache (explicit refresh CLI)."""

    def __init__(
        self,
        repo_root: Path | None = None,
        *,
        top_n: int = _DEFAULT_TOP_N,
        load_cache: Callable[[Path], list[dict]] | None = None,
    ) -> None:
        self.repo_root = resolve_repo_root(repo_root)
        self.top_n = top_n
        self._load_cache = load_cache or read_ti_cache

    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        del context
        raw_repos = self._load_cache(self.repo_root)
        return discover_candidates_from_records(raw_repos, objective, top_n=self.top_n)


def load_recorded_cache_fixtures(fixtures_dir: Path) -> list[dict]:
    """Load golden cache envelope for offline tests."""
    path = fixtures_dir / "starred-repos-cache.json"
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return [item for item in payload["records"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []
