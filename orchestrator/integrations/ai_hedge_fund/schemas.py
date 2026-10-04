"""Schemas and constants for the AI Hedge Fund adapter (AHF-P01)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

# Documented pin — Captain-approved form: SHA + optional local path (no submodule).
PINNED_REPO = "https://github.com/virattt/ai-hedge-fund"
PINNED_SHA = "78b779c1389e2d1452dc29606d2c4126d859b964"
PINNED_REF = "main"

ALLOWED_MODES = frozenset({"research", "paper", "backtest"})
DENIED_MODE_TOKENS = frozenset(
    {
        "live",
        "broker",
        "sign",
        "signing",
        "wallet",
        "real-money",
        "real_money",
        "production-trade",
        "production_trade",
    }
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class RunManifest:
    """Provenance record for every adapter operation."""

    run_id: str
    operation: str
    mode: str
    repo: str = PINNED_REPO
    pinned_sha: str = PINNED_SHA
    data_sources: list[str] = field(default_factory=list)
    selected_agents: list[str] = field(default_factory=list)
    model_versions: dict[str, str] = field(default_factory=dict)
    instruction_hashes: dict[str, str] = field(default_factory=dict)
    local_path: str | None = None
    provider: str = "fixture"
    created_at: str = field(default_factory=utc_now_iso)
    results: dict[str, Any] = field(default_factory=dict)
    approved_for_execution: bool = False
    authority_mutation: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        # Hard invariants — never allow callers to flip these via results.
        payload["approved_for_execution"] = False
        payload["authority_mutation"] = False
        return payload


def new_run_id(prefix: str = "ahf") -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def validate_manifest(payload: dict[str, Any]) -> list[str]:
    """Return a list of schema problems (empty = ok)."""
    errors: list[str] = []
    for key in ("run_id", "operation", "mode", "repo", "pinned_sha"):
        if not str(payload.get(key) or "").strip():
            errors.append(f"missing:{key}")
    mode = str(payload.get("mode") or "").strip().lower()
    if mode and mode not in ALLOWED_MODES:
        errors.append(f"invalid_mode:{mode}")
    if payload.get("approved_for_execution") is True:
        errors.append("approved_for_execution_must_be_false")
    if payload.get("authority_mutation") is True:
        errors.append("authority_mutation_must_be_false")
    return errors
