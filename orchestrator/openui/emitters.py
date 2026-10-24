"""Emit OpenUI Lang for NorthStar control surfaces."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.openui.lang import call, join_list, program

PLAN_ID_RE = re.compile(
    r"(?im)^\|\s*Plan ID\s*\|\s*`?([^`|\n]+)`?\s*\|"
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_plan_meta(text: str) -> dict[str, str]:
    status = "UNKNOWN"
    m = re.search(r"(?im)^-\s*Status:\s*\*?\*?([^*\n]+)", text)
    if m:
        status = m.group(1).strip().strip("*").strip()
    else:
        m2 = re.search(r"(?im)^\|\s*Status\s*\|\s*([^|]+)\|", text)
        if m2:
            status = m2.group(1).strip().strip("*").strip()
    plan_id = "unknown"
    m3 = PLAN_ID_RE.search(text)
    if m3:
        plan_id = m3.group(1).strip()
    title = "Implementation Plan"
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip() or title
            break
    return {"status": status, "plan_id": plan_id, "title": title}


def _list_skills(repo: Path, limit: int = 8) -> list[str]:
    root = repo / ".cursor" / "skills"
    if not root.is_dir():
        return []
    names = sorted(
        p.name
        for p in root.iterdir()
        if p.is_dir() and (p / "SKILL.md").is_file() and p.name != "inodes"
    )
    return names[:limit]


def _list_agents(repo: Path, limit: int = 12) -> list[str]:
    root = repo / ".cursor" / "agents"
    if not root.is_dir():
        return []
    names = sorted(p.stem for p in root.glob("*.md"))
    return names[:limit]


def _list_hooks(repo: Path) -> list[str]:
    root = repo / ".cursor" / "hooks"
    if not root.is_dir():
        return []
    return sorted(
        p.name
        for p in root.glob("*.sh")
        if p.name not in {"_common.sh", "README.md"} and not p.name.startswith("_")
    )


def _budget_summary(repo: Path) -> str:
    budgets = repo / ".agent" / "budgets"
    if not budgets.is_dir():
        return "no budgets"
    files = sorted(budgets.glob("*.md"))
    if not files:
        return "no budgets"
    latest = files[-1]
    text = _read_text(latest)
    status_line = ""
    for line in text.splitlines():
        if line.lower().startswith("status:"):
            status_line = line.strip()
            break
    return f"{latest.name}: {status_line or 'present'}"


def emit_plan_approval(repo_root: Path) -> str:
    plan_path = Path(repo_root) / "IMPLEMENTATION_PLAN.md"
    text = _read_text(plan_path)
    meta = _parse_plan_meta(text)
    hooks = _list_hooks(Path(repo_root))
    agents = _list_agents(Path(repo_root))
    # crude affected-files hint from plan table if present
    affected = "see plan Files Expected to Change"
    m = re.search(
        r"(?is)## Files Expected to Change.*?(?:\n## |\Z)", text
    )
    if m:
        rows = re.findall(r"`([^`]+)`", m.group(0))
        if rows:
            affected = join_list(rows, limit=8)

    card = call(
        "PlanApprovalCard",
        meta["plan_id"],
        meta["title"],
        meta["status"],
        f"hooks={len(hooks)}; specialists={len(agents)}",
        affected,
        join_list(agents, limit=8),
        join_list(hooks, limit=8),
    )
    return program([f"card = {card}"], root_expr="NorthStarStack([card])")


def emit_control_tower(repo_root: Path) -> str:
    repo = Path(repo_root)
    agents = _list_agents(repo)
    skills = _list_skills(repo)
    hooks = _list_hooks(repo)
    # green if present — inventory only (not live process telemetry)
    hook_grid = join_list([f"{h}:ready" for h in hooks], limit=10)
    tower = call(
        "ControlTowerTelemetry",
        join_list(agents, limit=12),
        join_list(skills, limit=10),
        _budget_summary(repo),
        hook_grid or "(none)",
    )
    badge = call(
        "CompassStatusBadge",
        "NorthStar",
        _version(repo),
        "ok",
    )
    return program(
        [f"tower = {tower}", f"badge = {badge}"],
        root_expr="NorthStarStack([badge, tower])",
    )


def emit_hermetic_scorecard(repo_root: Path, report: dict[str, Any] | None = None) -> str:
    repo = Path(repo_root)
    if report is None:
        report = _load_latest_scorecard(repo)
    phase = str(report.get("phase") or "unknown")
    rec = str(report.get("level3_recommendation") or "defer")
    rationale = str(report.get("level3_rationale") or "n/a")
    metrics = report.get("metrics") or {}
    if isinstance(metrics, dict):
        parts = []
        for k, v in list(metrics.items())[:7]:
            if isinstance(v, dict) and "rate" in v:
                parts.append(f"{k}={v.get('rate')}")
            elif isinstance(v, (int, float, str)):
                parts.append(f"{k}={v}")
            else:
                parts.append(k)
        metrics_summary = join_list(parts, limit=7)
    else:
        metrics_summary = str(metrics)[:200]
    deltas = report.get("deltas")
    compare = "n/a"
    if isinstance(deltas, dict) and deltas:
        compare = join_list(
            [f"{k}:{v}" for k, v in list(deltas.items())[:6]], limit=6
        )
    score = call(
        "HermeticScorecard",
        phase,
        rec,
        rationale[:240],
        metrics_summary,
        compare,
    )
    rec_card = call(
        "RecommendationCard",
        "Level 3",
        rec,
        rationale[:240],
    )
    badge = call("CompassStatusBadge", "Adaptive", _version(repo), rec)
    return program(
        [f"score = {score}", f"rec = {rec_card}", f"badge = {badge}"],
        root_expr="NorthStarStack([badge, score, rec])",
    )


def emit_closeout_ledger(repo_root: Path, report: dict[str, Any] | None = None) -> str:
    repo = Path(repo_root)
    if report is None:
        report = _load_latest_closeout(repo)
    snapshot_id = str(report.get("snapshot_id") or report.get("report_id") or "n/a")
    readiness = str(report.get("readiness") or "unknown")
    sha_local = str(report.get("repository_sha") or _git_sha(repo) or "n/a")
    sha_remote = str(report.get("compared_sha") or report.get("since_sha") or "n/a")
    actions = report.get("recommended_actions") or []
    if isinstance(actions, list):
        actions_s = join_list(actions, limit=6)
    else:
        actions_s = str(actions)[:200]
    evidence = join_list(
        [
            f"version={report.get('northstar_version') or _version(repo)}",
            f"auto_closed={report.get('issues_auto_closed', False)}",
            f"authority={report.get('authority_mutation', False)}",
        ],
        limit=6,
    )
    widget = call(
        "CloseoutLedgerWidget",
        snapshot_id,
        readiness,
        sha_local[:40],
        sha_remote[:40],
        evidence,
        actions_s,
    )
    return program([f"ledger = {widget}"], root_expr="NorthStarStack([ledger])")


def _version(repo: Path) -> str:
    p = repo / "VERSION"
    if p.is_file():
        return p.read_text(encoding="utf-8").strip()
    return "unknown"


def _git_sha(repo: Path) -> str:
    head = repo / ".git" / "HEAD"
    if not head.is_file():
        return ""
    try:
        raw = head.read_text(encoding="utf-8").strip()
        if raw.startswith("ref:"):
            ref = raw.split(" ", 1)[1].strip()
            ref_path = repo / ".git" / ref
            if ref_path.is_file():
                return ref_path.read_text(encoding="utf-8").strip()[:40]
        return raw[:40]
    except OSError:
        return ""


def _load_latest_scorecard(repo: Path) -> dict[str, Any]:
    evidence = repo / ".agent" / "evidence" / "n3-adaptive-intelligence-validation"
    if evidence.is_dir():
        candidates = sorted(evidence.glob("**/scorecard*.json")) + sorted(
            evidence.glob("**/*compare*.json")
        )
        for path in reversed(candidates):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    if "report" in data and isinstance(data["report"], dict):
                        return data["report"]
                    return data
            except (OSError, json.JSONDecodeError):
                continue
    return {
        "phase": "fixture",
        "level3_recommendation": "defer",
        "level3_rationale": "No scorecard artifact found; fixture deferral advisory.",
        "metrics": {},
        "deltas": {},
    }


def _load_latest_closeout(repo: Path) -> dict[str, Any]:
    evidence = repo / ".agent" / "evidence" / "n1-operational-reconciliation"
    paths: list[Path] = []
    if evidence.is_dir():
        paths.extend(sorted(evidence.glob("**/*closeout*.json")))
    status_dir = repo / ".agent" / "status" / "closeout-reports"
    if status_dir.is_dir():
        paths.extend(sorted(status_dir.glob("**/*.json")))
    for path in reversed(paths):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            continue
    return {
        "report_id": "closeout-fixture",
        "snapshot_id": "n/a",
        "readiness": "unknown",
        "repository_sha": _git_sha(repo),
        "compared_sha": "n/a",
        "northstar_version": _version(repo),
        "recommended_actions": ["run status closeout with COMPASS_STATUS_ENABLED=1"],
        "issues_auto_closed": False,
        "authority_mutation": False,
    }

