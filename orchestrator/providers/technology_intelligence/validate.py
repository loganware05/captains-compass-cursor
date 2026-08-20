"""Validate Technology Intelligence candidate payloads before plan rendering."""

from __future__ import annotations

from orchestrator.schemas.validate import ValidationError, validate_document


class TechnologyIntelligenceValidationError(ValueError):
    """Raised when a provider returns invalid or unsafe candidates."""


def validate_ti_candidates(candidates: list[dict]) -> None:
    """Ensure every candidate is schema-valid and never approved for execution."""
    for index, candidate in enumerate(candidates):
        try:
            validate_document(candidate, "candidate-capability.schema.json")
        except ValidationError as exc:
            raise TechnologyIntelligenceValidationError(
                f"candidate[{index}] failed schema validation: {exc}"
            ) from exc
        if candidate.get("kind") != "candidate":
            raise TechnologyIntelligenceValidationError(
                f"candidate[{index}] must have kind=candidate"
            )
        if candidate.get("approved_for_execution") is not False:
            raise TechnologyIntelligenceValidationError(
                f"candidate[{index}] must have approved_for_execution=false"
            )
