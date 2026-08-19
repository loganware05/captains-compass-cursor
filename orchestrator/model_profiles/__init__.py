"""Model profile catalog loader."""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator.schemas.validate import ValidationError, load_schema, validate

CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"


def load_catalog() -> dict:
    with CATALOG_PATH.open(encoding="utf-8") as handle:
        catalog = json.load(handle)
    wrapper_schema = {
        "type": "object",
        "required": ["version", "profiles"],
        "properties": {
            "version": {"type": "string"},
            "profiles": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "object"},
            },
        },
    }
    validate(catalog, wrapper_schema)
    profile_schema = load_schema("model-profile.schema.json")
    for index, profile in enumerate(catalog["profiles"]):
        try:
            validate(profile, profile_schema)
        except ValidationError as exc:
            raise ValidationError(f"profiles[{index}]: {exc}") from exc
    return catalog
