"""Technology Intelligence provider boundary (Phase H stub)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class CandidateCapability:
    """External discovery signal — never approved for execution in M1."""

    id: str
    version: str
    capabilities_provided: list[str]
    discovery_signal: str
    source_path: str
    provenance_url: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "kind": "candidate",
            "source": {
                "type": "external-candidate",
                "path": self.source_path,
                "provenance_url": self.provenance_url,
            },
            "capabilities_provided": list(self.capabilities_provided),
            "approved_for_execution": False,
            "lifecycle_stage": "DISCOVERED",
            "discovery_signal": self.discovery_signal,
            "notes": self.notes,
        }


class TechnologyIntelligenceProvider(Protocol):
    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        """Return normalized candidate capabilities for planning display only."""


class StubTechnologyIntelligenceProvider:
    """No-op provider until GitHub Star / external engines connect."""

    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        return []
