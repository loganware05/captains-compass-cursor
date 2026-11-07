"""Fail-closed gate for conversation trajectory ingest."""

from __future__ import annotations

import os

GATE = "COMPASS_CONVERSATION_INGEST_ENABLED"


def _truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def conversation_ingest_enabled() -> bool:
    return _truthy(GATE)


def require_conversation_ingest_enabled() -> None:
    if not conversation_ingest_enabled():
        raise PermissionError(
            f"conversation ingest disabled — set {GATE}=1 "
            "(evidence-only; never grants authority)"
        )
