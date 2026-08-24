"""Deterministic Skill ranking against required capabilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_WEIGHTS: dict[str, float] = {
    "capability_overlap": 0.45,
    "stack_match": 0.20,
    "lifecycle_stage": 0.15,
    "security_bonus": 0.10,
    "agent_affinity": 0.10,
}

WEIGHT_KEYS = tuple(DEFAULT_WEIGHTS.keys())

LIFECYCLE_SCORES = {
    "PROVEN_SKILL": 1.0,
    "AVAILABLE_SKILL": 0.7,
    "APPROVED": 0.6,
    "SANDBOX_TESTED": 0.5,
    "SECURITY_REVIEWED": 0.4,
    "ANALYZED": 0.3,
    "DISCOVERED": 0.0,
}

SECURITY_SKILL_IDS = frozenset(
    {
        "security-review",
        "dependency-supply-chain",
    }
)

_weights_cache: dict[str, float] | None = None


def default_weights_path() -> Path:
    return Path(__file__).resolve().parent / "weights.json"


def normalize_weights(raw: dict[str, Any]) -> dict[str, float]:
    """Validate and coerce a weights map to the canonical key set."""
    missing = [key for key in WEIGHT_KEYS if key not in raw]
    if missing:
        raise ValueError(f"weights missing keys: {missing}")
    out: dict[str, float] = {}
    for key in WEIGHT_KEYS:
        value = float(raw[key])
        if value < 0:
            raise ValueError(f"weight {key} must be non-negative")
        out[key] = value
    return out


def load_weights(path: Path | None = None, *, force_reload: bool = False) -> dict[str, float]:
    """Load matcher weights from JSON (defaults identical to historical hard-coded WEIGHTS)."""
    global _weights_cache
    if _weights_cache is not None and not force_reload and path is None:
        return dict(_weights_cache)

    target = Path(path) if path is not None else default_weights_path()
    if target.is_file():
        with target.open(encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise ValueError(f"weights file must be object: {target}")
        loaded = normalize_weights(raw)
    else:
        loaded = dict(DEFAULT_WEIGHTS)

    if path is None:
        _weights_cache = dict(loaded)
    return dict(loaded)


def reload_weights(path: Path | None = None) -> dict[str, float]:
    """Force-reload module WEIGHTS from disk (used after Captain-flagged apply)."""
    global WEIGHTS, _weights_cache
    loaded = load_weights(path, force_reload=True)
    if path is None or Path(path).resolve() == default_weights_path().resolve():
        _weights_cache = dict(loaded)
        WEIGHTS.clear()
        WEIGHTS.update(loaded)
    return dict(loaded)


def get_weights() -> dict[str, float]:
    return load_weights()


def write_weights(path: Path, weights: dict[str, float]) -> Path:
    normalized = normalize_weights(weights)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(normalized, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


# Module-level WEIGHTS mirrors historical import sites; kept in sync via reload_weights.
WEIGHTS: dict[str, float] = load_weights()


@dataclass
class RankedSkill:
    skill_id: str
    score: float
    scoring_breakdown: list[dict[str, str | float]]


def _overlap_score(required: set[str], provided: set[str]) -> float:
    if not required:
        return 0.0
    if not provided:
        return 0.0
    return len(required & provided) / len(required)


def _stack_score(required_stacks: set[str], compatible_stacks: set[str]) -> float:
    if not required_stacks:
        return 0.5
    if "any" in compatible_stacks:
        return 0.6
    if not compatible_stacks:
        return 0.0
    return len(required_stacks & compatible_stacks) / len(required_stacks)


def _lifecycle_score(stage: str | None) -> float:
    return LIFECYCLE_SCORES.get(stage or "", 0.0)


def _security_bonus(skill_id: str, security_sensitive: bool) -> float:
    if not security_sensitive:
        return 0.0
    if skill_id in SECURITY_SKILL_IDS:
        return 1.0
    return 0.0


def _affinity_score(skill: dict, preferred_profile: str | None) -> float:
    if not preferred_profile:
        return 0.5
    affinities = set(skill.get("agent_affinity") or [])
    if preferred_profile in affinities:
        return 1.0
    return 0.0


def is_eligible_skill(skill: dict) -> bool:
    """Candidates and non-skills are never ranked for execution."""
    if skill.get("kind") != "skill":
        return False
    if skill.get("approved_for_execution") is False:
        return False
    lifecycle = skill.get("lifecycle_stage", "")
    if lifecycle == "DISCOVERED":
        return False
    return True


def score_skill(
    skill: dict,
    required_capabilities: list[str],
    *,
    stacks: list[str] | None = None,
    security_sensitive: bool = False,
    preferred_profile: str | None = None,
    weights: dict[str, float] | None = None,
) -> RankedSkill:
    skill_id = str(skill["id"])
    provided = set(skill.get("capabilities_provided") or [])
    required = set(required_capabilities)
    required_stacks = set(stacks or [])
    compatible = set(skill.get("compatible_stacks") or [])
    active = normalize_weights(weights) if weights is not None else get_weights()

    overlap = _overlap_score(required, provided)
    stack = _stack_score(required_stacks, compatible)
    lifecycle = _lifecycle_score(skill.get("lifecycle_stage"))
    security = _security_bonus(skill_id, security_sensitive)
    affinity = _affinity_score(skill, preferred_profile)

    total = (
        overlap * active["capability_overlap"]
        + stack * active["stack_match"]
        + lifecycle * active["lifecycle_stage"]
        + security * active["security_bonus"]
        + affinity * active["agent_affinity"]
    )

    breakdown = [
        {
            "factor": "capability_overlap",
            "score": round(overlap * active["capability_overlap"], 4),
            "note": f"matched {len(required & provided)}/{len(required) or 0} required",
        },
        {
            "factor": "stack_match",
            "score": round(stack * active["stack_match"], 4),
            "note": f"stacks={sorted(required_stacks)} compatible={sorted(compatible)}",
        },
        {
            "factor": "lifecycle_stage",
            "score": round(lifecycle * active["lifecycle_stage"], 4),
            "note": str(skill.get("lifecycle_stage", "unknown")),
        },
        {
            "factor": "security_bonus",
            "score": round(security * active["security_bonus"], 4),
            "note": f"security_sensitive={security_sensitive}",
        },
        {
            "factor": "agent_affinity",
            "score": round(affinity * active["agent_affinity"], 4),
            "note": f"preferred_profile={preferred_profile or 'none'}",
        },
    ]

    return RankedSkill(
        skill_id=skill_id,
        score=round(total, 4),
        scoring_breakdown=breakdown,
    )


def rank_skills(
    skills: list[dict],
    required_capabilities: list[str],
    *,
    stacks: list[str] | None = None,
    security_sensitive: bool = False,
    preferred_profile: str | None = None,
    min_score: float = 0.0,
    weights: dict[str, float] | None = None,
) -> list[RankedSkill]:
    ranked: list[RankedSkill] = []
    for skill in skills:
        if not is_eligible_skill(skill):
            continue
        result = score_skill(
            skill,
            required_capabilities,
            stacks=stacks,
            security_sensitive=security_sensitive,
            preferred_profile=preferred_profile,
            weights=weights,
        )
        if result.score >= min_score:
            ranked.append(result)
    ranked.sort(key=lambda item: (-item.score, item.skill_id))
    return ranked


def find_capability_gaps(required_capabilities: list[str], skills: list[dict]) -> list[str]:
    """Return required capabilities no eligible Skill provides."""
    provided: set[str] = set()
    for skill in skills:
        if not is_eligible_skill(skill):
            continue
        provided.update(skill.get("capabilities_provided") or [])
    return [cap for cap in required_capabilities if cap not in provided]
