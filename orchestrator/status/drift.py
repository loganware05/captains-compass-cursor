"""Deterministic documentation / project-memory drift detectors (M51)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

REQUIRED_MEMORY_DOCS = (
    "AGENTS.md",
    "PROJECT_CONTEXT.md",
    "DECISIONS.md",
    "PROGRESS.md",
    "TESTING.md",
    "IMPLEMENTATION_PLAN.md",
    "VERSION",
)

_SKILL_COUNT_RE = re.compile(
    r"(?i)\b("
    r"forty-eight|forty eight|forty-seven|forty seven|"
    r"forty-four|forty four|forty-three|forty three|forty|"
    r"\d+"
    r")\s+skills?\b"
)
_WORD_NUMBERS = {
    "forty": 40,
    "forty-three": 43,
    "forty three": 43,
    "forty-four": 44,
    "forty four": 44,
    "forty-seven": 47,
    "forty seven": 47,
    "forty-eight": 48,
    "forty eight": 48,
}


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def count_skills_fs(repo_root: Path) -> int:
    skills = Path(repo_root) / ".cursor" / "skills"
    if not skills.is_dir():
        return 0
    return sum(1 for p in skills.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def parse_skill_count_from_docs(text: str) -> int | None:
    match = _SKILL_COUNT_RE.search(text)
    if not match:
        return None
    token = match.group(1).strip().lower()
    if token.isdigit():
        return int(token)
    return _WORD_NUMBERS.get(token)


def parse_plan_status(plan_text: str) -> str:
    for line in plan_text.splitlines():
        if line.strip().startswith("- Status:"):
            return line.split(":", 1)[1].strip()
        if "| Status |" in line and "APPROVED" in line.upper():
            # table cell form
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[0].lower() == "status":
                return parts[1].replace("*", "").strip()
    return ""


def parse_progress_plan_id(progress_text: str) -> str:
    match = re.search(r"[Pp]lan\s+`([^`]+)`", progress_text)
    if match:
        return match.group(1).strip()
    match = re.search(r"Plan ID[^`]*`([^`]+)`", progress_text)
    if match:
        return match.group(1).strip()
    return ""


def parse_active_plan_id(plan_text: str) -> str:
    match = re.search(r"\|\s*Plan ID\s*\|\s*`?([^`|]+)`?\s*\|", plan_text)
    if match:
        return match.group(1).strip()
    match = re.search(r"Plan ID\s*[:=]\s*`([^`]+)`", plan_text)
    if match:
        return match.group(1).strip()
    return ""


def collect_memory_docs(repo_root: Path) -> dict[str, bool]:
    root = Path(repo_root)
    return {name: (root / name).is_file() for name in REQUIRED_MEMORY_DOCS}


def detect_drift(repo_root: Path) -> dict[str, Any]:
    """Return structured drift findings + supporting counters."""
    root = Path(repo_root)
    version = _read_text(root / "VERSION").strip()
    progress = _read_text(root / "PROGRESS.md")
    context = _read_text(root / "PROJECT_CONTEXT.md")
    plan = _read_text(root / "IMPLEMENTATION_PLAN.md")
    memory = collect_memory_docs(root)
    skill_fs = count_skills_fs(root)
    skill_docs = parse_skill_count_from_docs(context)
    plan_status = parse_plan_status(plan)
    plan_id = parse_active_plan_id(plan)
    progress_plan_id = parse_progress_plan_id(progress)

    findings: list[dict[str, Any]] = []

    missing = [name for name, present in memory.items() if not present]
    if missing:
        findings.append(
            {
                "finding_id": "drift-missing-memory-docs",
                "kind": "missing_memory_docs",
                "severity": "error",
                "claim_kind": "observed",
                "summary": f"Required project memory docs missing: {', '.join(missing)}",
                "evidence": missing,
            }
        )
    else:
        findings.append(
            {
                "finding_id": "drift-memory-docs-present",
                "kind": "memory_docs",
                "severity": "info",
                "claim_kind": "observed",
                "summary": "All required project memory docs are present.",
                "evidence": list(REQUIRED_MEMORY_DOCS),
            }
        )

    if version and version not in progress and f"v{version}" not in progress:
        findings.append(
            {
                "finding_id": "drift-version-progress",
                "kind": "version_progress_mismatch",
                "severity": "warn",
                "claim_kind": "documented",
                "summary": (
                    f"VERSION={version} not mentioned in PROGRESS.md current status text."
                ),
                "evidence": [f"VERSION={version}"],
            }
        )

    if skill_docs is not None and skill_docs != skill_fs:
        findings.append(
            {
                "finding_id": "drift-skill-count",
                "kind": "skill_count_mismatch",
                "severity": "warn",
                "claim_kind": "documented",
                "summary": (
                    f"PROJECT_CONTEXT.md reports {skill_docs} Skills but "
                    f".cursor/skills has {skill_fs}."
                ),
                "evidence": [
                    f"docs_count={skill_docs}",
                    f"fs_count={skill_fs}",
                ],
            }
        )

    if plan_id and progress_plan_id and plan_id != progress_plan_id:
        findings.append(
            {
                "finding_id": "drift-plan-id",
                "kind": "plan_id_mismatch",
                "severity": "warn",
                "claim_kind": "documented",
                "summary": (
                    f"IMPLEMENTATION_PLAN Plan ID `{plan_id}` differs from "
                    f"PROGRESS plan `{progress_plan_id}`."
                ),
                "evidence": [f"plan={plan_id}", f"progress={progress_plan_id}"],
            }
        )

    if plan_status:
        status_upper = plan_status.upper()
        if "AWAITING" in status_upper and "APPROVED" in progress.upper() and plan_id:
            # soft signal only when progress claims implementing/approved while plan awaits
            if "implementing" in progress.lower() or "APPROVED" in progress:
                findings.append(
                    {
                        "finding_id": "drift-plan-status",
                        "kind": "plan_status_mismatch",
                        "severity": "warn",
                        "claim_kind": "documented",
                        "summary": (
                            f"Plan status is {plan_status!r} while PROGRESS may imply "
                            "active implementation."
                        ),
                        "evidence": [f"plan_status={plan_status}"],
                    }
                )

    # Development-process awareness: active plan + external evidence stores.
    status_upper = (plan_status or "").upper()
    if plan_id and any(
        token in status_upper for token in ("APPROVED", "IN PROGRESS", "VALIDATING")
    ):
        findings.append(
            {
                "finding_id": "dev-active-plan",
                "kind": "active_development",
                "severity": "info",
                "claim_kind": "documented",
                "summary": (
                    f"Active development plan `{plan_id}` is {plan_status!r}; "
                    "Overseer is tracking process without granting authority."
                ),
                "evidence": [
                    f"plan_id={plan_id}",
                    f"plan_status={plan_status}",
                    f"progress_plan_id={progress_plan_id or ''}",
                ],
            }
        )

    incident_dir = root / ".agent" / "incidents" / "sentry"
    incident_count = (
        len(list(incident_dir.glob("*.json"))) if incident_dir.is_dir() else 0
    )
    if incident_count:
        findings.append(
            {
                "finding_id": "dev-sentry-incidents",
                "kind": "external_incident_evidence",
                "severity": "info",
                "claim_kind": "external",
                "summary": (
                    f"Observed {incident_count} Sentry incident evidence packet(s) "
                    "under .agent/incidents/sentry/."
                ),
                "evidence": [f"count={incident_count}"],
            }
        )

    conv_dir = root / ".agent" / "conversations" / "trajectories"
    conv_count = len(list(conv_dir.glob("*.json"))) if conv_dir.is_dir() else 0
    if conv_count:
        findings.append(
            {
                "finding_id": "dev-conversation-trajectories",
                "kind": "external_conversation_evidence",
                "severity": "info",
                "claim_kind": "external",
                "summary": (
                    f"Observed {conv_count} conversation trajectory(ies) under "
                    ".agent/conversations/trajectories/."
                ),
                "evidence": [f"count={conv_count}"],
            }
        )

    exec_dir = root / ".agent" / "executions" / "t3"
    exec_count = len(list(exec_dir.glob("*.json"))) if exec_dir.is_dir() else 0
    if exec_count:
        findings.append(
            {
                "finding_id": "dev-t3-executions",
                "kind": "t3_execution_evidence",
                "severity": "info",
                "claim_kind": "observed",
                "summary": (
                    f"Observed {exec_count} T3 ExecutionAdapter run(s) under "
                    ".agent/executions/t3/."
                ),
                "evidence": [f"count={exec_count}"],
            }
        )

    research_dir = root / ".agent" / "research" / "apify"
    research_count = (
        len(list(research_dir.glob("*.json"))) if research_dir.is_dir() else 0
    )
    if research_count:
        findings.append(
            {
                "finding_id": "dev-apify-research",
                "kind": "external_research_evidence",
                "severity": "info",
                "claim_kind": "external",
                "summary": (
                    f"Observed {research_count} Apify research packet(s) under "
                    ".agent/research/apify/."
                ),
                "evidence": [f"count={research_count}"],
            }
        )

    return {
        "northstar_version": version,
        "memory_docs": memory,
        "skill_count_fs": skill_fs,
        "skill_count_docs": skill_docs,
        "active_plan_id": plan_id,
        "plan_status": plan_status,
        "progress_plan_id": progress_plan_id,
        "findings": findings,
    }
