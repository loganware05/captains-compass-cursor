"""Permission checklist for training-bridge export."""

from __future__ import annotations

from typing import Any

REQUIRED_CHECKS = (
    "export_authorized",
    "secrets_redacted_ack",
    "license_reviewed",
    "pii_reviewed",
    "specialized_model_handoff_ack",
)


class ChecklistError(ValueError):
    """Raised when the export permission checklist is incomplete."""


def normalize_checklist(raw: dict[str, Any] | None) -> dict[str, bool]:
    data = dict(raw or {})
    out: dict[str, bool] = {}
    for key in REQUIRED_CHECKS:
        val = data.get(key)
        if not isinstance(val, bool):
            raise ChecklistError(f"permission checklist missing boolean field: {key}")
        out[key] = val
    return out


def require_checklist_complete(checklist: dict[str, bool]) -> None:
    missing = [k for k, v in checklist.items() if v is not True]
    if missing:
        raise ChecklistError(
            "permission checklist incomplete — set true for: " + ", ".join(missing)
        )
