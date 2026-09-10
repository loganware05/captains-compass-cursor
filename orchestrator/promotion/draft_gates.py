"""Skill-draft evidence gates (M23).

Before any Skill draft is written, require security-review and
dependency-supply-chain evidence artifacts. Fail closed if missing.
"""

from __future__ import annotations

from pathlib import Path

REQUIRED_DRAFT_EVIDENCE_KINDS = (
    "security-review",
    "dependency-supply-chain",
)


class SkillDraftGateError(ValueError):
    """Raised when Skill draft evidence gates fail closed."""


def _normalize_kind(path: Path) -> str:
    name = path.name.lower()
    stem = path.stem.lower()
    parent = path.parent.name.lower()
    haystack = f"{parent}/{name}"
    if "security-review" in haystack or stem in {"security-review", "security"}:
        return "security-review"
    if (
        "dependency-supply-chain" in haystack
        or "supply-chain" in haystack
        or stem in {"dependency-supply-chain", "supply-chain"}
    ):
        return "dependency-supply-chain"
    return stem


def classify_evidence_paths(evidence_paths: list[str | Path]) -> dict[str, list[str]]:
    """Map required kinds to matching evidence paths that exist on disk."""
    found: dict[str, list[str]] = {kind: [] for kind in REQUIRED_DRAFT_EVIDENCE_KINDS}
    for raw in evidence_paths:
        path = Path(raw)
        if not path.is_file():
            continue
        kind = _normalize_kind(path)
        if kind in found:
            found[kind].append(str(path))
    return found


def require_skill_draft_evidence(
    evidence_paths: list[str | Path] | None,
    *,
    context: str = "skill-draft",
) -> dict[str, list[str]]:
    """Fail closed unless both required evidence kinds are present as files."""
    paths = list(evidence_paths or [])
    if not paths:
        raise SkillDraftGateError(
            f"{context}: Skill draft requires evidence artifacts for "
            f"{', '.join(REQUIRED_DRAFT_EVIDENCE_KINDS)}; none provided"
        )
    missing_files = [str(p) for p in paths if not Path(p).is_file()]
    if missing_files:
        raise SkillDraftGateError(
            f"{context}: evidence path(s) missing on disk: {', '.join(missing_files[:5])}"
        )
    classified = classify_evidence_paths(paths)
    missing_kinds = [kind for kind, hits in classified.items() if not hits]
    if missing_kinds:
        raise SkillDraftGateError(
            f"{context}: Skill draft fail-closed — missing required evidence "
            f"kind(s): {', '.join(missing_kinds)}. "
            "Produce security-review and dependency-supply-chain artifacts first "
            "(see skill-learning-loop / TI scorecard)."
        )
    return classified
