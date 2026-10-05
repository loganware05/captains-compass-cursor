"""Fixture-backed AI Hedge Fund adapter operations (AHF-P01)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from orchestrator.integrations.ai_hedge_fund.evaluators import compare_runs
from orchestrator.integrations.ai_hedge_fund.policy import (
    LiveExecutionDenied,
    assert_enabled,
    assert_research_mode,
)
from orchestrator.integrations.ai_hedge_fund.schemas import (
    PINNED_REPO,
    PINNED_SHA,
    RunManifest,
    new_run_id,
    validate_manifest,
)

DEFAULT_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def adapter_enabled() -> bool:
    raw = os.environ.get("COMPASS_AHF_ADAPTER_ENABLED", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _optional_local_path() -> str | None:
    path = os.environ.get("COMPASS_AHF_LOCAL_PATH", "").strip()
    return path or None


def _load_json(name: str, fixtures_dir: Path) -> dict[str, Any]:
    path = fixtures_dir / name
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"fixture {name} must be a JSON object")
    return payload


class AiHedgeFundAdapter:
    """Read-only NorthStar boundary over pinned ai-hedge-fund.

    v1 is **fixture-only** for strategy agents / backtest / paper. An optional
    local checkout path may be recorded for provenance but is never executed
    in this release (Captain decision: fixture-only in v1).
    """

    def __init__(
        self,
        *,
        fixtures_dir: Path | None = None,
        enabled: bool | None = None,
        local_path: str | None = None,
        require_enabled: bool = True,
    ) -> None:
        self.fixtures_dir = Path(fixtures_dir) if fixtures_dir else DEFAULT_FIXTURES_DIR
        self.enabled = adapter_enabled() if enabled is None else enabled
        self.local_path = local_path if local_path is not None else _optional_local_path()
        self.require_enabled = require_enabled
        self._runs: dict[str, RunManifest] = {}

    def _gate(self, mode: str, *, extras: dict[str, Any] | None = None) -> str:
        if self.require_enabled:
            assert_enabled(self.enabled)
        return assert_research_mode(mode, extras=extras)

    def _record(
        self,
        *,
        operation: str,
        mode: str,
        results: dict[str, Any],
        data_sources: list[str] | None = None,
        selected_agents: list[str] | None = None,
        model_versions: dict[str, str] | None = None,
        instruction_hashes: dict[str, str] | None = None,
    ) -> RunManifest:
        manifest = RunManifest(
            run_id=new_run_id(),
            operation=operation,
            mode=mode,
            repo=PINNED_REPO,
            pinned_sha=PINNED_SHA,
            data_sources=list(data_sources or ["fixture"]),
            selected_agents=list(selected_agents or []),
            model_versions=dict(model_versions or {}),
            instruction_hashes=dict(instruction_hashes or {}),
            local_path=self.local_path,
            provider="fixture",
            results=results,
        )
        errors = validate_manifest(manifest.to_dict())
        if errors:
            raise ValueError(f"invalid run manifest: {errors}")
        self._runs[manifest.run_id] = manifest
        return manifest

    def create_research_run(
        self,
        *,
        objective: str,
        mode: str = "research",
        agents: list[str] | None = None,
    ) -> dict[str, Any]:
        mode_n = self._gate(mode, extras={"objective": objective})
        fixture = _load_json("research_run.json", self.fixtures_dir)
        selected = list(agents or fixture.get("selected_agents") or ["warren_buffett", "risk"])
        manifest = self._record(
            operation="create_research_run",
            mode=mode_n,
            selected_agents=selected,
            data_sources=list(fixture.get("data_sources") or ["fixture"]),
            model_versions=dict(fixture.get("model_versions") or {}),
            instruction_hashes=dict(fixture.get("instruction_hashes") or {}),
            results={
                "objective": objective,
                "status": "created",
                "fixture": True,
                "notes": fixture.get("notes"),
            },
        )
        return manifest.to_dict()

    def run_strategy_agents(
        self,
        *,
        run_id: str | None = None,
        mode: str = "research",
    ) -> dict[str, Any]:
        """Fixture-only in v1 — does not invoke a local AHF checkout."""
        mode_n = self._gate(mode)
        fixture = _load_json("strategy_agents.json", self.fixtures_dir)
        opinions = list(fixture.get("opinions") or [])
        manifest = self._record(
            operation="run_strategy_agents",
            mode=mode_n,
            selected_agents=[str(item.get("agent")) for item in opinions if item.get("agent")],
            data_sources=["fixture"],
            results={
                "parent_run_id": run_id,
                "opinions": opinions,
                "fixture": True,
                "local_invoke": False,
            },
        )
        return manifest.to_dict()

    def get_market_state(self, *, mode: str = "research") -> dict[str, Any]:
        mode_n = self._gate(mode)
        fixture = _load_json("market_state.json", self.fixtures_dir)
        manifest = self._record(
            operation="get_market_state",
            mode=mode_n,
            data_sources=list(fixture.get("data_sources") or ["fixture"]),
            results={"market": fixture.get("market") or fixture, "fixture": True},
        )
        return manifest.to_dict()

    def get_portfolio_state(self, *, mode: str = "paper") -> dict[str, Any]:
        mode_n = self._gate(mode)
        fixture = _load_json("portfolio_state.json", self.fixtures_dir)
        manifest = self._record(
            operation="get_portfolio_state",
            mode=mode_n,
            data_sources=["fixture"],
            results={"portfolio": fixture.get("portfolio") or fixture, "fixture": True},
        )
        return manifest.to_dict()

    def run_backtest(
        self,
        *,
        mode: str = "backtest",
        strategy: str = "baseline",
    ) -> dict[str, Any]:
        mode_n = self._gate(mode, extras={"strategy": strategy})
        fixture = _load_json("backtest.json", self.fixtures_dir)
        metrics = dict(fixture.get("metrics") or {})
        manifest = self._record(
            operation="run_backtest",
            mode=mode_n,
            selected_agents=list(fixture.get("agents") or []),
            data_sources=list(fixture.get("data_sources") or ["fixture"]),
            results={
                "strategy": strategy,
                "metrics": metrics,
                "fixture": True,
            },
        )
        return manifest.to_dict()

    def run_paper_session(
        self,
        *,
        mode: str = "paper",
        session_label: str = "default",
    ) -> dict[str, Any]:
        mode_n = self._gate(mode, extras={"session_label": session_label})
        fixture = _load_json("paper_session.json", self.fixtures_dir)
        manifest = self._record(
            operation="run_paper_session",
            mode=mode_n,
            selected_agents=list(fixture.get("agents") or []),
            data_sources=["fixture"],
            results={
                "session_label": session_label,
                "fills": list(fixture.get("fills") or []),
                "pnl": fixture.get("pnl"),
                "fixture": True,
            },
        )
        return manifest.to_dict()

    def get_decision_ledger(
        self,
        *,
        mode: str = "research",
        run_id: str | None = None,
    ) -> dict[str, Any]:
        mode_n = self._gate(mode)
        fixture = _load_json("decision_ledger.json", self.fixtures_dir)
        entries = list(fixture.get("entries") or [])
        if run_id:
            entries = [e for e in entries if e.get("run_id") == run_id] or entries
        manifest = self._record(
            operation="get_decision_ledger",
            mode=mode_n,
            data_sources=["fixture"],
            results={"entries": entries, "fixture": True, "filter_run_id": run_id},
        )
        return manifest.to_dict()

    def compare_runs(
        self,
        left: dict[str, Any],
        right: dict[str, Any],
        *,
        mode: str = "research",
    ) -> dict[str, Any]:
        mode_n = self._gate(mode)
        comparison = compare_runs(left, right)
        manifest = self._record(
            operation="compare_runs",
            mode=mode_n,
            data_sources=["fixture"],
            results={"comparison": comparison, "fixture": True},
        )
        return manifest.to_dict()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        manifest = self._runs.get(run_id)
        return manifest.to_dict() if manifest else None


def get_adapter(**kwargs: Any) -> AiHedgeFundAdapter:
    return AiHedgeFundAdapter(**kwargs)
