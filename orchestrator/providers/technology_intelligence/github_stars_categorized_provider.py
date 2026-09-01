"""TI provider reading batch-categorized GitHub starred repos (M14)."""

from __future__ import annotations

from pathlib import Path

from orchestrator.providers.technology_intelligence import CandidateCapability
from orchestrator.providers.technology_intelligence.github_stars_provider import (
    _DEFAULT_TOP_N,
    discover_candidates_from_records,
)
from orchestrator.providers.technology_intelligence.stars_categorization import (
    read_categorized_records,
)
from orchestrator.providers.technology_intelligence.ti_cache import resolve_repo_root
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates


class GithubStarsCategorizedTechnologyIntelligenceProvider:
    """Read-only TI from offline batch-categorized starred-repo output."""

    def __init__(
        self,
        repo_root: Path | None = None,
        *,
        top_n: int = _DEFAULT_TOP_N,
    ) -> None:
        self.repo_root = resolve_repo_root(repo_root)
        self.top_n = top_n

    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        del context
        raw_repos = read_categorized_records(self.repo_root)
        if not raw_repos:
            return []
        candidates = discover_candidates_from_records(raw_repos, objective, top_n=self.top_n)
        enriched: list[CandidateCapability] = []
        category_by_name = {
            str(repo.get("full_name") or ""): str(repo.get("star_category") or "")
            for repo in raw_repos
        }
        for cand in candidates:
            category = category_by_name.get(cand.source_path, "")
            notes = cand.notes
            if category:
                notes = f"[{category}] {notes}".strip()
            enriched.append(
                CandidateCapability(
                    id=cand.id,
                    version=cand.version,
                    capabilities_provided=list(cand.capabilities_provided),
                    discovery_signal=f"{cand.discovery_signal}|category:{category or 'other'}",
                    source_path=cand.source_path,
                    provenance_url=cand.provenance_url,
                    notes=notes,
                )
            )
        validate_ti_candidates([item.to_dict() for item in enriched])
        return enriched
