"""Hermetic eight-pillar readiness vs NorthStar effectiveness assessor (XRV W2)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.xrv.readiness_gates import require_xrv_readiness_enabled

PILLAR_DEFS: list[tuple[str, str, list[tuple[str, str, list[str]]]]] = [
    (
        "style_validation",
        "Style & validation",
        [
            ("hooks_json", "Cursor hooks policy", [".cursor/hooks.json"]),
            ("doctor_script", "Doctor script", ["scripts/doctor.sh"]),
        ],
    ),
    (
        "build_systems",
        "Build systems",
        [
            ("ci_workflow", "Control CI workflow", [".github/workflows/ci.yml"]),
            ("install_script", "Installer", ["scripts/install.sh"]),
        ],
    ),
    (
        "testing",
        "Testing",
        [
            ("tests_runner", "Automated test runner", ["tests/run.sh"]),
            ("testing_md", "TESTING.md", ["TESTING.md"]),
        ],
    ),
    (
        "documentation",
        "Documentation",
        [
            ("agents_md", "AGENTS.md", ["AGENTS.md"]),
            ("project_context", "PROJECT_CONTEXT.md", ["PROJECT_CONTEXT.md"]),
            ("readme", "README.md", ["README.md"]),
        ],
    ),
    (
        "development_environments",
        "Development environments",
        [
            ("cursor_skills", "Cursor Skills tree", [".cursor/skills"]),
            ("update_script", "Update script", ["scripts/update.sh"]),
        ],
    ),
    (
        "code_quality",
        "Code quality",
        [
            ("code_reviewer_skill", "Code reviewer Skill", [".cursor/skills/code-reviewer/SKILL.md"]),
            ("plan_gate_rule", "Plan approval rule", [".cursor/rules/01-plan-approval-gate.mdc"]),
        ],
    ),
    (
        "observability",
        "Observability",
        [
            ("evidence_dir", "Evidence directory", [".agent/evidence"]),
            ("evidence_matrix", "Evidence matrix", ["docs/EVIDENCE_MATRIX.md"]),
        ],
    ),
    (
        "security_governance",
        "Security & governance",
        [
            ("implementation_plan", "IMPLEMENTATION_PLAN.md", ["IMPLEMENTATION_PLAN.md"]),
            ("decisions", "DECISIONS.md", ["DECISIONS.md"]),
            ("secret_hook", "Secret protection hook", [".cursor/hooks/secret-protection.sh"]),
        ],
    ),
]

EFFECTIVENESS_SIGNALS: list[tuple[str, str, list[str]]] = [
    (
        "eer_schema",
        "Experience Evidence Record schema",
        ["orchestrator/schemas/experience-evidence-record.schema.json"],
    ),
    (
        "eer_fixture",
        "I6 EER fixture",
        [".agent/evidence/xrv/eer-i6-cross-provider-fixture.json"],
    ),
    (
        "i6_scorecard_schema",
        "I6 scorecard schema",
        ["orchestrator/schemas/i6-cross-provider-scorecard.schema.json"],
    ),
    (
        "xrv_program_docs",
        "XRV program plan",
        ["docs/plans/XRV_CROSS_REPOSITORY_VALIDATION.md"],
    ),
    (
        "release_drift_module",
        "Release drift checker",
        ["orchestrator/xrv/release_drift.py"],
    ),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha(repo_root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _probe_paths(repo_root: Path, rels: list[str]) -> tuple[str, list[str], float | None]:
    found: list[str] = []
    for rel in rels:
        path = repo_root / rel
        if path.exists():
            found.append(rel)
    if found:
        return "present", found, 100.0
    return "missing", [f"missing:{r}" for r in rels], None


def _avg(scores: list[float]) -> float | None:
    if not scores:
        return None
    return round(sum(scores) / len(scores), 2)


def _load_schema(repo_root: Path) -> dict[str, Any]:
    path = (
        Path(repo_root)
        / "orchestrator"
        / "schemas"
        / "xrv-readiness-scorecard.schema.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(repo_root: Path, doc: dict[str, Any]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        for key in (
            "approved_for_execution",
            "authority_mutation",
            "auto_promoted",
            "scores_invented",
        ):
            if doc.get(key) is not False:
                raise ValueError(f"{key} must be false")
        return
    jsonschema.validate(instance=doc, schema=_load_schema(repo_root))


def _build_pillars(repo_root: Path) -> list[dict[str, Any]]:
    pillars: list[dict[str, Any]] = []
    for pillar_id, label, signal_defs in PILLAR_DEFS:
        signals: list[dict[str, Any]] = []
        present_scores: list[float] = []
        for signal_id, signal_label, paths in signal_defs:
            status, evidence, score = _probe_paths(repo_root, paths)
            if score is not None:
                present_scores.append(score)
            signals.append(
                {
                    "signal_id": signal_id,
                    "label": signal_label,
                    "status": status,
                    "score": score,
                    "evidence": evidence,
                }
            )
        if present_scores:
            pillar_status = "scored"
            pillar_score = _avg(present_scores)
        else:
            pillar_status = "unscored"
            pillar_score = None
        pillars.append(
            {
                "pillar_id": pillar_id,
                "label": label,
                "status": pillar_status,
                "score": pillar_score,
                "signals": signals,
            }
        )
    return pillars


def _build_effectiveness(repo_root: Path) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    present_scores: list[float] = []
    for signal_id, label, paths in EFFECTIVENESS_SIGNALS:
        status, evidence, score = _probe_paths(repo_root, paths)
        if score is not None:
            present_scores.append(score)
        signals.append(
            {
                "signal_id": signal_id,
                "label": label,
                "status": status,
                "score": score,
                "evidence": evidence,
            }
        )
    scored = len(present_scores)
    unscored = len(signals) - scored
    overall = _avg(present_scores)
    if scored == 0:
        overall_status = "unscored"
    elif unscored == 0 and overall is not None and overall >= 80:
        overall_status = "effective"
    elif scored > 0:
        overall_status = "partial"
    else:
        overall_status = "blocked"
    return {
        "overall_status": overall_status,
        "overall_score": overall,
        "scored_count": scored,
        "unscored_count": unscored,
        "signals": signals,
    }


def _readiness_rollup(pillars: list[dict[str, Any]]) -> dict[str, Any]:
    scored_scores = [
        float(p["score"])
        for p in pillars
        if p.get("status") == "scored" and p.get("score") is not None
    ]
    scored_count = len(scored_scores)
    unscored_count = len(pillars) - scored_count
    overall = _avg(scored_scores)
    if scored_count == 0:
        overall_status = "unscored"
    elif unscored_count == 0 and overall is not None and overall >= 80:
        overall_status = "ready"
    elif scored_count > 0:
        overall_status = "partial"
    else:
        overall_status = "blocked"
    return {
        "overall_status": overall_status,
        "overall_score": overall,
        "scored_count": scored_count,
        "unscored_count": unscored_count,
        "pillars": pillars,
    }


def assess_readiness(
    repo_root: Path,
    *,
    require_gate: bool = True,
    write_evidence: bool = True,
) -> dict[str, Any]:
    """Run hermetic readiness assessment. Never invents scores or grants authority."""
    if require_gate:
        require_xrv_readiness_enabled()
    root = Path(repo_root)
    sha = _git_sha(root)
    pillars = _build_pillars(root)
    readiness = _readiness_rollup(pillars)
    effectiveness = _build_effectiveness(root)
    blob = json.dumps(
        {"sha": sha, "readiness": readiness, "effectiveness": effectiveness},
        sort_keys=True,
    )
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]
    scorecard: dict[str, Any] = {
        "schema_version": "xrv-readiness-1",
        "scorecard_id": f"xrv-ready-{digest}",
        "created_at": _utc_now(),
        "repository_sha": sha,
        "repo_path": str(root),
        "mode": "hermetic",
        "summary": (
            f"readiness={readiness['overall_status']} "
            f"({readiness['scored_count']}/8 pillars scored); "
            f"effectiveness={effectiveness['overall_status']} "
            f"({effectiveness['scored_count']} signals scored)"
        ),
        "repository_readiness": readiness,
        "northstar_effectiveness": effectiveness,
        "notes": (
            "Hermetic path probes only. Missing paths yield unscored signals — "
            "scores are never invented. Separate readiness vs effectiveness."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "scores_invented": False,
    }
    _validate(root, scorecard)
    result: dict[str, Any] = {
        "status": "ok",
        "scorecard": scorecard,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "scores_invented": False,
    }
    if write_evidence:
        out_dir = root / ".agent" / "evidence" / "xrv-readiness"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{scorecard['scorecard_id']}.json"
        out_path.write_text(
            json.dumps(scorecard, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result["path"] = str(out_path)
    return result
