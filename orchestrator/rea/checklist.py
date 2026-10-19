"""Licensing / permission checklist for governed REA investigate."""

from __future__ import annotations

from typing import Any

REQUIRED_CHECKS = (
    "target_authorized",
    "license_reviewed",
    "execution_permitted",
    "source_docs_insufficient",
    "isolation_acknowledged",
)


class ChecklistError(ValueError):
    """Raised when the permission checklist is incomplete or invalid."""


def normalize_checklist(raw: dict[str, Any] | None) -> dict[str, bool]:
    data = dict(raw or {})
    out: dict[str, bool] = {}
    for key in REQUIRED_CHECKS:
        val = data.get(key)
        if not isinstance(val, bool):
            raise ChecklistError(
                f"permission checklist missing boolean field: {key}"
            )
        out[key] = val
    return out


def require_checklist_complete(checklist: dict[str, bool]) -> None:
    missing = [k for k, v in checklist.items() if v is not True]
    if missing:
        raise ChecklistError(
            "permission checklist incomplete — set true for: " + ", ".join(missing)
        )


def checklist_from_flags(
    *,
    target_authorized: bool = False,
    license_reviewed: bool = False,
    execution_permitted: bool = False,
    source_docs_insufficient: bool = False,
    isolation_acknowledged: bool = False,
) -> dict[str, bool]:
    return normalize_checklist(
        {
            "target_authorized": target_authorized,
            "license_reviewed": license_reviewed,
            "execution_permitted": execution_permitted,
            "source_docs_insufficient": source_docs_insufficient,
            "isolation_acknowledged": isolation_acknowledged,
        }
    )
