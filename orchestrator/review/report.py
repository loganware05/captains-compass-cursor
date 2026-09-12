"""Write schema-validated code review evidence reports."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import ValidationError, validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class ReportError(ValueError):
    """Raised when a review report cannot be written safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_id(value: str) -> str:
    if not _SAFE_ID.match(value):
        raise ReportError(f"unsafe run_id: {value!r}")
    return value


def evidence_dir(repo_root: Path, run_id: str) -> Path:
    return Path(repo_root) / ".agent" / "evidence" / "code-review" / _safe_id(run_id)


def build_report(
    *,
    run_id: str,
    repository: str,
    findings: list[dict[str, Any]],
    domains: list[str],
    skills_invoked: list[str] | None = None,
    intent_artifact: str | None = None,
    base_ref: str = "",
    head_ref: str = "",
    plan_id: str = "",
    hermetic: bool = True,
    candidates_source: str = "fixtures",
    context_pack_path: str = "",
    status: str = "completed",
) -> dict[str, Any]:
    verified = sum(1 for f in findings if f.get("status") == "verified")
    unverified = sum(1 for f in findings if f.get("status") == "unverified")
    discarded = sum(1 for f in findings if f.get("status") == "discarded")
    report: dict[str, Any] = {
        "schema_version": "northstar.code_review_report.v1",
        "run_id": run_id,
        "created_at": _utc_now(),
        "repository": repository,
        "base_ref": base_ref,
        "head_ref": head_ref,
        "plan_id": plan_id,
        "status": status,
        "summary": {
            "domains": list(domains),
            "skills_invoked": list(skills_invoked or []),
            "findings_total": len(findings),
            "verified": verified,
            "unverified": unverified,
            "discarded": discarded,
            "intent_artifact": intent_artifact or "",
        },
        "findings": findings,
        "provenance": {
            "pipeline": "northstar.review.v1",
            "hermetic": hermetic,
            "invoke_model": False,
            "github_review_posted": False,
            "candidates_source": candidates_source,
        },
        "context_pack_path": context_pack_path,
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    lines = [
        f"# Code review report — `{report.get('run_id')}`",
        "",
        f"- Repository: `{report.get('repository')}`",
        f"- Status: **{report.get('status')}**",
        f"- Created: {report.get('created_at')}",
        f"- Domains: {', '.join(summary.get('domains') or []) or '(none)'}",
        f"- Findings: {summary.get('findings_total', 0)} "
        f"(verified={summary.get('verified', 0)}, "
        f"unverified={summary.get('unverified', 0)}, "
        f"discarded={summary.get('discarded', 0)})",
        f"- GitHub review posted: `{report.get('provenance', {}).get('github_review_posted', False)}`",
        "",
        "## Findings",
        "",
    ]
    findings = report.get("findings") or []
    if not findings:
        lines.append("_No findings._")
    for finding in findings:
        lines.extend(
            [
                f"### {finding.get('id')}: {finding.get('title')}",
                "",
                f"- Severity: `{finding.get('severity')}`",
                f"- Confidence: `{finding.get('confidence')}`",
                f"- Status: **{finding.get('status')}**",
                f"- Skill: `{finding.get('skill')}`",
                f"- Evidence: {', '.join(f'`{p}`' for p in (finding.get('evidence_paths') or [])) or '_none_'}",
            ]
        )
        if finding.get("detail"):
            lines.extend(["", finding["detail"]])
        if finding.get("suggested_fix"):
            lines.extend(["", f"**Suggested fix:** {finding['suggested_fix']}"])
        if finding.get("discard_reason"):
            lines.extend(["", f"_Discard reason:_ `{finding['discard_reason']}`"])
        lines.append("")
    lines.extend(
        [
            "## Provenance",
            "",
            "```json",
            json.dumps(report.get("provenance") or {}, indent=2, sort_keys=True),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(
    repo_root: Path,
    report: dict[str, Any],
    *,
    context_pack: dict[str, Any] | None = None,
) -> Path:
    try:
        validate_document(report, "code-review-report.schema.json")
    except ValidationError as exc:
        raise ReportError(str(exc)) from exc
    out_dir = evidence_dir(repo_root, str(report["run_id"]))
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    md_path = out_dir / "report.md"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    if context_pack is not None:
        pack_path = out_dir / "context-pack.json"
        with pack_path.open("w", encoding="utf-8") as handle:
            json.dump(context_pack, handle, indent=2, sort_keys=True)
            handle.write("\n")
        report["context_pack_path"] = str(pack_path.relative_to(repo_root))
        # Rewrite JSON with updated context_pack_path; re-validate.
        try:
            validate_document(report, "code-review-report.schema.json")
        except ValidationError as exc:
            raise ReportError(str(exc)) from exc
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
        md_path.write_text(render_markdown(report), encoding="utf-8")
    return report_path
