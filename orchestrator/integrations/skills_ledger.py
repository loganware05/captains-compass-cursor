"""Minimal Skills Learning Loop ledger linkage (M24).

Linear is a flight recorder only. This module attaches Linear identifiers and
repository SHAs to learning-run JSON. It never originates Captain approval,
never sets approved_for_execution, and never installs Skills.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Durable Linear project for Skills learning (Captain-bootstrapped M0).
DEFAULT_PROJECT_NAME = "NorthStar Skills Learning Loop"
DEFAULT_PROJECT_ID = "c62f65bf-a376-4716-b958-0d874730a391"  # Linear: NorthStar Skills Learning Loop

# Allowlisted Linear project names/ids for Skills ledger writes.
SKILLS_LEDGER_PROJECT_ALLOWLIST = frozenset(
    {
        DEFAULT_PROJECT_NAME,
        DEFAULT_PROJECT_ID,
        "NorthStar",
        "northstar",
    }
)


class SkillsLedgerError(ValueError):
    """Raised when ledger sync fails closed."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_rev_parse(repo: Path) -> str | None:
    """Best-effort HEAD SHA; None when unavailable."""
    git_dir = Path(repo) / ".git"
    if not git_dir.exists():
        return None
    head = git_dir / "HEAD"
    try:
        raw = head.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if raw.startswith("ref:"):
        ref = raw.split(" ", 1)[1].strip()
        ref_path = git_dir / ref
        try:
            return ref_path.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None
    return raw or None


def empty_ledger(
    *,
    control_revision: str | None = None,
    product_revision: str | None = None,
    project_id: str | None = None,
    project_name: str | None = None,
) -> dict[str, Any]:
    return {
        "provider": "linear",
        "project_id": project_id,
        "project_name": project_name or DEFAULT_PROJECT_NAME,
        "parent_issue_id": None,
        "milestone": None,
        "last_synced_at": None,
        "control_revision": control_revision,
        "product_revision": product_revision,
        "delegated_agent": None,
        "authoritative_approval": False,
        "notes": (
            "Linear records state only. Captain approval must exist in GitHub/"
            "repository evidence; Linear must not originate CAPTAIN_APPROVED."
        ),
    }


def assert_project_allowlisted(
    project_id: str | None = None,
    project_name: str | None = None,
) -> None:
    if project_id and project_id not in SKILLS_LEDGER_PROJECT_ALLOWLIST:
        if project_name and project_name in SKILLS_LEDGER_PROJECT_ALLOWLIST:
            return
        raise SkillsLedgerError(
            f"linear project_id not allowlisted for skills ledger: {project_id!r}"
        )
    if project_name and project_name not in SKILLS_LEDGER_PROJECT_ALLOWLIST:
        if project_id and project_id in SKILLS_LEDGER_PROJECT_ALLOWLIST:
            return
        raise SkillsLedgerError(
            f"linear project_name not allowlisted for skills ledger: {project_name!r}"
        )


def build_ledger_for_run(
    report: dict[str, Any],
    *,
    control_root: Path | None = None,
    product_root: Path | None = None,
) -> dict[str, Any]:
    """Return an additive ledger block (does not mutate Linear)."""
    existing = dict(report.get("ledger") or {})
    control_rev = existing.get("control_revision") or (
        git_rev_parse(control_root) if control_root else None
    )
    product_rev = existing.get("product_revision") or (
        git_rev_parse(product_root) if product_root else None
    )
    ledger = empty_ledger(
        control_revision=control_rev,
        product_revision=product_rev,
        project_id=existing.get("project_id"),
        project_name=existing.get("project_name") or DEFAULT_PROJECT_NAME,
    )
    for key in (
        "parent_issue_id",
        "milestone",
        "last_synced_at",
        "delegated_agent",
        "authoritative_approval",
        "notes",
    ):
        if key in existing and existing[key] is not None:
            ledger[key] = existing[key]
    ledger["authoritative_approval"] = False
    return ledger


def sync_learning_run_ledger(
    run_path: Path,
    *,
    mode: str = "fixtures",
    project_id: str | None = None,
    project_name: str | None = None,
    parent_issue_id: str | None = None,
    milestone: str | None = None,
    control_revision: str | None = None,
    product_revision: str | None = None,
    delegated_agent: str | None = None,
    control_root: Path | None = None,
) -> dict[str, Any]:
    """
    Attach Linear linkage to a learning-run JSON file.

    Modes:
      - fixtures: placeholder IDs safe for CI
      - link: attach caller-provided IDs only (no Linear create, no approval)
    """
    run_path = Path(run_path)
    if not run_path.is_file():
        raise SkillsLedgerError(f"learning run not found: {run_path}")
    mode_norm = (mode or "fixtures").strip().lower()
    if mode_norm not in {"fixtures", "link"}:
        raise SkillsLedgerError(f"unsupported ledger sync mode: {mode!r}")

    report = json.loads(run_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise SkillsLedgerError("learning run JSON must be an object")

    ledger = build_ledger_for_run(report, control_root=control_root)
    if control_revision:
        ledger["control_revision"] = control_revision
    if product_revision:
        ledger["product_revision"] = product_revision

    if mode_norm == "fixtures":
        ledger["project_id"] = project_id or "fixture-project"
        ledger["project_name"] = project_name or DEFAULT_PROJECT_NAME
        ledger["parent_issue_id"] = parent_issue_id or f"fixture-parent-{report.get('run_id')}"
        ledger["milestone"] = milestone or "M0 — Ledger Bootstrap"
    else:
        pid = project_id or DEFAULT_PROJECT_ID
        pname = project_name or DEFAULT_PROJECT_NAME
        assert_project_allowlisted(pid, pname)
        if not parent_issue_id:
            raise SkillsLedgerError("link mode requires --parent-issue-id")
        ledger["project_id"] = pid
        ledger["project_name"] = pname
        ledger["parent_issue_id"] = parent_issue_id
        if milestone:
            ledger["milestone"] = milestone

    if delegated_agent:
        # Routing candidate only — not an approval or hardcoded dispatcher mandate.
        ledger["delegated_agent"] = delegated_agent

    ledger["last_synced_at"] = _utc_now()
    ledger["authoritative_approval"] = False
    if report.get("approved_for_execution") is True:
        raise SkillsLedgerError(
            "refusing to sync ledger while approved_for_execution=true "
            "(Skills learning loop must remain fail-closed)"
        )

    report["ledger"] = ledger
    run_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sibling = run_path.with_name(run_path.stem + ".ledger.json")
    sibling.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
