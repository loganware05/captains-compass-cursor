"""Policy lifecycle states and legal transitions (M50)."""

from __future__ import annotations

LIFECYCLE_STATES = frozenset(
    {
        "candidate",
        "sandbox_evaluated",
        "shadowed",
        "approved",
        "active",
        "proven",
        "retired",
    }
)

# from_state → allowed to_states
TRANSITIONS: dict[str, frozenset[str]] = {
    "candidate": frozenset({"sandbox_evaluated", "retired"}),
    "sandbox_evaluated": frozenset({"shadowed", "retired"}),
    "shadowed": frozenset({"approved", "retired"}),
    "approved": frozenset({"active", "retired"}),
    "active": frozenset({"proven", "retired"}),
    "proven": frozenset({"retired"}),
    "retired": frozenset(),
}

CAPTAIN_REQUIRED = frozenset({"approved", "active", "proven", "retired"})

SCHEMA_VERSION = "1"


def can_transition(from_state: str, to_state: str) -> bool:
    return to_state in TRANSITIONS.get(from_state, frozenset())
