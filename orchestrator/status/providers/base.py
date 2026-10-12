"""StatusProvider protocol (M52)."""

from __future__ import annotations

from typing import Any, Protocol


class StatusProvider(Protocol):
    """Read-oriented explanation provider for Project Overseer snapshots."""

    name: str
    model: str

    def explain(self, snapshot: dict[str, Any]) -> str:
        """Return explanation text; must not mutate authority or memory docs."""
