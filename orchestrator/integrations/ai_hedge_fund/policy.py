"""Deterministic policy for AI Hedge Fund adapter — research/paper/backtest only."""

from __future__ import annotations

from typing import Any

from orchestrator.integrations.ai_hedge_fund.schemas import ALLOWED_MODES, DENIED_MODE_TOKENS


class LiveExecutionDenied(RuntimeError):
    """Raised when a request attempts live / broker / wallet / signing paths."""


def _normalize_token(value: str) -> str:
    return value.strip().lower().replace(" ", "-").replace("_", "-")


def assert_research_mode(mode: str, *, extras: dict[str, Any] | None = None) -> str:
    """Validate mode and scan request extras for denied live tokens.

    Returns the normalized allowed mode or raises ``LiveExecutionDenied``.
    """
    raw = (mode or "").strip().lower()
    if not raw:
        raise LiveExecutionDenied("mode is required (research|paper|backtest)")
    if raw not in ALLOWED_MODES:
        raise LiveExecutionDenied(
            f"mode {raw!r} denied; allowed={sorted(ALLOWED_MODES)}"
        )

    extras = extras or {}
    haystacks: list[str] = [raw]
    for key, value in extras.items():
        haystacks.append(_normalize_token(str(key)))
        if isinstance(value, str):
            haystacks.append(_normalize_token(value))
        elif isinstance(value, (list, tuple, set)):
            haystacks.extend(_normalize_token(str(item)) for item in value)

    for token in haystacks:
        parts = {token, *token.replace("-", " ").split()}
        # Also check contiguous hyphen forms already present.
        for part in parts:
            compact = part.replace("-", "")
            for denied in DENIED_MODE_TOKENS:
                denied_n = _normalize_token(denied)
                if part == denied_n or compact == denied_n.replace("-", ""):
                    raise LiveExecutionDenied(
                        f"live execution token {denied!r} denied in request"
                    )
    return raw


def assert_enabled(enabled: bool) -> None:
    if not enabled:
        raise LiveExecutionDenied(
            "AI Hedge Fund adapter disabled "
            "(set COMPASS_AHF_ADAPTER_ENABLED=1 to enable)"
        )
