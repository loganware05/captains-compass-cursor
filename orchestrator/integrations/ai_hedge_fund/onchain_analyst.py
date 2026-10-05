"""On-Chain Analyst — normalized features → evidence-referenced signals (AHF-P04).

Consumes the AHF-P03 / bitcoin-data-collector on-chain schema shape (or a compact
subset). Never grants ``approved_for_execution``. Deterministic rules first;
optional Jev triage remains behind ``COMPASS_DECISION_AHF_SHADOW``.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

DEFAULT_FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "onchain_normalized_btc.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass
class EvidenceRef:
    label: str
    path: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OnChainAnalysis:
    asset: str
    signal: str  # bullish | bearish | neutral | uncertain
    confidence: float
    netflow_btc: float | None
    drivers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    evidence: list[EvidenceRef] = field(default_factory=list)
    provider: str | None = None
    freshness_seconds: float | None = None
    coverage: float | None = None
    analysis_id: str = field(default_factory=lambda: f"oca-{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=_utc_now)
    approved_for_execution: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["approved_for_execution"] = False
        return payload

    def to_jev_state(self) -> dict[str, Any]:
        """Compact state for AHF-P02 signal triage."""
        return {
            "price_change_24h": None,
            "exchange_netflow": self.netflow_btc,
            "agent_votes": {"on_chain": self.signal},
        }


def load_normalized_onchain(
    source: Mapping[str, Any] | Path | str | None = None,
) -> dict[str, Any]:
    """Load from mapping, snapshot JSON path, or default fixture."""
    if source is None:
        source = DEFAULT_FIXTURE
    if isinstance(source, (str, Path)):
        path = Path(source)
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError("on-chain source must be a JSON object")
        # Allow full collector snapshot or compact on_chain_data blob.
        if "on_chain_data" in payload and isinstance(payload["on_chain_data"], dict):
            data = dict(payload["on_chain_data"])
            data["_source_path"] = str(path)
            return data
        data = dict(payload)
        data["_source_path"] = str(path)
        return data
    data = dict(source)
    if "on_chain_data" in data and isinstance(data["on_chain_data"], dict):
        return dict(data["on_chain_data"])
    return data


class OnChainAnalyst:
    """Deterministic on-chain analyst over normalized features."""

    name = "onchain_analyst"

    def analyze(
        self,
        source: Mapping[str, Any] | Path | str | None = None,
        *,
        asset: str = "BTC",
    ) -> OnChainAnalysis:
        data = load_normalized_onchain(source)
        inflow = _safe_float(data.get("exchange_inflow_btc"))
        outflow = _safe_float(data.get("exchange_outflow_btc"))
        netflow = _safe_float(data.get("exchange_netflow_btc"))
        if netflow is None and inflow is not None and outflow is not None:
            netflow = inflow - outflow

        freshness = _safe_float(data.get("exchange_flow_freshness_seconds"))
        coverage = _safe_float(data.get("exchange_flow_coverage"))
        provider = data.get("exchange_flow_provider")
        source_path = str(
            data.get("exchange_flow_source")
            or data.get("_source_path")
            or "on_chain_data"
        )

        drivers: list[str] = []
        warnings: list[str] = []
        evidence: list[EvidenceRef] = []

        if netflow is None:
            warnings.append("exchange_netflow unavailable")
            signal = "uncertain"
            confidence = 0.2
        else:
            evidence.append(
                EvidenceRef(
                    label="exchange_netflow_btc",
                    path=source_path,
                    note=f"netflow={netflow}",
                )
            )
            # Convention: negative netflow = net leaving exchanges → mild bullish.
            if netflow < -1000:
                signal = "bullish"
                confidence = 0.65 if (coverage or 0) >= 0.8 else 0.5
                drivers.append(f"Net exchange outflow {netflow:.1f} BTC")
            elif netflow > 1000:
                signal = "bearish"
                confidence = 0.65 if (coverage or 0) >= 0.8 else 0.5
                drivers.append(f"Net exchange inflow {netflow:.1f} BTC")
            else:
                signal = "neutral"
                confidence = 0.45
                drivers.append(f"Exchange netflow near flat ({netflow:.1f} BTC)")

        if freshness is not None and freshness > 86400:
            warnings.append(f"stale exchange-flow data ({freshness:.0f}s)")
            confidence = max(0.15, confidence - 0.15)
            if signal in {"bullish", "bearish"}:
                signal = "uncertain"

        tx = _safe_float(data.get("transaction_count"))
        if tx is not None and tx > 0:
            drivers.append(f"tx_count={tx:.0f}")
            evidence.append(
                EvidenceRef(label="transaction_count", path=source_path, note=str(tx))
            )

        if provider:
            evidence.append(
                EvidenceRef(
                    label="exchange_flow_provider",
                    path=source_path,
                    note=str(provider),
                )
            )

        return OnChainAnalysis(
            asset=asset,
            signal=signal,
            confidence=round(confidence, 3),
            netflow_btc=netflow,
            drivers=drivers,
            warnings=warnings,
            evidence=evidence,
            provider=str(provider) if provider else None,
            freshness_seconds=freshness,
            coverage=coverage,
        )


def compose_with_ahf(
    analysis: OnChainAnalysis,
    *,
    research_manifest: Mapping[str, Any] | None = None,
    jev_shadow_ref: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose analyst output with optional AHF run + Jev shadow (record-only)."""
    return {
        "schema": "northstar.ahf_onchain_compose.v1",
        "analysis": analysis.to_dict(),
        "ahf_research_run_id": (research_manifest or {}).get("run_id"),
        "ahf_selected_agents": list((research_manifest or {}).get("selected_agents") or []),
        "jev_shadow": dict(jev_shadow_ref) if jev_shadow_ref else None,
        "approved_for_execution": False,
        "authority_mutation": False,
        "created_at": _utc_now(),
    }


def write_analysis_evidence(
    repo_root: Path,
    analysis: OnChainAnalysis,
    *,
    composed: Mapping[str, Any] | None = None,
    plan_id: str = "ahf-p04-onchain-analyst",
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    run_id = f"{analysis.analysis_id}"
    rel_dir = Path(".agent") / "evidence" / "ahf-p04-onchain-analyst" / run_id
    abs_dir = repo_root / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "northstar.ahf_onchain_analyst.v1",
        "plan_id_ref": plan_id,
        "analysis": analysis.to_dict(),
        "composed": dict(composed) if composed else None,
    }
    path = abs_dir / "analysis.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {
        "analysis_id": analysis.analysis_id,
        "evidence_path": str(rel_dir / "analysis.json"),
        "applied": False,
    }
