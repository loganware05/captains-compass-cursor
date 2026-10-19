"""Cognitive Core C7 — Training bridge (Specialized Model hand-off)."""

from orchestrator.train_bridge.enabled import (
    require_train_bridge_enabled,
    train_bridge_enabled,
)

__all__ = ["train_bridge_enabled", "require_train_bridge_enabled"]
