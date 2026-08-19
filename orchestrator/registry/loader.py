"""Load Skill frontmatter and optional capability sidecars."""

from __future__ import annotations

import re
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


class RegistryLoadError(ValueError):
    """Raised when Skill metadata cannot be loaded safely."""


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise RegistryLoadError(f"missing YAML frontmatter: {skill_md}")
    block = match.group(1)
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if "name" not in fields:
        raise RegistryLoadError(f"missing name in frontmatter: {skill_md}")
    return fields


def load_yaml_sidecar(path: Path) -> dict:
    from orchestrator.registry.yaml_simple import load_simple_yaml

    text = path.read_text(encoding="utf-8")
    return load_simple_yaml(text, str(path))


def resolve_skill_dir(repo_root: Path, slug: str) -> Path:
    return repo_root / ".cursor" / "skills" / slug


def load_skill_entry(repo_root: Path, slug: str) -> tuple[dict[str, str], dict | None, Path]:
    skill_dir = resolve_skill_dir(repo_root, slug)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise RegistryLoadError(f"missing SKILL.md for slug {slug}")
    frontmatter = parse_frontmatter(skill_md)
    sidecar_path = skill_dir / "capability.yaml"
    sidecar = load_yaml_sidecar(sidecar_path) if sidecar_path.is_file() else None
    return frontmatter, sidecar, skill_md
