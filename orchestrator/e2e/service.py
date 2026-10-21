"""Compose C1–C7 Cognitive Core surfaces into one hermetic e2e report."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.assess.service import assess_project
from orchestrator.cognitive.context import build_context
from orchestrator.cognitive.git_facts import git_sha
from orchestrator.cognitive.service import status as brain_status
from orchestrator.cognitive.service import sync as brain_sync
from orchestrator.cycle.service import cycle_begin, cycle_checkpoint, cycle_close
from orchestrator.e2e.enabled import require_e2e_gates
from orchestrator.rea.service import investigate as rea_investigate
from orchestrator.route.service import model_evaluate, model_route
from orchestrator.schemas.validate import validate_document
from orchestrator.train_bridge.service import train_export, train_review

ROOT = Path(__file__).resolve().parents[2]
GOLDSET_PATH = ROOT / "tests" / "fixtures" / "brain-goldset" / "questions.json"
ASSESS_BACKTEST_PATH = ROOT / "tests" / "fixtures" / "assess-backtest" / "cases.json"
DEFAULT_OBJECTIVE = (
    "Hermetic Cognitive Core e2e evaluation across brain assess cycle route rea train"
)


class E2EServiceError(ValueError):
    """Operator-facing e2e errors."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _version(repo_root: Path) -> str:
    path = repo_root / "VERSION"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _is_evidence_linked(doc: dict[str, Any]) -> bool:
    return bool(doc.get("hits") or doc.get("decision_links"))


def _expect_satisfied(doc: dict[str, Any], expect: list[str]) -> bool:
    kinds: set[str] = set()
    if doc.get("hits"):
        kinds.add("knowledge")
        for hit in doc["hits"]:
            if hit.get("kind") == "decision":
                kinds.add("decision")
    if doc.get("decision_links"):
        kinds.add("decision")
    for cite in doc.get("citations") or []:
        kind = cite.get("kind")
        if kind in {"knowledge", "decision", "snapshot"}:
            kinds.add(str(kind))
    return set(expect).issubset(kinds)


def _authority_locked(doc: dict[str, Any]) -> bool:
    return (
        doc.get("approved_for_execution") is False
        and doc.get("authority_mutation") is False
    )


def _score_goldset(repo_root: Path) -> dict[str, Any]:
    if not GOLDSET_PATH.is_file():
        return {
            "status": "warn",
            "rate": None,
            "target": None,
            "linked": 0,
            "total": 0,
            "summary": "brain goldset fixture missing",
        }
    spec = json.loads(GOLDSET_PATH.read_text(encoding="utf-8"))
    questions = list(spec.get("questions") or [])
    target = float(spec.get("target_evidence_linked_rate") or 0.9)
    linked = 0
    expect_failures: list[str] = []
    for q in questions:
        doc = build_context(repo_root, q["query"], mode="keyword", top_n=10)
        ok = _is_evidence_linked(doc) and bool(doc.get("evidence_linked"))
        if ok:
            linked += 1
        if not _expect_satisfied(doc, list(q.get("expect") or [])):
            expect_failures.append(str(q.get("id") or "?"))
    rate = (linked / len(questions)) if questions else 0.0
    # Primary e2e baseline is evidence-linked rate (warn-only vs target).
    # Citation-kind expects are secondary — live repos may lack C2 fixture
    # knowledge seeds while still evidence-linking via ADR hits.
    expect_ok = (len(questions) - len(expect_failures)) / len(questions) if questions else 0.0
    status = "pass" if rate >= target else "warn"
    if expect_ok < 0.5:
        status = "warn"
    return {
        "status": status,
        "rate": round(rate, 4),
        "target": target,
        "linked": linked,
        "total": len(questions),
        "expect_ok_rate": round(expect_ok, 4),
        "expect_failures": expect_failures[:12],
        "summary": (
            f"goldset evidence-linked {linked}/{len(questions)} "
            f"({rate:.1%}; target {target:.0%}; "
            f"expect_kinds {expect_ok:.0%})"
        ),
    }


def _score_assess_backtest(repo_root: Path) -> dict[str, Any]:
    if not ASSESS_BACKTEST_PATH.is_file():
        return {
            "status": "warn",
            "pass_rate": None,
            "passed": 0,
            "total": 0,
            "summary": "assess backtest fixture missing",
        }
    spec = json.loads(ASSESS_BACKTEST_PATH.read_text(encoding="utf-8"))
    cases = list(spec.get("cases") or [])
    passed = 0
    misses: list[str] = []
    for case in cases:
        assessment = assess_project(repo_root, str(case.get("objective") or ""))
        band = str(assessment.get("band") or "")
        expected = list(case.get("expected_bands") or [])
        if band in expected:
            passed += 1
        else:
            misses.append(f"{case.get('id')} got={band} expected={expected}")
    total = len(cases)
    rate = (passed / total) if total else 0.0
    status = "pass" if rate >= 0.8 else "warn"
    return {
        "status": status,
        "pass_rate": round(rate, 4),
        "passed": passed,
        "total": total,
        "misses": misses[:8],
        "summary": f"assess backtest {passed}/{total} ({rate:.0%})",
    }


def _stage(
    stage_id: str,
    milestone: str,
    status: str,
    summary: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": stage_id,
        "milestone": milestone,
        "status": status,
        "summary": summary,
        "details": details or {},
    }


def run_cognitive_core_e2e(
    repo_root: Path,
    *,
    mode: str = "hermetic",
    objective: str | None = None,
    evidence_dir: Path | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    """Run gated C1–C7 composition and return a schema-validated report."""
    require_e2e_gates()
    repo_root = Path(repo_root).resolve()
    if mode not in {"hermetic", "sandbox"}:
        raise E2EServiceError("--mode must be hermetic or sandbox")
    obj = (objective or DEFAULT_OBJECTIVE).strip()
    stages: list[dict[str, Any]] = []
    warnings: list[str] = []
    baselines: dict[str, Any] = {
        "brain_goldset_rate": None,
        "brain_goldset_target": None,
        "assess_backtest_pass_rate": None,
        "route_eval_case_count": None,
        "cycle_authority_locked": False,
        "rea_claim_kinds_ok": False,
        "train_auto_uploaded": True,  # flipped false on success
    }

    # C1 — brain sync + status
    sync_doc = brain_sync(repo_root)
    snap = sync_doc.get("snapshot") or {}
    st = brain_status(repo_root)
    c1_ok = _authority_locked(st) and st.get("status") in {"ok", "no_snapshot"}
    stages.append(
        _stage(
            "c1-brain-sync",
            "C1",
            "pass" if c1_ok else "fail",
            f"brain sync freshness={sync_doc.get('freshness')} status={st.get('status')}",
            {
                "freshness": sync_doc.get("freshness"),
                "snapshot_id": snap.get("snapshot_id"),
                "status_freshness": st.get("freshness"),
            },
        )
    )
    if not c1_ok:
        warnings.append("C1 authority flags or status unexpected")

    # C2 — context sample + goldset baseline (warn-only thresholds)
    ctx = build_context(repo_root, "Cognitive Core project-state brain sync", mode="keyword", top_n=8)
    gold = _score_goldset(repo_root)
    baselines["brain_goldset_rate"] = gold.get("rate")
    baselines["brain_goldset_target"] = gold.get("target")
    if gold.get("status") == "warn":
        warnings.append(f"C2 goldset below target or expect misses: {gold.get('summary')}")
    stages.append(
        _stage(
            "c2-brain-context-goldset",
            "C2",
            "pass" if _authority_locked(ctx) and gold.get("status") in {"pass", "warn"} else "fail",
            f"context evidence_linked={bool(ctx.get('evidence_linked'))}; {gold.get('summary')}",
            {
                "context_freshness": ctx.get("freshness"),
                "evidence_linked": bool(ctx.get("evidence_linked")),
                "goldset": {
                    "rate": gold.get("rate"),
                    "target": gold.get("target"),
                    "linked": gold.get("linked"),
                    "total": gold.get("total"),
                    "expect_failures": gold.get("expect_failures") or [],
                },
            },
        )
    )

    # C3 — assess + backtest
    assessment = assess_project(repo_root, obj)
    backtest = _score_assess_backtest(repo_root)
    baselines["assess_backtest_pass_rate"] = backtest.get("pass_rate")
    if backtest.get("status") == "warn":
        warnings.append(f"C3 assess backtest: {backtest.get('summary')}")
    stages.append(
        _stage(
            "c3-assess",
            "C3",
            "pass" if _authority_locked(assessment) else "fail",
            (
                f"band={assessment.get('band')} score={assessment.get('difficulty_score')}; "
                f"{backtest.get('summary')}"
            ),
            {
                "assessment_id": assessment.get("assessment_id"),
                "band": assessment.get("band"),
                "difficulty_score": assessment.get("difficulty_score"),
                "confidence": assessment.get("confidence"),
                "backtest": {
                    "pass_rate": backtest.get("pass_rate"),
                    "passed": backtest.get("passed"),
                    "total": backtest.get("total"),
                    "misses": backtest.get("misses") or [],
                },
            },
        )
    )

    # C4 — cycle begin → checkpoint → close
    begun = cycle_begin(repo_root, obj, plan_id="e2e-cognitive-core-evaluation")
    execution_id = str(begun.get("execution_id") or "")
    checked = cycle_checkpoint(
        repo_root,
        execution_id,
        checkpoint_key="e2e-main",
        outcome="in_progress",
        retries=0,
        notes="hermetic e2e checkpoint",
    )
    closed = cycle_close(repo_root, execution_id, outcome="success")
    cycle_locked = (
        _authority_locked(begun)
        and _authority_locked(checked)
        and _authority_locked(closed)
        and closed.get("status") == "closed"
    )
    baselines["cycle_authority_locked"] = bool(cycle_locked)
    stages.append(
        _stage(
            "c4-cycle",
            "C4",
            "pass" if cycle_locked else "fail",
            f"cycle {execution_id} closed; authority_locked={cycle_locked}",
            {
                "execution_id": execution_id,
                "phase": closed.get("phase"),
                "status": closed.get("status"),
                "checkpoint_count": len(closed.get("checkpoints") or []),
            },
        )
    )
    if not cycle_locked:
        warnings.append("C4 cycle authority flags not locked false")

    # C5 — model route + evaluate
    proposal = model_route(repo_root, obj)
    eval_report = model_evaluate(repo_root)
    rankings = list(eval_report.get("rankings") or [])
    baselines["route_eval_case_count"] = int(
        eval_report.get("cases_evaluated") or len(rankings) or 0
    )
    c5_ok = _authority_locked(proposal) and _authority_locked(eval_report)
    if proposal.get("auto_switched") is not False:
        c5_ok = False
        warnings.append("C5 auto_switched unexpected")
    stages.append(
        _stage(
            "c5-model-route",
            "C5",
            "pass" if c5_ok else "fail",
            (
                f"adapter={proposal.get('adapter_class')} "
                f"eval_cases={baselines['route_eval_case_count']}"
            ),
            {
                "proposal_id": proposal.get("proposal_id"),
                "adapter_class": proposal.get("adapter_class"),
                "profile_id": proposal.get("profile_id"),
                "eval_case_count": baselines["route_eval_case_count"],
            },
        )
    )

    # C6 — REA fixture investigate
    packet = rea_investigate(
        repo_root,
        target="tests/fixtures/rea-evidence/sample-packet.json",
        question="Hermetic e2e: confirm fixture evidence packet claim kinds",
        mode="native",
        allow_live=False,
        checklist={
            "target_authorized": False,
            "license_reviewed": False,
            "execution_permitted": False,
            "source_docs_insufficient": False,
            "isolation_acknowledged": False,
        },
    )
    observations = list(packet.get("observations") or [])
    kinds = {
        str(item.get("claim_kind") or "")
        for item in observations
        if item.get("claim_kind")
    }
    has_observed = "observed" in kinds
    has_hypothesis = "hypothesis" in kinds
    # Prefer both kinds when present; still pass if authority locked + artifact hash.
    rea_kinds_ok = bool(kinds) and (has_observed or has_hypothesis)
    rea_ok = _authority_locked(packet) and bool(packet.get("artifact_hash")) and rea_kinds_ok
    baselines["rea_claim_kinds_ok"] = bool(rea_kinds_ok)
    if rea_ok and not (has_observed and has_hypothesis):
        warnings.append(
            f"C6 claim kinds incomplete (observed={has_observed}, "
            f"hypothesis={has_hypothesis}) — recorded as baseline note"
        )
    stages.append(
        _stage(
            "c6-rea",
            "C6",
            "pass" if rea_ok else "fail",
            f"rea packet claim_kinds={sorted(kinds)} artifact_hash={bool(packet.get('artifact_hash'))}",
            {
                "packet_id": packet.get("packet_id"),
                "claim_kinds": sorted(kinds),
                "run_mode": packet.get("run_mode"),
            },
        )
    )

    # C7 — train export + review (fixtures allowed)
    checklist = {
        "export_authorized": True,
        "secrets_redacted_ack": True,
        "license_reviewed": True,
        "pii_reviewed": True,
        "specialized_model_handoff_ack": True,
    }
    # Hermetic e2e: allow fixtures when the store is empty, and include
    # unreviewed recorded Experiences so control-repo smoke does not stall
    # when only unreviewed telemetry exists (explicit override for eval only).
    export = train_export(
        repo_root,
        source="experiences",
        checklist=checklist,
        allow_fixtures=True,
        include_unreviewed=True,
    )
    review = train_review(repo_root, export_id=str(export.get("export_id") or ""))
    train_ok = (
        _authority_locked(export)
        and _authority_locked(review)
        and export.get("auto_uploaded") is False
        and review.get("auto_uploaded") is False
    )
    baselines["train_auto_uploaded"] = bool(export.get("auto_uploaded"))
    stages.append(
        _stage(
            "c7-train-bridge",
            "C7",
            "pass" if train_ok else "fail",
            (
                f"export_id={export.get('export_id')} "
                f"trajectories={export.get('trajectory_count')} "
                f"auto_uploaded={export.get('auto_uploaded')}"
            ),
            {
                "export_id": export.get("export_id"),
                "run_mode": export.get("run_mode"),
                "trajectory_count": export.get("trajectory_count"),
                "ready_for_specialized_model": review.get("ready_for_specialized_model"),
            },
        )
    )
    if not train_ok:
        warnings.append("C7 train export/review authority or auto_uploaded unexpected")

    fail_count = sum(1 for s in stages if s["status"] == "fail")
    warn_count = sum(1 for s in stages if s["status"] == "warn") + (
        1 if warnings and fail_count == 0 else 0
    )
    if fail_count:
        overall = "fail"
    elif warn_count or warnings:
        overall = "warn"
    else:
        overall = "pass"

    head = git_sha(repo_root) or ""
    version = _version(repo_root)
    report_id = f"e2e-cc-{uuid4().hex[:10]}"
    evidence_path: str | None = None
    report: dict[str, Any] = {
        "schema_version": "1",
        "report_id": report_id,
        "mode": mode,
        "repository_sha": head,
        "northstar_version": version,
        "plan_id": "e2e-cognitive-core-evaluation",
        "stages": stages,
        "baselines": baselines,
        "warnings": warnings,
        "overall_status": overall,
        "evidence_path": None,
        "notes": (
            "Cognitive Core C1–C7 e2e report. Aspirational metric thresholds are "
            "warn-only. Never grants authority, uploads training data, or promotes weights."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_uploaded": False,
        "generated_at": _utc_now(),
    }

    if write_evidence:
        out_root = Path(evidence_dir) if evidence_dir else (
            repo_root / ".agent" / "evidence" / "e2e-cognitive-core-evaluation"
        )
        out_root.mkdir(parents=True, exist_ok=True)
        json_path = out_root / f"{report_id}.json"
        md_path = out_root / "SUMMARY.md"
        report["evidence_path"] = str(json_path)
        validate_document(report, "e2e-cognitive-core-report.schema.json")
        json_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        md_lines = [
            "# Cognitive Core E2E Summary",
            "",
            f"- report_id: `{report_id}`",
            f"- mode: `{mode}`",
            f"- overall_status: **{overall}**",
            f"- repository_sha: `{head}`",
            f"- northstar_version: `{version}`",
            "",
            "## Stages",
            "",
        ]
        for stage in stages:
            md_lines.append(
                f"- **{stage['milestone']}** `{stage['id']}` — {stage['status']}: "
                f"{stage['summary']}"
            )
        if warnings:
            md_lines.extend(["", "## Warnings", ""])
            for w in warnings:
                md_lines.append(f"- {w}")
        md_lines.extend(
            [
                "",
                "## Baselines",
                "",
                f"- brain_goldset_rate: {baselines.get('brain_goldset_rate')}",
                f"- assess_backtest_pass_rate: {baselines.get('assess_backtest_pass_rate')}",
                f"- route_eval_case_count: {baselines.get('route_eval_case_count')}",
                f"- cycle_authority_locked: {baselines.get('cycle_authority_locked')}",
                f"- train_auto_uploaded: {baselines.get('train_auto_uploaded')}",
                "",
            ]
        )
        md_path.write_text("\n".join(md_lines), encoding="utf-8")
        evidence_path = str(json_path)
        # keep latest pointer
        (out_root / "LATEST.json").write_text(
            json.dumps({"report_id": report_id, "path": evidence_path}, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        validate_document(report, "e2e-cognitive-core-report.schema.json")

    return report
