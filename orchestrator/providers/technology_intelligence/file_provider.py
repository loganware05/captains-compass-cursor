"""File-backed Technology Intelligence provider (offline fixtures)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from orchestrator.providers.technology_intelligence import CandidateCapability
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates

DEFAULT_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _fixtures_dir() -> Path:
    override = os.environ.get("COMPASS_TI_FIXTURES_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_FIXTURES_DIR


def _candidate_from_stars_shaped(raw: dict) -> CandidateCapability:
    """Map redacted Stars-export shaped records to CandidateCapability."""
    source = raw.get("source") if isinstance(raw.get("source"), dict) else {}
    return CandidateCapability(
        id=str(raw["id"]),
        version=str(raw.get("version") or "0.1.0"),
        capabilities_provided=list(raw.get("capabilities_provided") or []),
        discovery_signal=str(
            raw.get("discovery_signal")
            or raw.get("star_signal")
            or "github-stars:redacted"
        ),
        source_path=str(source.get("path") or raw.get("full_name") or raw["id"]),
        provenance_url=str(source.get("provenance_url") or raw.get("html_url") or ""),
        notes=str(raw.get("notes") or raw.get("description") or ""),
    )


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
                candidates.append(_candidate_from_stars_shaped(raw))
        docs = [item.to_dict() for item in candidates]
        validate_ti_candidates(docs)
        return candidates


def select_ti_provider():
    """Return TI provider from COMPASS_TI_PROVIDER (default stub)."""
    from orchestrator.providers.technology_intelligence import StubTechnologyIntelligenceProvider

    name = os.environ.get("COMPASS_TI_PROVIDER", "stub").strip().lower() or "stub"
    if name == "stub":
        return StubTechnologyIntelligenceProvider()
    if name == "file":
        return FileTechnologyIntelligenceProvider()
    # Fail closed to stub for unknown values
    return StubTechnologyIntelligenceProvider()
