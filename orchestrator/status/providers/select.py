"""Select StatusProvider from COMPASS_STATUS_PROVIDER (default stub)."""

from __future__ import annotations

import os

from orchestrator.status.providers.base import StatusProvider
from orchestrator.status.providers.http import HttpStatusProvider, HttpStatusProviderError
from orchestrator.status.providers.stub import StubStatusProvider


class StatusProviderSelectError(ValueError):
    """Raised when provider selection is invalid or cannot be constructed."""


def selected_provider_name() -> str:
    return os.environ.get("COMPASS_STATUS_PROVIDER", "stub").strip().lower() or "stub"


def select_status_provider() -> StatusProvider:
    name = selected_provider_name()
    if name in {"", "stub"}:
        return StubStatusProvider()
    if name == "http":
        try:
            return HttpStatusProvider.from_env()
        except HttpStatusProviderError as exc:
            raise StatusProviderSelectError(str(exc)) from exc
    raise StatusProviderSelectError(
        f"unknown COMPASS_STATUS_PROVIDER={name!r} (supported: stub, http)"
    )
