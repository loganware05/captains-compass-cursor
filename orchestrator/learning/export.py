"""Export categorized Stars TI candidates into staging JSON (M19)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from orchestrator.providers.technology_intelligence.github_stars_provider import (
    discover_candidates_from_records,
)
from orchestrator.providers.technology_intelligence.stars_categorization import (
    read_categorized_records,
)
from orchestrator.promotion.advance import staging_dir

_SAFE = re.compile(r"[^a-z0-9]+")


class LearningExportError(ValueError):
    """Raised when TI → staging export fails."""


def suggest_skill_slug_from_candidate(candidate: dict) -> str:
    """Derive a draft slug from candidate id / source path."""
    source = candidate.get("source") if isinstance(candidate.get("source"), dict) else {}
    provenance = candidate.get("provenance") if isinstance(candidate.get("provenance"), dict) else {}
    raw = str(
        provenance.get("skill_slug")
        or source.get("path")
        or candidate.get("id")
        or "candidate"
    )
    slug = _SAFE.sub("-", raw.lower()).strip("-") or "candidate"
    if not slug.startswith("from-stars-"):
        slug = f"from-stars-{slug}"
    return slug[:80]


def enrich_candidate_with_category(candidate: dict, repo: dict) -> dict:
    """Attach star category metadata into notes / provenance."""
    out = dict(candidate)
    category = str(repo.get("star_category") or "")
    confidence = repo.get("star_category_confidence")
    provenance = dict(out.get("provenance") or {})
    if category:
        provenance["star_category"] = category
        if confidence is not None:
            provenance["star_category_confidence"] = confidence
        notes = str(out.get("notes") or "")
        if f"[{category}]" not in notes:
            out["notes"] = f"[{category}] {notes}".strip()
        signal = str(out.get("discovery_signal") or "")
        if "category:" not in signal:
            out["discovery_signal"] = f"{signal}|category:{category}"
    out["provenance"] = provenance
    out["approved_for_execution"] = False
    return out


def select_categorized_candidates(
    repo_root: Path,
    objective: str,
    *,
    top_n: int = 3,
    category_filter: str | None = None,
) -> list[tuple[dict, dict]]:
    """
    Return list of (candidate_dict, source_repo_record) from categorized Stars.

    Requires prior categorize-github-stars output under
    `.agent/ti/github-stars-categorized/categorized.json`.
    """
    records = read_categorized_records(repo_root)
    if not records:
        raise LearningExportError(
            "no categorized Stars records; run categorize-github-stars.sh first"
        )
    if category_filter:
        records = [
            r for r in records if str(r.get("star_category") or "") == category_filter
        ]
        if not records:
            raise LearningExportError(
                f"no categorized records for category {category_filter!r}"
            )

    ranked = discover_candidates_from_records(records, objective, top_n=top_n)
    by_name = {str(r.get("full_name") or ""): r for r in records}
    pairs: list[tuple[dict, dict]] = []
    for cand in ranked:
        repo = by_name.get(cand.source_path)
        if repo is None:
            for name, row in by_name.items():
                if name and (name in cand.id or cand.source_path in name):
                    repo = row
                    break
        if repo is None:
            repo = {
                "full_name": cand.source_path,
                "description": cand.notes,
                "star_category": "",
            }
        enriched = enrich_candidate_with_category(cand.to_dict(), repo)
        pairs.append((enriched, repo))
    return pairs


def write_staging_from_candidate(repo_root: Path, candidate: dict) -> Path:
    """Write ANALYZED candidate JSON under staging (never live Skills)."""
    if candidate.get("approved_for_execution") is not False:
        raise LearningExportError("candidates must keep approved_for_execution=false")
    out = dict(candidate)
    out["approved_for_execution"] = False
    if out.get("lifecycle_stage") in (None, "DISCOVERED"):
        out["lifecycle_stage"] = "ANALYZED"
    out_dir = staging_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{out['id']}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def export_categorized_to_staging(
    repo_root: Path,
    objective: str,
    *,
    top_n: int = 3,
    category_filter: str | None = None,
) -> list[dict]:
    """Select categorized candidates and write staging files."""
    pairs = select_categorized_candidates(
        repo_root,
        objective,
        top_n=top_n,
        category_filter=category_filter,
    )
    exported: list[dict] = []
    for candidate, repo in pairs:
        path = write_staging_from_candidate(repo_root, candidate)
        exported.append(
            {
                "staging_path": str(path),
                "candidate_id": candidate.get("id"),
                "full_name": repo.get("full_name"),
                "star_category": repo.get("star_category"),
                "skill_slug": suggest_skill_slug_from_candidate(candidate),
                "candidate": candidate,
                "repo": repo,
            }
        )
    return exported
