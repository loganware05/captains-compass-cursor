"""M50 Policy / Instruction Promotion Lifecycle.

Governed lifecycle: candidate → sandbox_evaluated → shadowed → approved →
active → proven. Shadow is observe-only; Active compose-include requires
COMPASS_POLICY_APPLY_ENABLED. Never writes .cursor/ or grants execution.
"""

from __future__ import annotations

from orchestrator.behavior.policy.states import LIFECYCLE_STATES
from orchestrator.behavior.policy.store import (
    PolicyStoreError as PolicyError,
    ensure_layout,
    list_policies,
    load_policy,
)

__all__ = [
    "LIFECYCLE_STATES",
    "PolicyError",
    "ensure_layout",
    "list_policies",
    "load_policy",
]
