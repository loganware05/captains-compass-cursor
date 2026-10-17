"""Operator service for northstar model route|evaluate (C5)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.cognitive.git_facts import git_sha
from orchestrator.model_profiles import load_catalog
from orchestrator.route.enabled import require_route_enabled
from orchestrator.route.scoring import (
    ADAPTER_TO_PROFILE,
    expected_budget,
    fallback_chain,
    select_adapter_class,
)
from orchestrator.schemas.validate import validate_document


class RouteServiceError(ValueError):
    """Operator-facing routing errors."""


DEFAULT_EVAL_FIXTURE = Path(__file__).resolve().parents[2] / (
    "tests/fixtures/model-route-eval/cases.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _optional_brain(repo_root: Path) -> tuple[str | None, str | None, str | None]:
    """Return (freshness, snapshot_id, snapshot_sha)."""
    try:
        from orchestrator.cognitive.enabled import brain_enabled
        from orchestrator.cognitive.store import load_latest

        if not brain_enabled():
            return None, None, None
        snap = load_latest(repo_root)
        if not snap:
            return "no_snapshot", None, None
        head = git_sha(repo_root)
        snap_sha = str(snap.get("repository_sha") or "")
        freshness = "fresh" if head and snap_sha and head == snap_sha else "stale"
        if not snap_sha:
            freshness = "no_snapshot"
        return freshness, str(snap.get("snapshot_id") or "") or None, snap_sha or None
    except Exception:
        return None, None, None


def _optional_assessment(repo_root: Path, objective: str) -> dict[str, Any] | None:
    try:
        from orchestrator.assess.enabled import assess_enabled
        from orchestrator.assess.service import assess_project

        if not assess_enabled():
            return None
        return assess_project(repo_root, objective)
    except Exception:
        return None


def _intent_security(repo_root: Path, objective: str) -> tuple[bool, int]:
    try:
        from orchestrator.resolver.resolve import resolve_capabilities

        result = resolve_capabilities(repo_root, objective)
        return bool(result.intent.security_sensitive), len(result.capability_gaps)
    except Exception:
        return False, 0


def model_route(repo_root: Path, objective: str) -> dict[str, Any]:
    """Build a schema-validated model-route proposal (advisory only)."""
    require_route_enabled()
    repo_root = Path(repo_root).resolve()
    obj = (objective or "").strip()
    if not obj:
        raise RouteServiceError("--objective is required for model route")

    assessment = _optional_assessment(repo_root, obj)
    freshness, snapshot_id, snap_sha = _optional_brain(repo_root)
    security, gaps = _intent_security(repo_root, obj)
    if assessment is not None:
        gaps = max(gaps, len(assessment.get("capability_gaps") or []))

    band = str((assessment or {}).get("band") or "") or None
    score = (assessment or {}).get("difficulty_score")
    if score is not None:
        score = float(score)

    adapter_class, reasons = select_adapter_class(
        difficulty_band=band,
        difficulty_score=score,
        security_sensitive=security,
        freshness=freshness,
        gap_count=gaps,
        objective=obj,
    )
    profile_id = ADAPTER_TO_PROFILE[adapter_class]
    catalog = load_catalog()
    profiles = {p["id"]: p for p in catalog.get("profiles") or []}
    profile = profiles.get(profile_id) or {"id": profile_id, "class": profile_id}
    fallbacks = [
        {
            "adapter_class": fb,
            "profile_id": ADAPTER_TO_PROFILE[fb],
        }
        for fb in fallback_chain(adapter_class)
    ]

    head_sha = git_sha(repo_root) or snap_sha or ""
    version = _version(repo_root)
    citations: list[dict[str, str]] = []
    if head_sha:
        citations.append({"kind": "git", "ref": f"HEAD={head_sha}", "claim_kind": "observed"})
    if snapshot_id:
        citations.append({"kind": "snapshot", "ref": snapshot_id, "claim_kind": "observed"})
    if assessment and assessment.get("assessment_id"):
        citations.append(
            {
                "kind": "assessment",
                "ref": str(assessment["assessment_id"]),
                "claim_kind": "observed",
            }
        )
    citations.append(
        {"kind": "profile", "ref": profile_id, "claim_kind": "documented"}
    )
    if version:
        citations.append(
            {"kind": "version", "ref": f"VERSION={version}", "claim_kind": "observed"}
        )

    digest = hashlib.sha256(
        f"{obj}|{adapter_class}|{head_sha}".encode("utf-8")
    ).hexdigest()[:12]
    proposal_id = f"route-{digest}-{uuid4().hex[:6]}"

    payload: dict[str, Any] = {
        "schema_version": "1",
        "proposal_id": proposal_id,
        "objective": obj,
        "adapter_class": adapter_class,
        "profile_id": profile_id,
        "profile_class": str(profile.get("class") or profile_id),
        "rationale": reasons,
        "expected_budget": expected_budget(adapter_class),
        "fallbacks": fallbacks,
        "difficulty_band": band,
        "difficulty_score": score,
        "assessment_id": str((assessment or {}).get("assessment_id") or "") or None,
        "freshness": freshness,
        "repository_sha": head_sha,
        "snapshot_id": snapshot_id,
        "northstar_version": version,
        "citations": citations,
        "notes": (
            "Cognitive Core C5 model-route proposal. Advisory only — "
            "does not bind Cursor models, spend cloud budget, or grant authority."
        ),
        "auto_switched": False,
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }
    validate_document(payload, "model-route-proposal.schema.json")
    return payload


def model_evaluate(
    repo_root: Path,
    *,
    fixture_path: Path | None = None,
) -> dict[str, Any]:
    """Hermetic evaluate of adapter classes on cost/quality proxies."""
    require_route_enabled()
    repo_root = Path(repo_root).resolve()
    path = Path(fixture_path) if fixture_path else DEFAULT_EVAL_FIXTURE
    if not path.is_file():
        raise RouteServiceError(f"evaluate fixture not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    cases = list(raw.get("cases") or [])
    if not cases:
        raise RouteServiceError("evaluate fixture has no cases")

    ranked: list[dict[str, Any]] = []
    for case in cases:
        adapter = str(case.get("adapter_class") or "")
        # Lower is better: cost per accepted task, inflated by retries and corrections.
        cost = float(case.get("cost_per_accepted_task") or 0)
        retries = float(case.get("retries") or 0)
        test_pass = float(case.get("test_pass_rate") or 0)
        corrections = float(case.get("human_correction_hours") or 0)
        quality_penalty = (1.0 - max(0.0, min(1.0, test_pass))) * 50.0
        composite = cost + (retries * 5.0) + (corrections * 20.0) + quality_penalty
        ranked.append(
            {
                "adapter_class": adapter,
                "profile_id": str(
                    case.get("profile_id") or ADAPTER_TO_PROFILE.get(adapter, "")
                ),
                "cost_per_accepted_task": cost,
                "retries": retries,
                "test_pass_rate": test_pass,
                "human_correction_hours": corrections,
                "composite_score": round(composite, 4),
                "label": str(case.get("label") or adapter),
            }
        )
    ranked.sort(key=lambda row: (row["composite_score"], row["adapter_class"]))
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index

    winner = ranked[0] if ranked else None
    digest = hashlib.sha256(
        f"eval|{path.name}|{len(ranked)}".encode("utf-8")
    ).hexdigest()[:12]
    payload: dict[str, Any] = {
        "schema_version": "1",
        "report_id": f"route-eval-{digest}-{uuid4().hex[:6]}",
        "fixture_path": str(path),
        "cases_evaluated": len(ranked),
        "rankings": ranked,
        "recommended_adapter_class": (winner or {}).get("adapter_class"),
        "metric_notes": (
            "composite = cost_per_accepted_task + 5*retries + 20*human_correction_hours "
            "+ 50*(1-test_pass_rate). Lower is better. Hermetic fixture only."
        ),
        "northstar_version": _version(repo_root),
        "citations": [
            {"kind": "fixture", "ref": str(path), "claim_kind": "observed"}
        ],
        "notes": (
            "Cognitive Core C5 hermetic model-route evaluate. "
            "Does not call live models or change bindings."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "generated_at": _utc_now(),
    }
    validate_document(payload, "model-route-eval-report.schema.json")
    return payload
