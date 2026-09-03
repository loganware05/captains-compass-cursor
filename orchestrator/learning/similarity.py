"""Similarity matching between Stars candidates and existing Compass Skills (M19)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.registry.yaml_simple import load_simple_yaml

_TOKEN = re.compile(r"[a-z0-9]{2,}", re.I)
_SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Default threshold for "processes are similar" (overlap / Jaccard on tokens).
DEFAULT_SIMILARITY_THRESHOLD = 0.28

# Boilerplate tokens that inflate overlap against long SKILL.md bodies.
STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "from",
        "this",
        "that",
        "when",
        "skill",
        "skills",
        "use",
        "using",
        "captain",
        "compass",
        "approved",
        "approval",
        "execution",
        "github",
        "stars",
        "starred",
        "live",
        "repo",
        "repos",
        "repository",
        "candidate",
        "candidates",
        "procedure",
        "prohibited",
        "actions",
        "notes",
        "review",
        "require",
        "requires",
        "required",
        "never",
        "auto",
        "install",
        "path",
        "json",
        "markdown",
        "true",
        "false",
        "other",
        "category",
        "signal",
        "discovery",
        "provenance",
        "version",
        "kind",
        "type",
        "external",
        "org",
        "example",
    }
)

# Meta / learning / safety-critical Skills should not be improvement targets.
EXCLUDED_IMPROVEMENT_TARGETS = frozenset(
    {
        "skill-learning-loop",
        "candidate-promotion",
        "skill-lifecycle",
        "experience-skill-training",
        "technology-intelligence-live",
        "capability-planning",
        "implementation-planning",
        "experience-routing",
        "bounded-autonomy",
        "compass-evaluator",
        "execution-telemetry",
        "autonomy-budget",
        "harness-gc",
        "pull-request-preparation",
        "worktree-orchestration",
        "repository-discovery",
        "security-review",
        "dependency-supply-chain",
        "persistent-role-promotion",
        "knowledge-steward",
        "external-knowledge-ingest",
        "procedure-playbooks",
        "embedding-providers",
        "hosted-vector-db",
        "package-registry-ti",
    }
)

CATEGORY_HINTS = {
    "frontend-ui": {
        "react-engineering",
        "accessibility-review",
        "playwright-browser-validation",
    },
    "backend-library": {"node-engineering", "postgres-prisma", "python-ml"},
    "devtool": {"docker-cloud", "github-integration", "node-engineering"},
    "ml-data": {"python-ml", "embedding-providers", "hosted-vector-db"},
}


class SkillSimilarityError(ValueError):
    """Raised when similarity / improvement proposal generation fails."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tokenize(text: str) -> set[str]:
    return {
        m.group(0).lower()
        for m in _TOKEN.finditer(text or "")
        if m.group(0).lower() not in STOPWORDS
    }


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def improvement_proposals_dir(repo_root: Path) -> Path:
    return (
        Path(repo_root)
        / ".agent"
        / "capabilities"
        / "candidates"
        / "skill-improvement-proposals"
    )


def load_existing_skills(control_root: Path) -> list[dict]:
    """Load live Skills from `.cursor/skills/*/capability.yaml` (+ SKILL.md text)."""
    skills_root = Path(control_root) / ".cursor" / "skills"
    if not skills_root.is_dir():
        return []
    loaded: list[dict] = []
    for path in sorted(skills_root.iterdir()):
        if not path.is_dir():
            continue
        cap = path / "capability.yaml"
        skill_md = path / "SKILL.md"
        if not cap.is_file() or not skill_md.is_file():
            continue
        try:
            meta = load_simple_yaml(cap.read_text(encoding="utf-8"), str(cap))
        except Exception:
            continue
        slug = str(meta.get("id") or path.name)
        caps = meta.get("capabilities_provided") or []
        if not isinstance(caps, list):
            caps = []
        # Prefer capability/tags/categories over full procedure prose.
        blob = " ".join(
            [
                slug,
                " ".join(str(c) for c in caps),
                " ".join(str(t) for t in (meta.get("tags") or [])),
                " ".join(str(c) for c in (meta.get("categories") or [])),
                # First ~40 lines of SKILL.md (title + when-to-use), not whole body
                "\n".join(skill_md.read_text(encoding="utf-8").splitlines()[:40]),
            ]
        )
        loaded.append(
            {
                "slug": slug,
                "capabilities_provided": [str(c) for c in caps],
                "tokens": tokenize(blob),
                "path": str(path),
            }
        )
    return loaded


def candidate_tokens(candidate: dict, repo: dict | None = None) -> set[str]:
    repo = repo or {}
    topics = repo.get("topics") or []
    topic_text = " ".join(
        str(t.get("name") if isinstance(t, dict) else t) for t in topics
    )
    parts = [
        str(candidate.get("notes") or ""),
        " ".join(str(c) for c in (candidate.get("capabilities_provided") or [])),
        str(repo.get("description") or ""),
        str(repo.get("star_category") or ""),
        topic_text,
        str(repo.get("full_name") or "").replace("/", " "),
    ]
    return tokenize(" ".join(parts))


def find_similar_skills(
    control_root: Path,
    candidate: dict,
    *,
    repo: dict | None = None,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    top_k: int = 3,
) -> list[dict]:
    """Return ranked similar live Skills above threshold."""
    repo = repo or {}
    cand_tokens = candidate_tokens(candidate, repo)
    category = str(
        (candidate.get("provenance") or {}).get("star_category")
        or repo.get("star_category")
        or ""
    )
    hints = CATEGORY_HINTS.get(category, set())
    matches: list[dict] = []
    for skill in load_existing_skills(control_root):
        if skill["slug"] in EXCLUDED_IMPROVEMENT_TARGETS:
            continue
        score = jaccard(cand_tokens, skill["tokens"])
        if cand_tokens:
            overlap = len(cand_tokens & skill["tokens"]) / len(cand_tokens)
        else:
            overlap = 0.0
        flat_caps: set[str] = set()
        for cap in skill["capabilities_provided"]:
            flat_caps |= tokenize(str(cap))
        cap_score = jaccard(cand_tokens, flat_caps)
        if cand_tokens and flat_caps:
            cap_overlap = len(cand_tokens & flat_caps) / len(cand_tokens)
        else:
            cap_overlap = 0.0
        combined = max(score, overlap, cap_score, cap_overlap)
        if skill["slug"] in hints:
            combined = min(1.0, combined + 0.12)
        if combined >= threshold:
            matches.append(
                {
                    "skill_slug": skill["slug"],
                    "similarity": round(combined, 4),
                    "skill_path": skill["path"],
                    "capabilities_provided": skill["capabilities_provided"],
                }
            )
    matches.sort(key=lambda m: (-m["similarity"], m["skill_slug"]))
    return matches[:top_k]


def write_improvement_proposal(
    repo_root: Path,
    candidate: dict,
    match: dict,
    *,
    evidence_paths: list[str] | None = None,
) -> Path:
    """
    Write a proposal to improve an existing Skill — never mutates live SKILL.md.

    Captain must review and apply via PR.
    """
    if candidate.get("approved_for_execution") is not False:
        raise SkillSimilarityError("candidates must keep approved_for_execution=false")
    slug = str(match["skill_slug"])
    if not _SAFE_SLUG.match(slug):
        raise SkillSimilarityError(f"invalid target skill slug: {slug!r}")
    cand_id = str(candidate.get("id") or "candidate")
    safe_id = re.sub(r"[^a-zA-Z0-9._-]+", "-", cand_id).strip("-") or "candidate"
    out_dir = improvement_proposals_dir(repo_root) / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    proposal = {
        "kind": "skill-improvement-proposal",
        "target_skill_slug": slug,
        "candidate_id": candidate.get("id"),
        "similarity": match.get("similarity"),
        "approved_for_execution": False,
        "captain_approval_required": True,
        "auto_apply": False,
        "proposed_at": _utc_now(),
        "discovery_signal": candidate.get("discovery_signal"),
        "star_category": (candidate.get("provenance") or {}).get("star_category"),
        "evidence_paths": list(evidence_paths or []),
        "suggested_changes": [
            {
                "section": "Procedure",
                "action": "append-lesson",
                "rationale": (
                    f"Categorized Stars candidate {candidate.get('id')} is similar "
                    f"(score={match.get('similarity')}) to existing Skill `{slug}`. "
                    "Review notes and fold applicable steps; do not clone the starred repo."
                ),
                "source_notes": candidate.get("notes"),
            }
        ],
        "notes": (
            "Proposal only — Captain-reviewed PR required to edit "
            f".cursor/skills/{slug}/; never auto-apply"
        ),
    }
    path = out_dir / f"from-{safe_id}.json"
    path.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
