"""Deterministic pattern detector over the M46 behavior ledger (M47)."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from orchestrator.behavior.ledger import list_records
from orchestrator.behavior.patterns.quality import (
    min_occurrence,
    polarity_for_signal,
    qualifying_signals,
)
from orchestrator.behavior.patterns.store import build_candidate, build_pattern
from orchestrator.behavior.thresholds import load_thresholds


def _skill_keys(record: dict[str, Any]) -> list[str]:
    skills = [str(s) for s in (record.get("skill_ids") or []) if str(s)]
    return skills or [""]


def detect_patterns(repo_root: Path) -> list[dict[str, Any]]:
    """Scan ledger and return pattern records that meet min_occurrence."""
    thresholds = load_thresholds()
    need = min_occurrence()
    # key -> {evaluation_ids, scores, threshold}
    buckets: dict[tuple[str, str, str, str], dict[str, Any]] = defaultdict(
        lambda: {"evaluation_ids": [], "scores": [], "threshold": 0.0}
    )

    for record in list_records(repo_root):
        evaluation_id = str(record.get("evaluation_id") or "")
        if not evaluation_id:
            continue
        agent = str(record.get("agent") or "")
        for signal, score, floor in qualifying_signals(record, thresholds=thresholds):
            polarity = polarity_for_signal(signal)
            for skill_id in _skill_keys(record):
                key = (polarity, signal, agent, skill_id)
                bucket = buckets[key]
                if evaluation_id not in bucket["evaluation_ids"]:
                    bucket["evaluation_ids"].append(evaluation_id)
                    bucket["scores"].append(score)
                    bucket["threshold"] = floor

    patterns: list[dict[str, Any]] = []
    for (polarity, signal, agent, skill_id), bucket in sorted(buckets.items()):
        ids = list(bucket["evaluation_ids"])
        if len(ids) < need:
            continue
        patterns.append(
            build_pattern(
                signal=signal,
                polarity=polarity,
                agent=agent,
                skill_id=skill_id,
                evidence_evaluation_ids=ids,
                scores=list(bucket["scores"]),
                threshold=float(bucket["threshold"]),
                min_occurrence=need,
            )
        )
    return patterns


def patterns_with_candidates(
    repo_root: Path,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Detect patterns and pair each with a proposal-only candidate."""
    out: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for pattern in detect_patterns(repo_root):
        out.append((pattern, build_candidate(pattern)))
    return out
