"""Deterministic compare_runs helpers for AHF adapter manifests."""

from __future__ import annotations

from typing import Any


def _metrics_from_manifest(payload: dict[str, Any]) -> dict[str, float]:
    results = payload.get("results") if isinstance(payload.get("results"), dict) else {}
    metrics = results.get("metrics") if isinstance(results.get("metrics"), dict) else {}
    out: dict[str, float] = {}
    for key, value in metrics.items():
        try:
            out[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    # Paper sessions may expose pnl instead of metrics.
    if "pnl" in results and "pnl" not in out:
        try:
            out["pnl"] = float(results["pnl"])
        except (TypeError, ValueError):
            pass
    return out


def compare_runs(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Compare two adapter run manifests / result payloads.

    Returns a structured, deterministic diff suitable for hermetic tests.
    """
    left_m = _metrics_from_manifest(left)
    right_m = _metrics_from_manifest(right)
    keys = sorted(set(left_m) | set(right_m))
    deltas: dict[str, float] = {}
    for key in keys:
        deltas[key] = round(right_m.get(key, 0.0) - left_m.get(key, 0.0), 6)

    return {
        "left_run_id": left.get("run_id"),
        "right_run_id": right.get("run_id"),
        "left_operation": left.get("operation"),
        "right_operation": right.get("operation"),
        "metric_deltas": deltas,
        "improved_keys": [k for k, v in deltas.items() if v > 0],
        "regressed_keys": [k for k, v in deltas.items() if v < 0],
        "unchanged_keys": [k for k, v in deltas.items() if v == 0],
        "approved_for_execution": False,
    }
