"""Offline TI cache for starred repositories (M8+)."""

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


def read_ti_cache_envelope(repo_root: Path) -> dict | None:
    """Load full cache envelope (metadata + records) if present."""
    path = ti_cache_path(repo_root)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return {
            "fetched_at": None,
            "refreshed_at": None,
            "source": "legacy-list",
            "record_count": len(payload),
            "records": [item for item in payload if isinstance(item, dict)],
        }
    if isinstance(payload, dict):
        return payload
    return None


def read_ti_cache(repo_root: Path) -> list[dict]:
    """Load cached GitHub API-shaped starred repo records."""
    envelope = read_ti_cache_envelope(repo_root)
    if not envelope:
        return []
    records = envelope.get("records")
    if isinstance(records, list):
        return [item for item in records if isinstance(item, dict)]
    return []


def cache_fetched_at(repo_root: Path) -> str | None:
    """Return fetched_at (or legacy refreshed_at) from cache envelope."""
    envelope = read_ti_cache_envelope(repo_root)
    if not envelope:
        return None
    return (
        str(envelope.get("fetched_at") or envelope.get("refreshed_at") or "").strip()
        or None
    )


def cache_age_hours(repo_root: Path, *, now: datetime | None = None) -> float | None:
    """Hours since fetched_at; None if missing/unparseable."""
    stamp = cache_fetched_at(repo_root)
    if not stamp:
        return None
    try:
        fetched = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    current = now or datetime.now(timezone.utc)
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    return max(0.0, (current - fetched).total_seconds() / 3600.0)


def is_cache_stale(repo_root: Path, *, max_age_hours: float) -> bool:
    """True when cache missing, unparseable, or older than max_age_hours."""
    age = cache_age_hours(repo_root)
    if age is None:
        return True
    return age >= float(max_age_hours)


def write_ti_cache(repo_root: Path, records: list[dict]) -> Path:
    """Write starred repo cache with metadata envelope (includes fetched_at)."""
    cache_dir = ti_cache_dir(repo_root)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = ti_cache_path(repo_root)
    now = _utc_now()
    envelope = {
        "fetched_at": now,
        "refreshed_at": now,  # backward-compatible alias
        "source": "gh api user/starred",
        "record_count": len(records),
        "records": records,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(envelope, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def refresh_ti_cache(
    repo_root: Path,
    *,
    limit: int = _DEFAULT_LIMIT,
    if_stale_hours: float | None = None,
) -> Path:
    """Fetch live starred repos via gh and persist to cache.

    When if_stale_hours is set and the existing cache is fresher, skip the network
    fetch and return the existing path.
    """
    path = ti_cache_path(repo_root)
    if if_stale_hours is not None and path.is_file() and not is_cache_stale(
        repo_root, max_age_hours=if_stale_hours
    ):
        return path
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
