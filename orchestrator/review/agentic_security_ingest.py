"""Opt-in Cursor Agentic Security Review ingest (M39 / Phase B).

Hermetic default `northstar review` is unchanged. This module normalizes an
exported Cursor Security Reviewer / `/review-security` artifact into NorthStar
finding shapes under `.agent/evidence/review/<run-id>/agentic-security/`.

Refuse-closed without an allowlisted repo (same posture as M30 GitHub drafts).
Never invokes Cursor Cloud; never auto-merges.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml

from orchestrator.integrations.events import redact_secrets
from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA_VERSION = "northstar.agentic_security_allowlist.v1"
_REPO_SLUG = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

# Cursor Security Reviewer severities → NorthStar
_SEVERITY_MAP = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "warning": "medium",
    "low": "low",
    "info": "info",
    "informational": "info",
}


class AgenticSecurityIngestError(ValueError):
    """Raised when ingest cannot proceed safely."""


def map_severity(value: str | None) -> str:
    raw = (value or "medium").strip().lower()
    if raw not in _SEVERITY_MAP:
        raise AgenticSecurityIngestError(f"unknown Cursor severity: {value!r}")
    return _SEVERITY_MAP[raw]


def resolve_allowlist_path(repo_root: Path, explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        return Path(explicit)
    candidates = (
        Path(repo_root) / ".agent" / "review" / "agentic-security-allowlist.yml",
        Path(repo_root) / ".agent" / "review" / "agentic-security-allowlist.yaml",
        Path(repo_root) / ".agent" / "review" / "agentic-security-allowlist.json",
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
            "enabled": False,
            "notes": "",
        }
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise AgenticSecurityIngestError("allowlist must be an object")
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("repos", [])
    data.setdefault("enabled", False)
    data.setdefault("notes", "")
    data["schema_version"] = SCHEMA_VERSION
    data["repos"] = [str(r).strip() for r in (data.get("repos") or []) if str(r).strip()]
    data["enabled"] = bool(data.get("enabled"))
    try:
        validate_document(data, "agentic-security-allowlist.schema.json")
    except (FileNotFoundError, ValidationError) as exc:
        raise AgenticSecurityIngestError(str(exc)) from exc
    return data


def repo_allowed(slug: str, allowlist: Mapping[str, Any]) -> bool:
    if not allowlist.get("enabled"):
        return False
    slug = (slug or "").strip()
    if not _REPO_SLUG.match(slug):
        return False
    allowed = {str(r).strip().lower() for r in (allowlist.get("repos") or [])}
    return slug.lower() in allowed


def _extract_findings(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        raise AgenticSecurityIngestError("artifact must be a JSON object or array")
    for key in ("findings", "issues", "results", "vulnerabilities"):
        val = payload.get(key)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]
    # Single finding object
    if any(k in payload for k in ("severity", "title", "id", "description")):
        return [payload]
    raise AgenticSecurityIngestError(
        "artifact missing findings/issues/results array (or a single finding object)"
    )


def normalize_finding(raw: Mapping[str, Any], *, index: int) -> dict[str, Any]:
    sev = map_severity(
        str(raw.get("severity") or raw.get("level") or raw.get("priority") or "medium")
    )
    fid = str(raw.get("id") or raw.get("finding_id") or f"agentic-sec-{index + 1}")
    title = str(raw.get("title") or raw.get("name") or raw.get("summary") or fid)
    detail = str(
        raw.get("detail")
        or raw.get("description")
        or raw.get("message")
        or raw.get("body")
        or ""
    )
    paths = raw.get("evidence_paths") or raw.get("paths") or raw.get("files") or []
    if isinstance(paths, str):
        paths = [paths]
    if not isinstance(paths, list):
        paths = []
    paths = [str(p) for p in paths if str(p).strip()]
    return {
        "id": fid,
        "title": title,
        "detail": detail,
        "severity": sev,
        "status": "imported",
        "skill": "security-review",
        "category": "agentic-security",
        "source": "cursor-agentic-security",
        "evidence_paths": paths,
        "confidence": float(raw.get("confidence") or 0.75),
        "suggested_fix": str(raw.get("suggested_fix") or raw.get("fix") or ""),
        "cursor": {
            k: raw.get(k)
            for k in ("url", "link", "fix_in_cursor", "rule_id")
            if raw.get(k) is not None
        },
    }


def normalize_artifact(payload: Any) -> list[dict[str, Any]]:
    findings = _extract_findings(payload)
    return [normalize_finding(f, index=i) for i, f in enumerate(findings)]


def ingest_agentic_security(
    *,
    repo_root: Path | str,
    artifact_path: Path | str,
    repo_slug: str,
    run_id: str | None = None,
    allowlist_path: Path | None = None,
    outcomes_proposal: bool = False,
) -> dict[str, Any]:
    """Ingest a Cursor Security artifact into evidence. Fail-closed on allowlist."""
    root = Path(repo_root)
    artifact = Path(artifact_path)
    if not artifact.is_file():
        raise AgenticSecurityIngestError(f"artifact not found: {artifact}")

    alist_path = resolve_allowlist_path(root, allowlist_path)
    allowlist = load_allowlist(alist_path)
    gate = {
        "enabled": bool(allowlist.get("enabled")),
        "allowlist_path": str(alist_path) if alist_path else "",
        "repo": repo_slug,
        "allowed": repo_allowed(repo_slug, allowlist),
    }
    if not gate["allowed"]:
        raise AgenticSecurityIngestError(
            "agentic-security ingest refuse-closed: repo not allowlisted or "
            "allowlist.enabled=false (Captain must opt in; same posture as M30)"
        )

    text = artifact.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AgenticSecurityIngestError(f"artifact is not JSON: {exc}") from exc

    findings = normalize_artifact(payload)
    rid = (run_id or "").strip() or datetime.now(timezone.utc).strftime(
        "agentic-%Y%m%dT%H%M%SZ"
    )
    out_dir = root / ".agent" / "evidence" / "review" / rid / "agentic-security"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "schema_version": "northstar.agentic_security_ingest.v1",
        "run_id": rid,
        "repo": repo_slug,
        "source_artifact": str(artifact),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "gate": gate,
        "finding_count": len(findings),
        "findings": findings,
        "hermetic_default_unchanged": True,
        "notes": (
            "Opt-in ingest only. Default northstar review remains hermetic "
            "specialists (M28–M37). Never auto-merge."
        ),
    }
    if outcomes_proposal:
        report["outcomes_proposal"] = [
            {
                "finding_id": f["id"],
                "proposed_status": "accepted",
                "note": "Captain may record via M31 outcomes; proposal-only here",
            }
            for f in findings
        ]

    redacted = redact_secrets(report)
    (out_dir / "findings.json").write_text(
        json.dumps(redacted, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_lines = [
        f"# Agentic Security ingest — `{rid}`",
        "",
        f"- Repo: `{repo_slug}`",
        f"- Findings: **{len(findings)}**",
        f"- Source: `{artifact}`",
        "",
        "| Id | Severity | Title |",
        "|---|---|---|",
    ]
    for f in findings:
        md_lines.append(
            f"| `{f['id']}` | {f['severity']} | {f['title'].replace('|', '/')} |"
        )
    (out_dir / "SUMMARY.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return redacted
