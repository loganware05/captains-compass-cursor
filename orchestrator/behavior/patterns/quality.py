"""Sample-quality and min-occurrence gates for pattern learning (M47)."""

from __future__ import annotations

import os
from typing import Any

from orchestrator.behavior.thresholds import threshold_for_signal

DEFAULT_MIN_OCCURRENCE = 3
PATTERN_SCHEMA_VERSION = "1"


def min_occurrence() -> int:
    raw = os.environ.get("COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE", "").strip()
    if not raw:
        return DEFAULT_MIN_OCCURRENCE
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_MIN_OCCURRENCE
    return max(1, value)


def polarity_for_signal(signal: str) -> str:
    """Shared detector polarity: praise → positive; other friction → negative."""
    return "positive" if signal == "praise" else "negative"


def record_is_usable(record: dict[str, Any]) -> bool:
    """Exclude abstaining / empty-signal records from pattern evidence."""
    if record.get("abstain"):
        return False
    signals = record.get("signals")
    if not isinstance(signals, dict) or not signals:
        return False
    return True


def qualifying_signals(
    record: dict[str, Any],
    *,
    thresholds: dict[str, float] | None = None,
) -> list[tuple[str, float, float]]:
    """Return (signal, score, threshold) for scores at/above configured floors."""
    if not record_is_usable(record):
        return []
    out: list[tuple[str, float, float]] = []
    signals = dict(record.get("signals") or {})
    for name, raw in signals.items():
        try:
            score = float(raw)
        except (TypeError, ValueError):
            continue
        floor = threshold_for_signal(str(name), thresholds)
        if score >= floor:
            out.append((str(name), score, floor))
    return out
