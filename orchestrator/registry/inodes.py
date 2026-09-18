"""Content-addressed Skill inodes (M40 Task 3).

Each Skill gets an immutable inode keyed by the SHA-256 of its content
(``SKILL.md`` + ``capability.yaml``), stored at ``.cursor/skills/inodes/``.
Skill identity becomes content, not slug: editing a Skill produces a new
inode, and Experience/proficiency reputation pinned to an inode never
transfers to new content silently — carry-over requires explicit Captain
approval (consistent with ADR-025 / ADR-050).

The index is deterministic: identical Skill contents ⇒ byte-identical inodes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from orchestrator.registry.loader import load_yaml_sidecar
from orchestrator.schemas.validate import validate_document

SKILL_INODE_STORE_VERSION = "1.0.0"
SKILL_INODES_DIR = Path(".cursor") / "skills" / "inodes"
INDEX_FILENAME = "index.json"
HASHED_FILES = ("SKILL.md", "capability.yaml")


class SkillInodeError(ValueError):
    """Raised when skill inode operations cannot complete safely."""


def skill_content_hash(skill_dir: Path) -> str:
    """SHA-256 over the Skill's hashed files (name + bytes, sorted by name)."""
    skill_dir = Path(skill_dir)
    digest = hashlib.sha256()
    hashed: list[str] = []
    for name in sorted(HASHED_FILES):
        path = skill_dir / name
        if not path.is_file():
            continue
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
        hashed.append(name)
    if not hashed:
        raise SkillInodeError(f"no hashable skill files under {skill_dir}")
    return digest.hexdigest()


def skill_inode_id_for(content_hash: str) -> str:
    return f"skl-{content_hash[:16]}"


def _lifecycle_stage(skill_dir: Path) -> str:
    sidecar = Path(skill_dir) / "capability.yaml"
    if not sidecar.is_file():
        return ""
    try:
        data = load_yaml_sidecar(sidecar)
    except Exception:
        return ""
    return str(data.get("lifecycle_stage") or "")


def iter_skill_dirs(skills_root: Path) -> list[Path]:
    """Skill directories under .cursor/skills/, excluding the inodes store."""
    skills_root = Path(skills_root)
    return sorted(
        (
            path
            for path in skills_root.iterdir()
            if path.is_dir() and path.name != "inodes" and (path / "SKILL.md").is_file()
        ),
        key=lambda path: path.name,
    )


def build_skill_inode(
    skill_dir: Path,
    *,
    previous: dict[str, Any] | None = None,
    captain_approved: bool = False,
) -> dict[str, Any]:
    """Build one skill inode. Carry-over rules:

    - No prior index entry → fresh inode, ``captain_approved: false``.
    - Unchanged content → prior carry-over state preserved (idempotent rebuild);
      a passed ``captain_approved`` retroactively approves a pending carry-over.
    - Changed content → new inode; reputation carry-over requires
      ``captain_approved=True`` (Captain gate), default false.
    """
    skill_dir = Path(skill_dir)
    slug = skill_dir.name
    chash = skill_content_hash(skill_dir)
    sources = [name for name in sorted(HASHED_FILES) if (skill_dir / name).is_file()]

    carry_over_from: str | None = None
    approved = False
    if previous is not None:
        if previous.get("content_hash") == chash:
            carry_over_from = previous.get("reputation", {}).get("carry_over_from")
            approved = bool(previous.get("reputation", {}).get("captain_approved"))
            if captain_approved and carry_over_from:
                approved = True
        else:
            carry_over_from = previous.get("skill_inode_id")
            approved = bool(captain_approved)

    inode = {
        "skill_inode_id": skill_inode_id_for(chash),
        "store_version": SKILL_INODE_STORE_VERSION,
        "slug": slug,
        "content_hash": chash,
        "sources": sources,
        "lifecycle_stage": _lifecycle_stage(skill_dir),
        "reputation": {
            "carry_over_from": carry_over_from,
            "captain_approved": approved,
        },
    }
    validate_document(inode, "skill-inode.schema.json")
    return inode


def _load_previous_index(inodes_dir: Path) -> dict[str, Any]:
    path = Path(inodes_dir) / INDEX_FILENAME
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def build_skill_inode_index(
    repo_root: Path,
    *,
    captain_approved: bool = False,
    captain_approved_slugs: list[str] | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Build/refresh the skill inode index for all Skills. Deterministic.

    ``captain_approved`` approves carry-over for every changed Skill;
    ``captain_approved_slugs`` scopes approval to named Skills only.
    """
    repo_root = Path(repo_root)
    skills_root = repo_root / ".cursor" / "skills"
    inodes_dir = Path(output_dir) if output_dir else repo_root / SKILL_INODES_DIR
    inodes_dir.mkdir(parents=True, exist_ok=True)

    previous_index = _load_previous_index(inodes_dir)
    previous_by_slug = previous_index.get("skills") or {}

    slugs: dict[str, Any] = {}
    written: list[str] = []
    for skill_dir in iter_skill_dirs(skills_root):
        previous = previous_by_slug.get(skill_dir.name)
        approved = bool(captain_approved) or bool(
            captain_approved_slugs and skill_dir.name in captain_approved_slugs
        )
        inode = build_skill_inode(
            skill_dir,
            previous=previous,
            captain_approved=approved,
        )
        out_path = inodes_dir / f"{inode['content_hash']}.json"
        if not out_path.is_file() or json.loads(out_path.read_text(encoding="utf-8")) != inode:
            with out_path.open("w", encoding="utf-8") as handle:
                json.dump(inode, handle, indent=2, sort_keys=True)
                handle.write("\n")
        written.append(str(out_path))
        slugs[inode["slug"]] = {
            "skill_inode_id": inode["skill_inode_id"],
            "content_hash": inode["content_hash"],
            "lifecycle_stage": inode["lifecycle_stage"],
            "reputation": inode["reputation"],
        }

    index = {
        "store_version": SKILL_INODE_STORE_VERSION,
        "skill_count": len(slugs),
        "skills": slugs,
    }
    index_path = inodes_dir / INDEX_FILENAME
    with index_path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {"index": index, "written": written, "inodes_dir": str(inodes_dir)}


def verify_skill_inodes(repo_root: Path, *, inodes_dir: Path | None = None) -> list[dict[str, str]]:
    """Return Skills whose committed inode no longer matches current content."""
    repo_root = Path(repo_root)
    skills_root = repo_root / ".cursor" / "skills"
    base = Path(inodes_dir) if inodes_dir else repo_root / SKILL_INODES_DIR
    index = _load_previous_index(base)
    problems: list[dict[str, str]] = []
    if not index:
        return [{"slug": "*", "reason": "skill inode index missing — run scripts/build-skill-inodes.sh"}]
    indexed = index.get("skills") or {}
    for skill_dir in iter_skill_dirs(skills_root):
        slug = skill_dir.name
        entry = indexed.get(slug)
        if not entry:
            problems.append({"slug": slug, "reason": "missing inode"})
            continue
        current = skill_content_hash(skill_dir)
        if current != entry.get("content_hash"):
            problems.append({"slug": slug, "reason": "content changed — rerun scripts/build-skill-inodes.sh"})
    for slug in sorted(set(indexed) - {path.name for path in iter_skill_dirs(skills_root)}):
        problems.append({"slug": slug, "reason": "indexed but skill directory removed"})
    return problems
