"""Opt-in GitHub draft PR review posting (M30).

Default path remains evidence-only. Posting requires an explicit flag, an
allowlisted owner/repo, and never uses APPROVE / REQUEST_CHANGES.
Tokens are never logged; evidence bodies are secret-redacted.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib import error, request

import yaml

from orchestrator.integrations.events import redact_secrets
from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA_VERSION = "northstar.github_allowlist.v1"
_SEVERITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "warning": 2,  # alias → medium
    "low": 3,
    "info": 4,
}
_REPO_SLUG = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

HttpClient = Callable[[str, str, dict[str, str], bytes | None], tuple[int, dict[str, Any]]]


class GitHubDraftError(ValueError):
    """Raised when draft posting cannot proceed safely."""


def normalize_severity_floor(value: str | None) -> str:
    floor = (value or "medium").strip().lower()
    if floor == "warning":
        floor = "medium"
    if floor not in {"critical", "high", "medium", "low", "info"}:
        raise GitHubDraftError(f"invalid severity_floor: {value!r}")
    return floor


def severity_meets_floor(severity: str, floor: str) -> bool:
    sev = (severity or "info").strip().lower()
    if sev == "warning":
        sev = "medium"
    if sev not in _SEVERITY_RANK:
        sev = "info"
    return _SEVERITY_RANK[sev] <= _SEVERITY_RANK[normalize_severity_floor(floor)]


def resolve_allowlist_path(repo_root: Path, explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        return Path(explicit)
    candidates = (
        Path(repo_root) / ".agent" / "review" / "github-allowlist.yml",
        Path(repo_root) / ".agent" / "review" / "github-allowlist.yaml",
        Path(repo_root) / ".agent" / "review" / "github-allowlist.json",
    )
    for path in candidates:
        if path.is_file():
            return path
    return None


def load_allowlist(path: Path | None) -> dict[str, Any]:
    if path is None or not Path(path).is_file():
        return {
            "schema_version": SCHEMA_VERSION,
            "repos": [],
            "severity_floor": "medium",
            "notes": "",
        }
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise GitHubDraftError("allowlist must be an object")
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("repos", [])
    data.setdefault("severity_floor", "medium")
    data.setdefault("notes", "")
    data["schema_version"] = SCHEMA_VERSION
    data["repos"] = [str(r).strip() for r in (data.get("repos") or []) if str(r).strip()]
    data["severity_floor"] = normalize_severity_floor(
        str(data.get("severity_floor") or "medium")
    )
    try:
        validate_document(data, "github-allowlist.schema.json")
    except (FileNotFoundError, ValidationError) as exc:
        raise GitHubDraftError(str(exc)) from exc
    return data


def repo_allowed(slug: str, allowlist: Mapping[str, Any]) -> bool:
    slug = (slug or "").strip()
    if not _REPO_SLUG.match(slug):
        return False
    allowed = {str(r).strip().lower() for r in (allowlist.get("repos") or [])}
    return slug.lower() in allowed


def select_findings_for_draft(
    findings: list[dict[str, Any]],
    *,
    severity_floor: str = "medium",
) -> list[dict[str, Any]]:
    floor = normalize_severity_floor(severity_floor)
    selected: list[dict[str, Any]] = []
    for finding in findings:
        if finding.get("status") != "verified":
            continue
        if not severity_meets_floor(str(finding.get("severity") or "info"), floor):
            continue
        selected.append(finding)
    return selected


def render_draft_body(
    report: Mapping[str, Any],
    findings: list[dict[str, Any]],
) -> str:
    run_id = report.get("run_id") or ""
    summary = report.get("summary") or {}
    provenance = report.get("provenance") or {}
    lines = [
        "## NorthStar Code Reviewer (draft)",
        "",
        f"_Hermetic evidence run `{run_id}`. Opt-in draft only — not an approval._",
        "",
        f"- Verified findings included: **{len(findings)}**",
        f"- Domains: {', '.join(summary.get('domains') or []) or '(none)'}",
        f"- Candidates source: `{provenance.get('candidates_source', '')}`",
        "",
    ]
    if not findings:
        lines.append("_No verified findings met the severity floor._")
    for finding in findings:
        lines.extend(
            [
                f"### {finding.get('id')}: {finding.get('title')}",
                "",
                f"- Severity: `{finding.get('severity')}`",
                f"- Confidence: `{finding.get('confidence')}`",
                f"- Skill: `{finding.get('skill')}`",
            ]
        )
        if finding.get("detail"):
            lines.extend(["", str(finding["detail"])])
        if finding.get("suggested_fix"):
            lines.extend(["", f"**Suggested fix:** {finding['suggested_fix']}"])
        lines.append("")
    lines.extend(
        [
            "---",
            "Posted by NorthStar M30 opt-in draft posting. Default reviews remain evidence-only.",
        ]
    )
    return "\n".join(lines)


def _default_http_client(
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes | None,
) -> tuple[int, dict[str, Any]]:
    req = request.Request(url, data=body, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw.strip() else {}
            return int(resp.status), payload if isinstance(payload, dict) else {"data": payload}
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw.strip() else {"message": str(exc)}
        except json.JSONDecodeError:
            payload = {"message": raw or str(exc)}
        if not isinstance(payload, dict):
            payload = {"message": str(payload)}
        return int(exc.code), payload
    except error.URLError as exc:
        raise GitHubDraftError(f"GitHub request failed: {exc}") from exc


def _auth_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "northstar-code-reviewer-m30",
    }


def create_pending_review(
    *,
    repo_slug: str,
    pull_number: int,
    body: str,
    commit_id: str | None = None,
    token: str | None = None,
    http_client: HttpClient | None = None,
) -> dict[str, Any]:
    """Create a PENDING (draft) PR review — never APPROVE / REQUEST_CHANGES."""
    token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if not token:
        raise GitHubDraftError("GITHUB_TOKEN or GH_TOKEN required for draft posting")
    if not _REPO_SLUG.match(repo_slug):
        raise GitHubDraftError(f"invalid repo slug: {repo_slug!r}")
    if pull_number <= 0:
        raise GitHubDraftError(f"invalid pull_number: {pull_number}")

    payload: dict[str, Any] = {"body": body}
    # Omit `event` → PENDING draft review (not APPROVE / REQUEST_CHANGES / COMMENT).
    if commit_id:
        payload["commit_id"] = commit_id

    url = f"https://api.github.com/repos/{repo_slug}/pulls/{pull_number}/reviews"
    client = http_client or _default_http_client
    status, response = client(
        "POST",
        url,
        _auth_headers(token),
        json.dumps(payload).encode("utf-8"),
    )
    redacted = redact_secrets(
        {
            "http_status": status,
            "repo": repo_slug,
            "pull_number": pull_number,
            "event": None,
            "state": response.get("state"),
            "id": response.get("id"),
            "html_url": response.get("html_url"),
            "message": response.get("message"),
        }
    )
    if status >= 300:
        raise GitHubDraftError(
            f"GitHub draft review failed ({status}): {redacted.get('message') or response}"
        )
    return {
        "posted": True,
        "http_status": status,
        "review_id": response.get("id"),
        "state": response.get("state") or "PENDING",
        "html_url": response.get("html_url"),
        "evidence": redacted,
    }


def post_if_allowed(
    *,
    report: Mapping[str, Any],
    findings: list[dict[str, Any]],
    repo_slug: str,
    pull_number: int,
    allowlist_path: Path | None = None,
    repo_root: Path | None = None,
    severity_floor: str | None = None,
    commit_id: str | None = None,
    token: str | None = None,
    http_client: HttpClient | None = None,
) -> dict[str, Any]:
    """Post a draft review when allowlisted; otherwise refuse with evidence."""
    path = resolve_allowlist_path(Path(repo_root or "."), allowlist_path)
    allowlist = load_allowlist(path)
    floor = normalize_severity_floor(
        severity_floor or str(allowlist.get("severity_floor") or "medium")
    )
    selected = select_findings_for_draft(findings, severity_floor=floor)
    evidence_base = {
        "allowlist_path": str(path) if path else "",
        "repo_slug": repo_slug,
        "pull_number": pull_number,
        "severity_floor": floor,
        "selected_finding_ids": [f.get("id") for f in selected],
        "allowed": repo_allowed(repo_slug, allowlist),
    }

    if not repo_allowed(repo_slug, allowlist):
        return {
            "posted": False,
            "reason": "repo_not_allowlisted",
            "evidence": redact_secrets(evidence_base),
        }

    body = render_draft_body(report, selected)
    try:
        result = create_pending_review(
            repo_slug=repo_slug,
            pull_number=pull_number,
            body=body,
            commit_id=commit_id,
            token=token,
            http_client=http_client,
        )
    except GitHubDraftError as exc:
        return {
            "posted": False,
            "reason": str(exc),
            "evidence": redact_secrets({**evidence_base, "error": str(exc)}),
        }

    return {
        "posted": True,
        "reason": "posted_pending_draft",
        "review_id": result.get("review_id"),
        "state": result.get("state"),
        "html_url": result.get("html_url"),
        "evidence": redact_secrets({**evidence_base, **(result.get("evidence") or {})}),
    }


def write_draft_evidence(repo_root: Path, run_id: str, result: Mapping[str, Any]) -> Path:
    out = Path(repo_root) / ".agent" / "evidence" / "code-review" / run_id / "github-draft.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = redact_secrets(dict(result))
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
