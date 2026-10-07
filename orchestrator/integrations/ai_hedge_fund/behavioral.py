"""AHF-P06 — couple portfolio experiment outcomes into behavior loop (proposal-only).

Ingests AHF-P05 ``experiment.json`` into ExecutionRun / Experience telemetry,
optionally runs M46 evaluate + M47 learn, and emits an execution-readiness
assessment. Never sets ``approved_for_execution: true``.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from orchestrator.telemetry.record import (
    build_execution_run,
    experience_from_run,
)
from orchestrator.telemetry.store import write_execution_run, write_experience

EVIDENCE_ROOT_REL = Path(".agent") / "evidence" / "ahf-p06-behavioral-coupling"
_SAFE_REL = re.compile(r"^[A-Za-z0-9._/-]+$")

# Hard maturity gates for live execution — all must pass AND Captain must
# explicitly approve. Confidence alone is never sufficient.
READINESS_GATES: tuple[tuple[str, str], ...] = (
    ("non_fixture_backtests", "Multi-period backtests on non-fixture market data"),
    ("paper_track_record", "Sustained paper-trading track record beyond a single session"),
    ("multiple_live_jev_runs", "Repeated live-Jev experiment runs with stable acceptance"),
    ("live_execution_path_absent", "No broker/wallet/signing path wired in NorthStar AHF"),
    ("kill_switch_and_limits", "Deterministic kill-switch + exposure limits for live mode"),
    ("security_review_live_path", "Security review of any proposed live execution surface"),
    ("captain_written_approval", "Captain written approval for approved_for_execution"),
)


def coupling_enabled() -> bool:
    raw = os.environ.get("COMPASS_AHF_BEHAVIOR_COUPLING_ENABLED", "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_experiment(path: Path | str) -> dict[str, Any]:
    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("experiment.json must be a JSON object")
    if "arms" not in payload or "acceptance" not in payload:
        raise ValueError("experiment.json missing arms/acceptance")
    return payload


def _outcome_from_acceptance(acceptance: Mapping[str, Any]) -> str:
    if acceptance.get("passed"):
        return "success"
    return "partial"


def _lessons_from_experiment(experiment: Mapping[str, Any]) -> list[str]:
    acc = dict(experiment.get("acceptance") or {})
    winner = acc.get("winner_arm")
    lessons = [
        f"AHF-P05 winner_arm={winner}",
        f"acceptance.passed={acc.get('passed')}",
        "proposal_only — do not treat as trade authority",
    ]
    ranking = (acc.get("comparison") or {}).get("ranking_by_return_then_sharpe")
    if ranking:
        lessons.append(f"ranking={','.join(str(x) for x in ranking)}")
    if experiment.get("approved_for_execution") is True:
        lessons.append("WARNING: source claimed approved_for_execution — coupling forces false")
    return lessons


def ingest_experiment_outcome(
    repo_root: Path,
    experiment_path: Path | str,
    *,
    require_enabled: bool = True,
    source_instance: str = "control-live",
) -> dict[str, Any]:
    """Write ExecutionRun + Experience from an AHF-P05 experiment report."""
    if require_enabled and not coupling_enabled():
        raise RuntimeError(
            "AHF behavior coupling disabled — set COMPASS_AHF_BEHAVIOR_COUPLING_ENABLED=1"
        )
    root = Path(repo_root).resolve()
    experiment_path = Path(experiment_path)
    experiment = load_experiment(experiment_path)
    acc = dict(experiment.get("acceptance") or {})
    exp_id = str(experiment.get("experiment_id") or experiment_path.parent.name)
    run = build_execution_run(
        plan_id="ahf-p06-behavioral-coupling",
        task_id="task-ahf-portfolio-experiment",
        objective=str(experiment.get("objective") or "AHF portfolio experiment"),
        outcome=_outcome_from_acceptance(acc),
        skills=["ai-hedge-fund-adapter", "onchain-analyst", "ahf-portfolio-experiment"],
        agents=list(
            ((experiment.get("arms") or {}).get(acc.get("winner_arm") or "baseline") or {}).get(
                "selected_agents"
            )
            or ["on_chain_analyst"]
        ),
        models=["jev-1.13.0"] if experiment.get("jev_shadow") else ["fixture"],
        provenance={
            "experiment_id": exp_id,
            "experiment_path": str(experiment_path),
            "winner_arm": acc.get("winner_arm"),
            "paper_session": bool(experiment.get("paper_session")),
            "branch": "ahf-p06-behavioral-coupling",
        },
        lessons=_lessons_from_experiment(experiment),
        run_id=f"run-ahf-{uuid4().hex[:10]}",
    )
    experience = experience_from_run(
        run,
        source_instance=source_instance,
        capabilities_exercised=[
            "ahf-adapter",
            "ahf-onchain-analyst",
            "ahf-portfolio-experiment",
            "ahf-jev-shadow",
        ],
    )
    run["experience_id"] = experience["experience_id"]
    run_path = write_execution_run(root, run)
    exp_path = write_experience(root, experience)
    return {
        "status": "ingested",
        "execution_id": run["run_id"],
        "experience_id": experience["experience_id"],
        "execution_run_path": str(run_path),
        "experience_path": str(exp_path),
        "experiment_id": exp_id,
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def couple_experiment_to_behavior(
    repo_root: Path,
    experiment_path: Path | str,
    *,
    require_enabled: bool = True,
    run_evaluate: bool = True,
    run_learn: bool = False,
) -> dict[str, Any]:
    """Ingest experiment then optionally evaluate / learn (proposal-only)."""
    root = Path(repo_root).resolve()
    ingested = ingest_experiment_outcome(
        root, experiment_path, require_enabled=require_enabled
    )
    evaluate_result: dict[str, Any] | None = None
    learn_result: dict[str, Any] | None = None
    evaluate_error: str | None = None
    learn_error: str | None = None

    if run_evaluate:
        try:
            from orchestrator.behavior.enabled import behavior_eval_enabled
            from orchestrator.behavior.service import evaluate_execution

            if behavior_eval_enabled():
                evaluate_result = evaluate_execution(root, ingested["execution_id"])
            else:
                evaluate_error = "COMPASS_BEHAVIOR_EVAL_ENABLED unset — evaluate skipped"
        except Exception as exc:  # noqa: BLE001 — surface to Captain evidence
            evaluate_error = str(exc)

    if run_learn:
        try:
            from orchestrator.behavior.enabled import behavior_learn_enabled
            from orchestrator.behavior.patterns.service import scan_and_persist

            if behavior_learn_enabled():
                learn_result = scan_and_persist(root)
            else:
                learn_error = "COMPASS_BEHAVIOR_LEARN_ENABLED unset — learn skipped"
        except Exception as exc:  # noqa: BLE001
            learn_error = str(exc)

    report = {
        "schema": "northstar.ahf_behavior_coupling.v1",
        "coupling_id": f"ahf-bc-{_utc_stamp()}-{uuid4().hex[:8]}",
        "created_at": _utc_now(),
        "plan_id": "ahf-p06-behavioral-coupling",
        "ingest": ingested,
        "evaluate": evaluate_result,
        "evaluate_error": evaluate_error,
        "learn": learn_result,
        "learn_error": learn_error,
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    return report


def assess_execution_readiness(
    repo_root: Path,
    experiment_path: Path | str | None = None,
    *,
    captain_reported_live_jev: bool = False,
) -> dict[str, Any]:
    """Evaluate whether confidence is strong enough for approved_for_execution.

    Returns a structured verdict. This function **never** recommends true under
    the current AHF foundation — fixture-backed research + shadow Jev is not
    live-trading authority.
    """
    root = Path(repo_root).resolve()
    experiment: dict[str, Any] | None = None
    experiment_path_resolved: str | None = None
    if experiment_path is not None and Path(experiment_path).is_file():
        experiment = load_experiment(experiment_path)
        experiment_path_resolved = str(experiment_path)

    checks: list[dict[str, Any]] = []

    def _add(gate_id: str, ok: bool, detail: str) -> None:
        label = dict(READINESS_GATES).get(gate_id, gate_id)
        checks.append({"gate": gate_id, "label": label, "ok": ok, "detail": detail})

    # 1) Non-fixture backtests — AHF adapter remains fixture-only
    _add(
        "non_fixture_backtests",
        False,
        "AHF adapter v1 is fixture-only; arm metrics are not live-market backtests",
    )

    # 2) Paper track record
    paper_ok = False
    paper_detail = "No sustained paper track record in control evidence"
    if experiment and experiment.get("paper_session"):
        paper_detail = (
            "Single paper_session present on experiment — insufficient duration/sample"
        )
    _add("paper_track_record", paper_ok, paper_detail)

    # 3) Multiple live Jev runs
    live_jev_ok = False
    if captain_reported_live_jev:
        detail = (
            "Captain reported one live-Jev experiment "
            "(exp-20261007T211148Z-23fa367a); need repeated stable runs"
        )
    else:
        detail = "No live-Jev experiment file available in this workspace"
    _add("multiple_live_jev_runs", live_jev_ok, detail)

    # 4) Live execution path must remain absent (pass = still absent)
    _add(
        "live_execution_path_absent",
        True,
        "No broker/wallet/signing path in AHF adapter policy (LiveExecutionDenied)",
    )

    # 5) Kill switch / limits for live — not implemented
    _add(
        "kill_switch_and_limits",
        False,
        "Live-mode kill-switch and exposure limits not implemented (research-only)",
    )

    # 6) Security review of live path — N/A until path exists; fail closed
    _add(
        "security_review_live_path",
        False,
        "No live execution surface to review; fail closed until designed + reviewed",
    )

    # 7) Captain written approval for execution — not granted
    _add(
        "captain_written_approval",
        False,
        "Captain asked to evaluate readiness; no written approval for live execution",
    )

    # Experiment acceptance is research signal only
    research_acceptance = None
    if experiment:
        research_acceptance = {
            "passed": bool((experiment.get("acceptance") or {}).get("passed")),
            "winner_arm": (experiment.get("acceptance") or {}).get("winner_arm"),
            "source_approved_for_execution": bool(
                experiment.get("approved_for_execution")
            ),
        }

    required_failures = [c for c in checks if not c["ok"]]
    # Explicit hard rule: never recommend true from this assessor in v1.54
    recommend = False
    confidence = "research_operable" if (
        research_acceptance and research_acceptance.get("passed")
    ) or captain_reported_live_jev else "insufficient_evidence"

    verdict = {
        "schema": "northstar.ahf_execution_readiness.v1",
        "assessment_id": f"ahf-ready-{_utc_stamp()}-{uuid4().hex[:8]}",
        "created_at": _utc_now(),
        "plan_id": "ahf-p06-behavioral-coupling",
        "experiment_path": experiment_path_resolved,
        "captain_reported_live_jev": captain_reported_live_jev,
        "research_acceptance": research_acceptance,
        "checks": checks,
        "failed_gates": [c["gate"] for c in required_failures],
        "confidence_band": confidence,
        "recommend_approved_for_execution": recommend,
        "approved_for_execution": False,
        "authority_mutation": False,
        "rationale": (
            "Research stack (P01–P05) is operable including live Jev shadow, but "
            "execution authority requires non-fixture performance evidence, "
            "sustained paper results, live risk controls, security review, and "
            "explicit Captain written approval. Current confidence is NOT strong "
            "enough to approve for execution."
        ),
        "northstar_version": (
            (root / "VERSION").read_text(encoding="utf-8").strip()
            if (root / "VERSION").is_file()
            else "unknown"
        ),
    }
    return verdict


def write_coupling_evidence(repo_root: Path, report: Mapping[str, Any]) -> Path:
    root = Path(repo_root)
    cid = str(report.get("coupling_id") or report.get("assessment_id") or uuid4().hex[:12])
    rel = EVIDENCE_ROOT_REL / cid
    abs_dir = root / rel
    abs_dir.mkdir(parents=True, exist_ok=True)
    name = "coupling.json" if "coupling_id" in report else "readiness.json"
    path = abs_dir / name
    payload = dict(report)
    payload["approved_for_execution"] = False
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_behavioral_coupling(
    repo_root: Path,
    experiment_path: Path | str,
    *,
    require_enabled: bool = True,
    run_evaluate: bool = True,
    run_learn: bool = False,
    captain_reported_live_jev: bool = False,
) -> dict[str, Any]:
    """Couple experiment → behavior path and emit readiness assessment."""
    root = Path(repo_root).resolve()
    coupling = couple_experiment_to_behavior(
        root,
        experiment_path,
        require_enabled=require_enabled,
        run_evaluate=run_evaluate,
        run_learn=run_learn,
    )
    readiness = assess_execution_readiness(
        root,
        experiment_path,
        captain_reported_live_jev=captain_reported_live_jev,
    )
    bundle = {
        "schema": "northstar.ahf_p06_bundle.v1",
        "created_at": _utc_now(),
        "coupling": coupling,
        "readiness": readiness,
        "approved_for_execution": False,
        "recommend_approved_for_execution": False,
    }
    evidence = write_coupling_evidence(root, {**coupling, "readiness": readiness})
    ready_path = write_coupling_evidence(root, readiness)
    bundle["coupling_evidence_path"] = str(evidence)
    bundle["readiness_evidence_path"] = str(ready_path)
    return bundle
