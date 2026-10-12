"""StatusProvider adapters (M51/M52). Default stub; opt-in http."""

from __future__ import annotations

from orchestrator.status.providers.http import HttpStatusProvider
from orchestrator.status.providers.select import select_status_provider
from orchestrator.status.providers.stub import StubStatusProvider

__all__ = ["HttpStatusProvider", "StubStatusProvider", "select_status_provider"]
