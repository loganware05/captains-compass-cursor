"""File-backed Hugging Face Technology Intelligence provider (offline fixtures)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from orchestrator.providers.technology_intelligence import CandidateCapability
from orchestrator.providers.technology_intelligence.mapper import (
    candidate_from_huggingface_shaped,
)
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates

DEFAULT_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "huggingface"
_DEFAULT_TOP_N = 8


def _fixtures_dir() -> Path:
    override = os.environ.get("COMPASS_HF_TI_FIXTURES_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_FIXTURES_DIR


def _score_candidate(objective: str, candidate: CandidateCapability) -> float:
    tokens = {t.lower() for t in objective.replace("/", " ").replace("-", " ").split() if len(t) > 2}
    if not tokens:
        return 0.0
    blob = " ".join(
        [
            candidate.id,
            candidate.discovery_signal,
            candidate.notes,
            " ".join(candidate.capabilities_provided),
            candidate.source_path,
        ]
    ).lower()
    hits = sum(1 for t in tokens if t in blob)
    return hits / max(len(tokens), 1)


class HuggingFaceFileTechnologyIntelligenceProvider:
    """Load offline Hugging Face model-card-shaped fixtures (no Hub network)."""

    def __init__(
        self,
        fixtures_dir: Path | None = None,
        *,
        top_n: int = _DEFAULT_TOP_N,
    ) -> None:
        self.fixtures_dir = fixtures_dir or _fixtures_dir()
        self.top_n = top_n

    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        del context
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
                candidates.append(candidate_from_huggingface_shaped(raw))
        docs = [item.to_dict() for item in candidates]
        validate_ti_candidates(docs)
        ranked = sorted(
            candidates,
            key=lambda c: _score_candidate(objective, c),
            reverse=True,
        )
        return ranked[: self.top_n]
