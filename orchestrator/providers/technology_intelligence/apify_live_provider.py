"""Live Apify MCP Technology Intelligence skeleton (fail-closed; no call-actor)."""

from __future__ import annotations

from orchestrator.providers.technology_intelligence import CandidateCapability
from orchestrator.providers.technology_intelligence.apify_gates import (
    apify_token,
    require_apify_live_enabled,
)


class ApifyLiveTechnologyIntelligenceProvider:
    """Injectable live Apify MCP skeleton — fails closed in v1.80.0.

    Does not call Actors. Future work may search Actors via MCP after
    Captain opts into live spend/network separately from this release.
    """

    def discover_candidates(
        self, objective: str, context: dict
    ) -> list[CandidateCapability]:
        del objective, context
        require_apify_live_enabled()
        if not apify_token():
            raise PermissionError(
                "apify live requires COMPASS_APIFY_TOKEN or APIFY_TOKEN"
            )
        raise RuntimeError(
            "Live Apify MCP transport not injected in v1.80.0 skeleton; "
            "use COMPASS_TI_PROVIDER=apify-file (call-actor deferred)"
        )
