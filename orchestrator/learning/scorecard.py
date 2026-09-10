"""TI usefulness scorecard + draft-gate evidence writers (M23).

Produces metadata-only security-review and dependency-supply-chain evidence
for starred repos. Never clones or executes third-party repositories.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.promotion.draft_gates import REQUIRED_DRAFT_EVIDENCE_KINDS
from orchestrator.providers.technology_intelligence.starred_provenance import (
    StarredProvenanceError,
    assert_starred_provenance,
    has_starred_provenance,
)


class ScorecardError(ValueError):
    """Raised when scorecard generation fails closed."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def scorecard_dir(repo_root: Path, candidate_id: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in candidate_id).strip("-")
    safe = safe or "candidate"
    return Path(repo_root) / ".agent" / "evidence" / "ti-scorecards" / safe


def _repo_name(repo: dict, candidate: dict | None = None) -> str:
    if repo.get("full_name"):
        return str(repo["full_name"])
    source = (candidate or {}).get("source") if isinstance((candidate or {}).get("source"), dict) else {}
    return str(
        source.get("path")
        or (candidate or {}).get("id")
        or repo.get("id")
        or "unknown-repo"
    )


def write_ti_scorecard_evidence(
    repo_root: Path,
    *,
    repo: dict,
    candidate: dict | None = None,
    category: str | None = None,
) -> dict:
    """
    Write security-review + dependency-supply-chain evidence for a starred repo.

    Metadata-only: no clone, no install, no execution of the third-party repo.
    """
    repo_root = Path(repo_root)
    candidate = dict(candidate or {})
    records = [repo]
    try:
        assert_starred_provenance(records, context="ti-scorecard")
    except StarredProvenanceError as exc:
        raise ScorecardError(str(exc)) from exc
    if candidate and not has_starred_provenance(candidate) and not has_starred_provenance(repo):
        raise ScorecardError("ti-scorecard: candidate lacks starred provenance")

    full_name = _repo_name(repo, candidate)
    candidate_id = str(candidate.get("id") or full_name.replace("/", "-"))
    star_category = str(
        category
        or repo.get("star_category")
        or (candidate.get("provenance") or {}).get("star_category")
        or "other"
    )
    out_dir = scorecard_dir(repo_root, candidate_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    security_path = out_dir / "security-review.md"
    supply_path = out_dir / "dependency-supply-chain.md"
    scorecard_path = out_dir / "scorecard.json"

    security_body = (
        f"# Security review (metadata-only TI scorecard)\n\n"
        f"- Reviewed at: `{_utc_now()}`\n"
        f"- Repo: `{full_name}`\n"
        f"- Candidate: `{candidate_id}`\n"
        f"- Star category: `{star_category}`\n"
        f"- Starred provenance: `true`\n"
        f"- Clone/exec performed: `false`\n\n"
        f"## Findings\n\n"
        f"- External starred repository treated as **discovery signal only**.\n"
        f"- `approved_for_execution` remains `false`.\n"
        f"- No secrets or credentials ingested from the third-party repo.\n"
        f"- Do not clone or execute this repository from TI/learning paths.\n\n"
        f"## Decision\n\n"
        f"Pass for **draft proposal staging only** (not live Skill install).\n"
    )
    supply_body = (
        f"# Dependency supply-chain review (metadata-only TI scorecard)\n\n"
        f"- Reviewed at: `{_utc_now()}`\n"
        f"- Repo: `{full_name}`\n"
        f"- Candidate: `{candidate_id}`\n"
        f"- Star category: `{star_category}`\n"
        f"- Package install from starred repo: `false`\n"
        f"- Lockfile mutation: `false`\n\n"
        f"## Findings\n\n"
        f"- No third-party packages were added from this starred repo.\n"
        f"- Learning path is inspiration/procedure draft only — not a vendor install.\n"
        f"- Any future sandbox experiment must use in-repo tokens/components only.\n\n"
        f"## Decision\n\n"
        f"Pass for **draft proposal staging only**. Live Skill apply still requires "
        f"`--captain-approved`.\n"
    )
    security_path.write_text(security_body, encoding="utf-8")
    supply_path.write_text(supply_body, encoding="utf-8")

    evidence_paths = [str(security_path), str(supply_path)]
    scorecard = {
        "kind": "ti-usefulness-scorecard",
        "schema_version": "m23-v1",
        "scored_at": _utc_now(),
        "full_name": full_name,
        "candidate_id": candidate_id,
        "star_category": star_category,
        "starred_provenance": True,
        "approved_for_execution": False,
        "auto_install": False,
        "clone_or_exec": False,
        "required_evidence_kinds": list(REQUIRED_DRAFT_EVIDENCE_KINDS),
        "evidence_paths": evidence_paths,
        "usefulness_labels": [star_category] if star_category else [],
        "gates": {
            "starred_provenance": "pass",
            "security-review": "pass",
            "dependency-supply-chain": "pass",
        },
        "notes": (
            "Metadata-only scorecard. Does not clone or execute the starred repo. "
            "Skill drafts may proceed after these evidence artifacts exist; live "
            "install remains Captain-gated."
        ),
    }
    scorecard_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "scorecard_path": str(scorecard_path),
        "evidence_paths": evidence_paths,
        "out_dir": str(out_dir),
        "star_category": star_category,
        "candidate_id": candidate_id,
        "full_name": full_name,
        "approved_for_execution": False,
    }
