"""Orchestrate proposal-only behavior pattern learning (M47)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from orchestrator.behavior.enabled import require_behavior_learn_enabled
from orchestrator.behavior.patterns.detect import patterns_with_candidates
from orchestrator.behavior.patterns.store import (
    BehaviorPatternStoreError,
    list_candidates,
    list_patterns,
    load_pattern,
    write_candidate,
    write_pattern,
)


class BehaviorLearnServiceError(ValueError):
    """Operator-facing learn errors."""


def scan_and_persist(repo_root: Path) -> dict[str, Any]:
    require_behavior_learn_enabled()
    root = Path(repo_root).resolve()
    written_patterns: list[str] = []
    written_candidates: list[str] = []
    pairs = patterns_with_candidates(root)
    try:
        for pattern, candidate in pairs:
            # Stable overwrite by pattern_id (deterministic)
            p_path = write_pattern(root, pattern)
            c_path = write_candidate(root, candidate)
            written_patterns.append(str(p_path))
            written_candidates.append(str(c_path))
    except BehaviorPatternStoreError as exc:
        raise BehaviorLearnServiceError(str(exc)) from exc
    return {
        "status": "scanned",
        "pattern_count": len(written_patterns),
        "candidate_count": len(written_candidates),
        "patterns": written_patterns,
        "candidates": written_candidates,
    }


def list_learned_patterns(repo_root: Path) -> dict[str, Any]:
    require_behavior_learn_enabled()
    patterns = list_patterns(repo_root)
    return {"count": len(patterns), "patterns": patterns}


def show_pattern(repo_root: Path, pattern_id: str) -> dict[str, Any]:
    require_behavior_learn_enabled()
    try:
        pattern = load_pattern(repo_root, pattern_id)
    except BehaviorPatternStoreError as exc:
        raise BehaviorLearnServiceError(str(exc)) from exc
    related = [
        c
        for c in list_candidates(repo_root)
        if c.get("pattern_id") == pattern.get("pattern_id")
    ]
    return {"pattern": pattern, "candidates": related}


def export_patterns_csv(repo_root: Path, dest: Path) -> Path:
    require_behavior_learn_enabled()
    patterns = list_patterns(repo_root)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "pattern_id",
        "signal",
        "polarity",
        "agent",
        "skill_id",
        "occurrence_count",
        "min_occurrence",
        "mean_score",
        "threshold",
        "summary",
        "created_at",
    ]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for pattern in patterns:
            writer.writerow({k: pattern.get(k, "") for k in fieldnames})
    return dest
