"""NorthStar connected-system adapters (fixture-backed)."""

from orchestrator.integrations.adapters.base import FixtureAdapterBase
from orchestrator.integrations.adapters.cursor import CursorAdapter
from orchestrator.integrations.adapters.github import GitHubAdapter
from orchestrator.integrations.adapters.linear import LinearAdapter
from orchestrator.integrations.adapters.slack import SlackAdapter

__all__ = [
    "FixtureAdapterBase",
    "GitHubAdapter",
    "LinearAdapter",
    "SlackAdapter",
    "CursorAdapter",
]
