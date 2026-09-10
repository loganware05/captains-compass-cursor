"""Starred-only provenance gate for external-repo Technology Intelligence (M23).

External repository records must carry explicit starred provenance before they
may enter categorization, live/cache TI export, or the skill learning loop.
Arbitrary non-starred URL ingest is rejected fail-closed.
"""

from __future__ import annotations

from typing import Any

STARRED_PROVENANCE_KEYS = (
    "starred",
    "starred_provenance",
    "from_github_stars",
)

TRUSTED_STARRED_SOURCES = (
    "gh api user/starred",
    "fixtures:github-stars-recorded",
    "ti-cache:starred-repos.json",
    "github-stars",
    "github-stars-recorded",
    "github-stars-cached",
    "github-stars-categorized",
)


class StarredProvenanceError(ValueError):
    """Raised when an external repo lacks starred provenance."""


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str) and value.strip().lower() in {"1", "true", "yes", "starred"}:
        return True
    return False


def has_starred_provenance(record: dict, *, source: str | None = None) -> bool:
    """Return True when a repo/candidate record is starred-provenance safe."""
    if not isinstance(record, dict):
        return False

    for key in STARRED_PROVENANCE_KEYS:
        if _truthy(record.get(key)):
            return True

    provenance = record.get("provenance")
    if isinstance(provenance, dict):
        for key in STARRED_PROVENANCE_KEYS:
            if _truthy(provenance.get(key)):
                return True
        if _truthy(provenance.get("starred")):
            return True

    source_obj = record.get("source")
    if isinstance(source_obj, dict) and _truthy(source_obj.get("starred")):
        return True

    signal = " ".join(
        [
            str(record.get("star_signal") or ""),
            str(record.get("discovery_signal") or ""),
            str(source or ""),
            str(record.get("ti_source") or ""),
        ]
    ).lower()
    if "github-stars" in signal or "user/starred" in signal:
        return True

    src = str(source or record.get("ti_source") or "").strip().lower()
    for trusted in TRUSTED_STARRED_SOURCES:
        if trusted in src:
            return True

    return False


def stamp_starred_provenance(
    records: list[dict],
    *,
    source: str = "github-stars",
) -> list[dict]:
    """Return copies of records with explicit starred provenance fields."""
    stamped: list[dict] = []
    for row in records:
        if not isinstance(row, dict):
            continue
        out = dict(row)
        out["starred"] = True
        out["starred_provenance"] = True
        out["from_github_stars"] = True
        out["ti_source"] = str(out.get("ti_source") or source)
        provenance = dict(out.get("provenance") or {})
        provenance["starred"] = True
        provenance["starred_provenance"] = True
        provenance["source"] = provenance.get("source") or source
        out["provenance"] = provenance
        source_obj = dict(out.get("source") or {}) if isinstance(out.get("source"), dict) else {}
        if source_obj:
            source_obj["starred"] = True
            out["source"] = source_obj
        stamped.append(out)
    return stamped


def assert_starred_provenance(
    records: list[dict],
    *,
    source: str | None = None,
    context: str = "technology-intelligence",
) -> list[dict]:
    """Fail closed unless every record has starred provenance.

    Returns the same list when valid so callers can chain.
    """
    if not records:
        return records
    rejected: list[str] = []
    for idx, row in enumerate(records):
        if has_starred_provenance(row, source=source):
            continue
        name = f"index:{idx}"
        if isinstance(row, dict):
            source_obj = row.get("source") if isinstance(row.get("source"), dict) else {}
            name = str(
                row.get("full_name")
                or row.get("id")
                or source_obj.get("path")
                or f"index:{idx}"
            )
        rejected.append(name)
    if rejected:
        sample = ", ".join(rejected[:5])
        more = f" (+{len(rejected) - 5} more)" if len(rejected) > 5 else ""
        raise StarredProvenanceError(
            f"{context}: rejecting non-starred external repo feed "
            f"({len(rejected)} record(s)): {sample}{more}. "
            "External repos must enter TI via GitHub Stars (starred provenance)."
        )
    return records
