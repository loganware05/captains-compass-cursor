"""File-backed Technology Intelligence provider (offline fixtures)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from orchestrator.providers.technology_intelligence import CandidateCapability
from orchestrator.providers.technology_intelligence.mapper import candidate_from_stars_shaped
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates

DEFAULT_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _fixtures_dir() -> Path:
    override = os.environ.get("COMPASS_TI_FIXTURES_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_FIXTURES_DIR


class FileTechnologyIntelligenceProvider:
    """Load offline redacted Stars-shaped candidate fixtures."""

    def __init__(self, fixtures_dir: Path | None = None) -> None:
        self.fixtures_dir = fixtures_dir or _fixtures_dir()

    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        del objective, context  # fixtures are curated offline samples
        if not self.fixtures_dir.is_dir():
            return []
        candidates: list[CandidateCapability] = []
        for path in sorted(self.fixtures_dir.glob("*.json")):
            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
            records = payload if isinstance(payload, list) else [payload]
            for raw in records:
                if not isinstance(raw, dict):
                    continue
                candidates.append(candidate_from_stars_shaped(raw))
        docs = [item.to_dict() for item in candidates]
        validate_ti_candidates(docs)
        return candidates


def select_ti_provider(repo_root: Path | None = None):
    """Return TI provider from COMPASS_TI_PROVIDER (default stub)."""
    from orchestrator.providers.technology_intelligence import StubTechnologyIntelligenceProvider
    from orchestrator.providers.technology_intelligence.github_stars_provider import (
        GithubStarsTechnologyIntelligenceProvider,
    )
    from orchestrator.providers.technology_intelligence.huggingface_file_provider import (
        HuggingFaceFileTechnologyIntelligenceProvider,
    )
    from orchestrator.providers.technology_intelligence.package_registry_file_provider import (
        PackageRegistryFileTechnologyIntelligenceProvider,
    )
    from orchestrator.providers.technology_intelligence.ti_cache import (
        CachedGithubStarsTechnologyIntelligenceProvider,
    )

    name = os.environ.get("COMPASS_TI_PROVIDER", "stub").strip().lower() or "stub"
    if name == "stub":
        return StubTechnologyIntelligenceProvider()
    if name == "file":
        return FileTechnologyIntelligenceProvider()
    if name in {"github-stars", "github", "live"}:
        return GithubStarsTechnologyIntelligenceProvider()
    if name in {"github-stars-cached", "cached", "stars-cached"}:
        return CachedGithubStarsTechnologyIntelligenceProvider(repo_root)
    if name in {"huggingface-file", "hf-file", "huggingface"}:
        return HuggingFaceFileTechnologyIntelligenceProvider()
    if name in {"package-registry-file", "package-registry", "npm-pypi-file"}:
        return PackageRegistryFileTechnologyIntelligenceProvider()
    return StubTechnologyIntelligenceProvider()
