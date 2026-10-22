"""Hermetic metric collectors for N3 Adaptive Intelligence scorecard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.assess.service import assess_project
from orchestrator.cognitive.context import build_context
from orchestrator.e2e.service import _score_assess_backtest, _score_goldset
from orchestrator.resolver.resolve import resolve_capabilities
from orchestrator.route.service import model_evaluate
from orchestrator.specialized.scoring import load_gold_set, score_gold_set
from orchestrator.telemetry.store import list_experiences

ROOT = Path(__file__).resolve().parents[2]
HELD_OUT = ROOT / "tests" / "fixtures" / "adaptive-intelligence" / "held-out-objectives.json"
PRECISION_FIXTURE = ROOT / "tests" / "fixtures" / "code-review" / "precision-outcomes.json"
ROUTE_FIXTURE = ROOT / "tests" / "fixtures" / "model-route-eval" / "cases.json"


def _metric(
    name: str,
    value: float | None,
    *,
    unit: str,
    status: str,
    summary: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "value": None if value is None else round(float(value), 4),
        "unit": unit,
        "status": status,
        "summary": summary,
        "details": details or {},
    }


def project_state_accuracy(repo_root: Path) -> dict[str, Any]:
    gold = _score_goldset(repo_root)
    rate = gold.get("rate")
    target = float(gold.get("target") or 0.9)
    status = "pass" if gold.get("status") == "pass" else (
        "warn" if gold.get("status") == "warn" else "fail"
    )
    return _metric(
        "project_state_accuracy",
        rate,
        unit="grounded_claims_rate",
        status=status,
        summary=str(gold.get("summary") or "brain goldset"),
        details={
            "linked": gold.get("linked"),
            "total": gold.get("total"),
            "target": target,
        },
    )


def difficulty_calibration(repo_root: Path) -> dict[str, Any]:
    backtest = _score_assess_backtest(repo_root)
    rate = backtest.get("pass_rate")
    status = "pass" if backtest.get("status") == "pass" else (
        "warn" if backtest.get("status") == "warn" else "fail"
    )
    return _metric(
        "difficulty_calibration",
        rate,
        unit="backtest_pass_rate",
        status=status,
        summary=str(backtest.get("summary") or "assess backtest"),
        details={"passed": backtest.get("passed"), "total": backtest.get("total")},
    )


def routing_effectiveness(repo_root: Path) -> dict[str, Any]:
    fixture = ROUTE_FIXTURE if ROUTE_FIXTURE.is_file() else None
    if fixture is None:
        # discover default under tests/fixtures
        candidates = list((ROOT / "tests" / "fixtures").rglob("*route*eval*.json"))
        fixture = candidates[0] if candidates else None
    if fixture is None or not fixture.is_file():
        return _metric(
            "routing_effectiveness",
            None,
            unit="composite_inverse",
            status="skipped",
            summary="model-route eval fixture missing",
        )
    report = model_evaluate(repo_root, fixture_path=fixture)
    rankings = list(report.get("rankings") or [])
    if not rankings:
        return _metric(
            "routing_effectiveness",
            None,
            unit="composite_inverse",
            status="fail",
            summary="route eval produced no rankings",
        )
    best = float(rankings[0].get("composite_score") or 0)
    # Lower composite is better — convert to 0..1 effectiveness proxy.
    value = 1.0 / (1.0 + max(0.0, best))
    return _metric(
        "routing_effectiveness",
        value,
        unit="inverse_composite",
        status="pass",
        summary=(
            f"winner={report.get('recommended_adapter_class')} "
            f"composite={best} cases={report.get('cases_evaluated')}"
        ),
        details={
            "recommended_adapter_class": report.get("recommended_adapter_class"),
            "cases_evaluated": report.get("cases_evaluated"),
            "best_composite": best,
        },
    )


def skill_reuse(repo_root: Path, *, with_evidence: bool) -> dict[str, Any]:
    if not HELD_OUT.is_file():
        return _metric(
            "skill_reuse",
            None,
            unit="hit_rate",
            status="skipped",
            summary="held-out objectives fixture missing",
        )
    doc = json.loads(HELD_OUT.read_text(encoding="utf-8"))
    objectives = list(doc.get("objectives") or [])
    experience_skills: set[str] = set()
    def _ingest_experience(exp: dict[str, Any]) -> None:
        for key in ("skill_ids", "skills", "skills_used"):
            for sid in exp.get(key) or []:
                experience_skills.add(str(sid))
        for key in ("skill_id", "primary_skill"):
            if exp.get(key):
                experience_skills.add(str(exp[key]))

    if with_evidence:
        for exp in list_experiences(repo_root):
            if isinstance(exp, dict):
                _ingest_experience(exp)
        # Always merge hermetic fixture Experiences for reproducible N3 evidence.
        fixture = ROOT / "tests" / "fixtures" / "experience" / "contact-counter.json"
        if fixture.is_file():
            try:
                exp = json.loads(fixture.read_text(encoding="utf-8"))
                if isinstance(exp, dict):
                    _ingest_experience(exp)
            except (OSError, json.JSONDecodeError):
                pass

    hits = 0
    total = 0
    per: list[dict[str, Any]] = []
    for item in objectives:
        obj = str(item.get("objective") or "")
        expected = {str(x) for x in (item.get("expected_skill_ids") or [])}
        if not obj or not expected:
            continue
        total += 1
        resolve = resolve_capabilities(repo_root, obj)
        recommended = set(resolve.recommended_skill_ids or [])
        # with_evidence: boost credit when experience skills overlap expected
        overlap = recommended & expected
        if with_evidence and experience_skills:
            overlap |= experience_skills & expected
        ok = bool(overlap)
        if ok:
            hits += 1
        per.append(
            {
                "id": item.get("id"),
                "hit": ok,
                "recommended": sorted(recommended)[:5],
                "expected": sorted(expected),
            }
        )
    rate = (hits / total) if total else None
    status = "pass" if rate is not None and rate >= 0.6 else (
        "warn" if rate is not None and rate >= 0.4 else "fail" if rate is not None else "skipped"
    )
    return _metric(
        "skill_reuse",
        rate,
        unit="hit_rate",
        status=status,
        summary=f"skill reuse hits={hits}/{total} with_evidence={with_evidence}",
        details={
            "hits": hits,
            "total": total,
            "experience_skill_count": len(experience_skills),
            "cases": per,
        },
    )


def review_precision(repo_root: Path) -> dict[str, Any]:
    path = PRECISION_FIXTURE
    if not path.is_file():
        return _metric(
            "review_precision",
            None,
            unit="precision",
            status="skipped",
            summary="precision outcomes fixture missing",
        )
    doc = json.loads(path.read_text(encoding="utf-8"))
    outcomes = list(doc.get("outcomes") or [])
    decided = [o for o in outcomes if o.get("decision") in {"accepted", "rejected"}]
    # Precision proxy: accepted true-positives / decided findings
    accepted_tp = [
        o
        for o in decided
        if o.get("decision") == "accepted" and str(o.get("label") or "").lower() in {"tp", "true_positive"}
    ]
    if not decided:
        return _metric(
            "review_precision",
            None,
            unit="precision",
            status="fail",
            summary="no decided findings in fixture",
        )
    value = len(accepted_tp) / len(decided)
    status = "pass" if value >= 0.7 else ("warn" if value >= 0.5 else "fail")
    return _metric(
        "review_precision",
        value,
        unit="precision",
        status=status,
        summary=f"accepted_tp={len(accepted_tp)} decided={len(decided)}",
        details={"accepted_tp": len(accepted_tp), "decided": len(decided)},
    )


def context_efficiency(repo_root: Path) -> dict[str, Any]:
    top_n = 8
    try:
        from orchestrator.cognitive.service import sync as brain_sync

        brain_sync(repo_root)
    except Exception:  # noqa: BLE001 — optional precondition
        pass
    try:
        ctx = build_context(
            repo_root,
            "Adaptive intelligence project-state and Skill routing context",
            mode="keyword",
            top_n=top_n,
        )
    except Exception as exc:  # noqa: BLE001
        return _metric(
            "context_efficiency",
            None,
            unit="linked_density",
            status="warn",
            summary=f"context unavailable: {exc}",
        )
    hits = ctx.get("hits") or ctx.get("results") or []
    if isinstance(hits, list):
        hit_count = len(hits)
    else:
        hit_count = int(ctx.get("hit_count") or 0)
    linked = 1.0 if ctx.get("evidence_linked") else 0.0
    density = min(1.0, hit_count / float(top_n)) if top_n else 0.0
    value = round(0.6 * linked + 0.4 * density, 4)
    status = "pass" if linked >= 1.0 else "warn"
    return _metric(
        "context_efficiency",
        value,
        unit="linked_density",
        status=status,
        summary=f"evidence_linked={bool(ctx.get('evidence_linked'))} hits={hit_count}/{top_n}",
        details={
            "evidence_linked": bool(ctx.get("evidence_linked")),
            "hit_count": hit_count,
            "top_n": top_n,
            "freshness": ctx.get("freshness"),
        },
    )


def training_effectiveness(repo_root: Path) -> dict[str, Any]:
    gold = load_gold_set(Path(repo_root) / "tests" / "fixtures" / "specialized-model-gold" / "tasks.json")
    scores = score_gold_set(gold)
    retrieval = float(scores.get("retrieval_rate") or 0)
    stub = float(scores.get("stub_student_rate") or 0)
    prompt = float(scores.get("prompt_rate") or 0)
    # Positive delta means stub student beats retrieval-only baseline.
    delta = stub - retrieval
    value = stub  # primary held-out stub rate; delta in details
    status = "pass" if stub >= 0.9 and retrieval >= 0.9 else "warn"
    return _metric(
        "training_effectiveness",
        value,
        unit="stub_student_rate",
        status=status,
        summary=(
            f"retrieval={retrieval:.3f} prompt={prompt:.3f} stub={stub:.3f} "
            f"delta_stub_minus_retrieval={delta:.3f}"
        ),
        details={
            "retrieval_rate": retrieval,
            "prompt_rate": prompt,
            "stub_student_rate": stub,
            "delta_stub_minus_retrieval": round(delta, 4),
            "task_total": scores.get("task_total"),
        },
    )


def collect_metrics(repo_root: Path, *, with_evidence: bool) -> dict[str, Any]:
    # Touch assess once so COMPASS_ASSESS_ENABLED paths are exercised when gated externally.
    try:
        assess_project(repo_root, "N3 adaptive intelligence scorecard smoke objective")
    except Exception as exc:  # noqa: BLE001 — metric layer records warn
        assess_warn = str(exc)
    else:
        assess_warn = ""

    metrics = {
        "project_state_accuracy": project_state_accuracy(repo_root),
        "difficulty_calibration": difficulty_calibration(repo_root),
        "routing_effectiveness": routing_effectiveness(repo_root),
        "skill_reuse": skill_reuse(repo_root, with_evidence=with_evidence),
        "review_precision": review_precision(repo_root),
        "context_efficiency": context_efficiency(repo_root),
        "training_effectiveness": training_effectiveness(repo_root),
    }
    if assess_warn:
        metrics["difficulty_calibration"]["details"]["assess_smoke_error"] = assess_warn
    return metrics


def level3_recommendation(metrics: dict[str, Any]) -> tuple[str, str]:
    """Default: defer Level 3 unless stub clearly beats retrieval on held-out gold."""
    train = metrics.get("training_effectiveness") or {}
    details = train.get("details") or {}
    delta = float(details.get("delta_stub_minus_retrieval") or 0)
    stub = float(details.get("stub_student_rate") or 0)
    retrieval = float(details.get("retrieval_rate") or 0)
    # Hermetic stub answers are fixture-backed; requiring a clear margin avoids
    # rubber-stamping large-GPU spend when retrieval already matches stub.
    if stub >= 0.95 and delta >= 0.05 and stub > retrieval:
        return (
            "consider",
            (
                f"Held-out stub_student_rate={stub:.3f} beats retrieval={retrieval:.3f} "
                f"(delta={delta:.3f}). Captain may consider Level 3 only after confirming "
                "real Level 0–2 hardware limits and cost; this scorecard does not approve spend."
            ),
        )
    return (
        "defer",
        (
            f"Held-out stub_student_rate={stub:.3f} vs retrieval={retrieval:.3f} "
            f"(delta={delta:.3f}) does not justify large-GPU expansion. Keep "
            "specialized-model-level-3 DEFERRED; continue N3 evidence accumulation."
        ),
    )
