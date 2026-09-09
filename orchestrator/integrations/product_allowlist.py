"""Sandbox-only product dispatch allowlist for NorthStar live/product paths."""

from __future__ import annotations

PRODUCT_DISPATCH_ALLOWLIST: frozenset[str] = frozenset(
    {
        "loganware05/captain-compass-sandbox",
    }
)

DEFAULT_PRODUCT_REPOSITORY = "loganware05/captain-compass-sandbox"


def require_allowed_repository(repository: str) -> str:
    """Fail closed unless repository is the sandbox product allowlist entry."""
    from orchestrator.integrations.routine import NorthStarRoutineError

    repo = (repository or "").strip()
    if repo not in PRODUCT_DISPATCH_ALLOWLIST:
        raise NorthStarRoutineError(
            f"BLOCKED_SCOPE: repository not allowlisted: {repo!r}"
        )
    return repo
