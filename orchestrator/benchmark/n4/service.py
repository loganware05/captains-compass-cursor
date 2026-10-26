"""N4 benchmark service — hermetic (default) and gated live scaffolding."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.benchmark.n4.enabled import (
    n4_live_implement_enabled,
    require_n4_gate,
)
from orchestrator.benchmark.n4.metrics import (
    primary_efficiency,
    simulate_task_result,
    summarize_arm,
)
from orchestrator.benchmark.n4.tasks import (
    TaskPackError,
    load_task_pack,
    seeded_order,
    stack_summary,
)
from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA = "n4-benchmark-report.schema.json"
SCHEMA_VERSION = "1"
PLAN_ID = "n4-cross-stack-benchmark"
DEFAULT_SEED = 20261026


class N4ServiceError(ValueError):
    """Operator-facing N4 errors."""


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _version(repo_root: Path) -> str:
    path = Path(repo_root) / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _git_sha(repo_root: Path) -> str:
    head = Path(repo_root) / ".git" / "HEAD"
    if not head.is_file():
        return ""
    try:
        raw = head.read_text(encoding="utf-8").strip()
        if raw.startswith("ref:"):
            ref = raw.split(" ", 1)[1].strip()
            ref_path = Path(repo_root) / ".git" / ref
            if ref_path.is_file():
                return ref_path.read_text(encoding="utf-8").strip()[:40]
        return raw[:40]
    except OSError:
        return ""


def _report_id(mode: str) -> str:
    digest = hashlib.sha256(
        f"{mode}|{_utc_now()}|{uuid4().hex}".encode()
    ).hexdigest()[:12]
    return f"n4-{mode}-{digest}"


def _evidence_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "n4-cross-stack-benchmark"


def run_n4_benchmark(
    repo_root: Path,
    *,
    mode: str = "hermetic",
    seed: int = DEFAULT_SEED,
    persist: bool = True,
    fixture_dir: Path | None = None,
) -> dict[str, Any]:
    require_n4_gate()
    repo_root = Path(repo_root).resolve()
    mode_n = (mode or "hermetic").strip().lower()
    if mode_n not in {"hermetic", "live"}:
        raise N4ServiceError("--mode must be hermetic|live")

    if mode_n == "live" and n4_live_implement_enabled():
        raise N4ServiceError(
            "COMPASS_N4_LIVE_IMPLEMENT=1 is reserved for a separate Captain "
            "approval; v1.75.0 evaluate-only harness refuses live implement"
        )

    if mode_n == "live":
        # Live evaluate scaffolding: still uses hermetic task outcomes unless
        # operator supplies future adapters; refuse silent remote clones.
        allow = (os.environ.get("COMPASS_N4_STACK_ROOTS") or "").strip()
        if not allow:
            raise N4ServiceError(
                "live mode requires COMPASS_N4_STACK_ROOTS=stack_id=/abs/path,... "
                "(Captain-local checkouts only; no silent clone). "
                "Use --mode hermetic for CI."
            )

    try:
        tasks = load_task_pack(fixture_dir)
    except TaskPackError as exc:
        raise N4ServiceError(str(exc)) from exc

    ordered = seeded_order(tasks, seed)
    baseline_results = [
        simulate_task_result(t, arm="baseline") for t in ordered
    ]
    evidence_results = [
        simulate_task_result(t, arm="evidence") for t in ordered
    ]

    baseline_arm = summarize_arm(baseline_results)
    evidence_arm = summarize_arm(evidence_results)

    primary_b = primary_efficiency(baseline_arm)
    primary_e = primary_efficiency(evidence_arm)

    secondary = {
        "accept_rate": {
            "baseline": baseline_arm["accept_rate"],
            "evidence": evidence_arm["accept_rate"],
            "unit": "rate",
            "summary": "Accepted tasks / total",
        },
        "first_pass_test_rate": {
            "baseline": baseline_arm["first_pass_test_rate"],
            "evidence": evidence_arm["first_pass_test_rate"],
            "unit": "rate",
        },
        "skill_reuse_rate": {
            "baseline": baseline_arm["skill_reuse_rate"],
            "evidence": evidence_arm["skill_reuse_rate"],
            "unit": "rate",
        },
        "retrieval_precision": {
            "baseline": baseline_arm["retrieval_precision"],
            "evidence": evidence_arm["retrieval_precision"],
            "unit": "rate",
        },
        "review_precision": {
            "baseline": baseline_arm["review_precision"],
            "evidence": evidence_arm["review_precision"],
            "unit": "rate",
        },
        "latency_p95_ms": {
            "baseline": baseline_arm["latency_p95_ms"],
            "evidence": evidence_arm["latency_p95_ms"],
            "unit": "ms",
        },
        "retries": {
            "baseline": baseline_arm["retries"],
            "evidence": evidence_arm["retries"],
            "unit": "mean",
        },
    }

    deltas: dict[str, float | None] = {
        "primary_efficiency": (
            None
            if primary_b is None or primary_e is None
            else round(primary_e - primary_b, 6)
        ),
        "accept_rate": round(
            evidence_arm["accept_rate"] - baseline_arm["accept_rate"], 4
        ),
        "skill_reuse_rate": round(
            evidence_arm["skill_reuse_rate"] - baseline_arm["skill_reuse_rate"], 4
        ),
        "retrieval_precision": round(
            evidence_arm["retrieval_precision"] - baseline_arm["retrieval_precision"],
            4,
        ),
    }

    held_ids = [t["task_id"] for t in ordered if t.get("held_out")]
    held_b = [r for r in baseline_results if r["held_out"]]
    held_e = [r for r in evidence_results if r["held_out"]]
    held_b_rate = (
        sum(1 for r in held_b if r["accepted"]) / len(held_b) if held_b else None
    )
    held_e_rate = (
        sum(1 for r in held_e if r["accepted"]) / len(held_e) if held_e else None
    )
    transfer = (
        None
        if held_b_rate is None or held_e_rate is None
        else round(held_e_rate - held_b_rate, 4)
    )

    uncertainty = [
        f"Sample size n={len(ordered)} tasks (hermetic fixtures); not production proof.",
        "Inference/engineering costs are fixture proxy units, not invoices.",
        "Verdant.sys substituted by captain-compass-sandbox in hermetic stack table.",
        "bitcoin-data-collector pin is M35 NorthStar install branch, not default feature branch.",
    ]
    if mode_n == "live":
        uncertainty.append(
            "Live mode evaluate scaffolding only; outcomes still fixture-driven in v1.75.0."
        )

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "report_id": _report_id(mode_n),
        "plan_id": PLAN_ID,
        "created_at": _utc_now(),
        "mode": mode_n,
        "seed": int(seed),
        "repository_sha": _git_sha(repo_root),
        "northstar_version": _version(repo_root),
        "frozen_config": {
            "model_proxy": "hermetic-fixture-v1",
            "tool_config": "northstar-evaluate-only",
            "evidence_gates": (
                "baseline=off; evidence=brain/assess/Experiences simulated via fixture boost"
            ),
        },
        "stacks": stack_summary(),
        "task_count": len(ordered),
        "primary_outcome": {
            "name": "accepted_per_cost",
            "baseline": primary_b,
            "evidence": primary_e,
            "unit": "accepted/(inference+engineering)",
            "summary": (
                "Primary efficiency under no security/authorization regression; "
                "proxy cost units only."
            ),
        },
        "secondary_outcomes": secondary,
        "arms": {"baseline": baseline_arm, "evidence": evidence_arm},
        "deltas": deltas,
        "held_out": {
            "task_ids": held_ids,
            "baseline_accept_rate": (
                None if held_b_rate is None else round(held_b_rate, 4)
            ),
            "evidence_accept_rate": (
                None if held_e_rate is None else round(held_e_rate, 4)
            ),
            "transfer_delta": transfer,
        },
        "uncertainty_notes": uncertainty,
        "security_regression": False,
        "warnings": [],
        "evidence_path": None,
        "notes": (
            "N4 Cross-Stack Benchmark. Evaluate-only. Does not promote Skills/policies, "
            "approve plans, or authorize Level 3 GPU spend."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_applied": False,
        "policy_promoted": False,
    }

    try:
        validate_document(report, SCHEMA)
    except ValidationError as exc:
        raise N4ServiceError(f"n4 report schema validation failed: {exc}") from exc

    if persist:
        out_dir = _evidence_dir(repo_root)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{report['report_id']}.json"
        latest = out_dir / f"LATEST_{mode_n}.json"
        report["evidence_path"] = str(path)
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        path.write_text(text, encoding="utf-8")
        latest.write_text(text, encoding="utf-8")
        # detail lanes for debugging (not schema-gated)
        (out_dir / f"{report['report_id']}-baseline-results.json").write_text(
            json.dumps(baseline_results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (out_dir / f"{report['report_id']}-evidence-results.json").write_text(
            json.dumps(evidence_results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        validate_document(report, SCHEMA)
    return report
