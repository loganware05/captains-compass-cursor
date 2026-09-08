"""NorthStar branding registry and legacy alias normalization.

Parsers accept Captain's Compass legacy forms. New serializers emit NorthStar.
Machine-readable identifiers (repo slug, Skill IDs, paths, env vars) stay stable.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any

BRANDING_REGISTRY: dict[str, Any] = {
    "canonical_name": "NorthStar",
    "canonical_slug": "northstar",
    "legacy_names": [
        "Captain's Compass",
        "Captains Compass",
        "Captain Compass",
    ],
    "legacy_slugs": [
        "captains-compass",
        "captain-compass",
    ],
    "compatibility_version": 1,
}

# Governance terms are unchanged in M21.
CAPTAIN_ROLE = "Captain"
FIRST_MATE_ROLE = "First Mate"

_LEGACY_NAME_PATTERN = re.compile(
    r"captain'?s?\s*compass",
    re.IGNORECASE,
)
_LEGACY_SLUG_PATTERN = re.compile(
    r"captains?-compass",
    re.IGNORECASE,
)


def get_branding_registry() -> dict[str, Any]:
    """Return a deep copy of the versioned branding registry."""
    return deepcopy(BRANDING_REGISTRY)


def branding_registry_json(*, indent: int = 2) -> str:
    return json.dumps(get_branding_registry(), indent=indent, sort_keys=True) + "\n"


def is_legacy_product_name(value: str | None) -> bool:
    if not value or not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    registry = BRANDING_REGISTRY
    lowered = text.casefold()
    for name in registry["legacy_names"]:
        if lowered == name.casefold():
            return True
    for slug in registry["legacy_slugs"]:
        if lowered == slug.casefold():
            return True
    return bool(_LEGACY_NAME_PATTERN.fullmatch(text) or _LEGACY_SLUG_PATTERN.fullmatch(text))


def is_canonical_product_name(value: str | None) -> bool:
    if not value or not isinstance(value, str):
        return False
    text = value.strip()
    return text.casefold() in {
        BRANDING_REGISTRY["canonical_name"].casefold(),
        BRANDING_REGISTRY["canonical_slug"].casefold(),
    }


def normalize_product_name(value: str | None) -> str:
    """Map legacy or canonical product names to NorthStar."""
    if value is None or not str(value).strip():
        return BRANDING_REGISTRY["canonical_name"]
    text = str(value).strip()
    if is_canonical_product_name(text) or is_legacy_product_name(text):
        return BRANDING_REGISTRY["canonical_name"]
    # Soft normalize embedded legacy phrases for human-facing output.
    if _LEGACY_NAME_PATTERN.search(text) or _LEGACY_SLUG_PATTERN.search(text):
        return BRANDING_REGISTRY["canonical_name"]
    return text


def normalize_product_slug(value: str | None) -> str:
    if value is None or not str(value).strip():
        return BRANDING_REGISTRY["canonical_slug"]
    text = str(value).strip()
    if is_canonical_product_name(text) or is_legacy_product_name(text):
        return BRANDING_REGISTRY["canonical_slug"]
    return text.casefold().replace(" ", "-")


def display_name() -> str:
    return BRANDING_REGISTRY["canonical_name"]


def legacy_alias_received(value: str | None) -> str | None:
    """Return the original legacy form when input was a recognized alias."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if is_legacy_product_name(text) and not is_canonical_product_name(text):
        return text
    return None
