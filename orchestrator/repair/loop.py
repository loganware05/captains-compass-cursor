"""B4 repair loop — FIND→PROVE→packet (Captain-gated FIX/SUBMIT).

Never auto-merges. Verified findings only. Hermetic by default.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA_VERSION = "northstar.repair_run.v1"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")

SEVERITY_RANK = {
    "critical": 5,
    "high": 4,
    "medium": 3,
    "warning": 3,
    "low": 2,
    "info": 1,
    "none": 0,
}


class RepairError(ValueError):
    """Raised when a repair run cannot proceed safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_id(value: str, label: str = "id") -> str:
    if not _SAFE_ID.match(value):
        raise RepairError(f"unsafe {label}: {value!r}")
    return value


def load_report(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise RepairError(f"review report not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RepairError(f"invalid report JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RepairError("report must be a JSON object")
    return data


def load_allowlist_repos(path: Path | None) -> set[str]:
    """Load repo allowlist from github-allowlist.yml-like JSON/YAML-lite or JSON."""
    if path is None:
        return {"loganware05/captain-compass-sandbox"}
    path = Path(path)
    if not path.is_file():
        raise RepairError(f"allowlist not found: {path}")
    text = path.read_text(encoding="utf-8")
    # Prefer JSON
    if path.suffix == ".json":
        data = json.loads(text)
        repos = data.get("repos") or []
        return {str(r) for r in repos}
    # Minimal YAML: collect lines under repos:
    repos: set[str] = set()
    in_repos = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("repos:"):
            in_repos = True
            continue
        if in_repos:
            if stripped.startswith("- "):
                repos.add(stripped[2:].strip().strip("'\""))
            elif stripped and not stripped.startswith("#") and not line.startswith(" "):
                break
    if not repos:
        raise RepairError(f"no repos found in allowlist: {path}")
    return repos


def normalize_repo(repository: str) -> str:
    repo = repository.strip()
    repo = repo.replace("https://github.com/", "").replace("http://github.com/", "")
    repo = repo.removesuffix(".git").strip("/")
    # Drop absolute local paths to basename owner/name when possible
    if "/" in repo and not repo.startswith("/"):
        parts = repo.split("/")
        if len(parts) >= 2:
            return f"{parts[-2]}/{parts[-1]}"
    return repo


def find_finding(report: dict[str, Any], finding_id: str) -> dict[str, Any]:
    findings = report.get("findings") or []
    for item in findings:
        if str(item.get("id")) == finding_id:
            return item
    raise RepairError(f"finding not found: {finding_id}")


def prove_finding(
    finding: dict[str, Any],
    *,
    severity_floor: str = "medium",
) -> dict[str, Any]:
    status = str(finding.get("status") or "").lower()
    if status != "verified":
        raise RepairError(f"finding not verified (status={status!r})")
    sev = str(finding.get("severity") or "none").lower()
    if SEVERITY_RANK.get(sev, 0) < SEVERITY_RANK.get(severity_floor.lower(), 0):
        raise RepairError(
            f"finding severity {sev!r} below floor {severity_floor!r}"
        )
    return {
        "finding_id": finding.get("id"),
        "status": status,
        "severity": sev,
        "title": finding.get("title"),
        "suggested_fix": finding.get("suggested_fix") or "",
        "evidence_paths": list(finding.get("evidence_paths") or []),
        "proved_at": _utc_now(),
    }


def build_dispatch_packet(
    *,
    run_id: str,
    finding: dict[str, Any],
    repository: str,
    selected_agent_id: str | None = None,
) -> dict[str, Any]:
    return {
        "kind": "northstar-repair-dispatch-packet",
        "repair_run_id": run_id,
        "created_at": _utc_now(),
        "dispatch_authorized": False,
        "finding_id": finding.get("id"),
        "repository": repository,
        "selected_agent_id": selected_agent_id,
        "objective": {
            "title": f"Repair verified finding {finding.get('id')}: {finding.get('title')}",
            "category": "devtool",
            "target_repository": repository,
            "required_skills": ["code-reviewer", "review-fix-loop"],
            "skill_scope": "sandbox",
        },
        "awaiting_captain_utterance": "I authorize the repair fix",
        "never_auto_merge": True,
    }


def start_repair(
    *,
    repo_root: Path,
    report_path: Path,
    finding_id: str,
    run_id: str | None = None,
    allowlist_path: Path | None = None,
    severity_floor: str = "medium",
    captain_authorized_fix: bool = False,
    selected_agent_id: str | None = None,
    repository_override: str | None = None,
) -> dict[str, Any]:
    """Run FIND→PROVE→packet; optionally mark FIX authorized (still no auto-merge)."""
    repo_root = Path(repo_root).resolve()
    report = load_report(Path(report_path))
    finding = find_finding(report, finding_id)
    proved = prove_finding(finding, severity_floor=severity_floor)

    repository = normalize_repo(
        str(repository_override or report.get("repository") or "")
    )
    if not repository or "/" not in repository:
        raise RepairError(
            "repository must be owner/name (use --repository for fixture reports)"
        )
    allow = load_allowlist_repos(allowlist_path)
    if repository not in allow:
        raise RepairError(f"repository not allowlisted for repair: {repository}")

    rid = _safe_id(run_id or f"repair-{finding_id}", "run_id")
    out_dir = repo_root / ".agent" / "evidence" / "repair" / rid
    out_dir.mkdir(parents=True, exist_ok=True)

    packet = build_dispatch_packet(
        run_id=rid,
        finding=finding,
        repository=repository,
        selected_agent_id=selected_agent_id,
    )

    stage = "packet_ready"
    submit: dict[str, Any] = {
        "prepared": False,
        "auto_merge": False,
        "note": "Draft PR / branch submit requires human review; never auto-merge.",
    }
    if captain_authorized_fix:
        stage = "fix_authorized_prepare_submit"
        packet["dispatch_authorized"] = True
        packet["dispatch_authorized_at"] = _utc_now()
        submit = {
            "prepared": True,
            "auto_merge": False,
            "suggested_branch": f"cursor/repair-{finding_id}-05fd",
            "suggested_pr_title": f"fix: address verified finding {finding_id}",
            "rollback": "Revert the repair PR; restore pre-fix evidence.",
            "note": "Captain authorized FIX preparation only — open draft PR manually; never auto-merge.",
        }

    result = {
        "schema_version": SCHEMA_VERSION,
        "run_id": rid,
        "created_at": _utc_now(),
        "stage": stage,
        "repository": packet["repository"],
        "finding": proved,
        "report_path": str(Path(report_path)),
        "dispatch_packet": packet,
        "submit": submit,
        "locks": {
            "never_auto_merge": True,
            "verified_only": True,
            "captain_fix_authorized": bool(captain_authorized_fix),
        },
    }

    try:
        validate_document(result, "repair-run.schema.json")
    except ValidationError as exc:
        raise RepairError(f"repair run failed schema validation: {exc}") from exc

    (out_dir / "repair-run.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (out_dir / "dispatch-packet.json").write_text(
        json.dumps(packet, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                f"# Repair run `{rid}`",
                "",
                f"- Stage: **{stage}**",
                f"- Finding: `{finding_id}` (verified / {proved.get('severity')})",
                f"- Repository: `{packet['repository']}`",
                f"- Auto-merge: **false**",
                f"- Captain FIX authorized: `{bool(captain_authorized_fix)}`",
                "",
                "## Title",
                "",
                str(proved.get("title") or ""),
                "",
                "## Suggested fix",
                "",
                str(proved.get("suggested_fix") or "(none)"),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return result
