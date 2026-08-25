"""Compile capability registry from Skills and reference agent profiles."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from orchestrator.registry.infer import infer_capability
from orchestrator.registry.loader import RegistryLoadError, load_skill_entry
from orchestrator.registry.yaml_simple import load_simple_yaml
from orchestrator.schemas.validate import ValidationError, validate_document

SKILL_SLUGS = (
    "repository-discovery",
    "implementation-planning",
    "worktree-orchestration",
    "testing-validation",
    "security-review",
    "accessibility-review",
    "pull-request-preparation",
    "github-integration",
    "react-engineering",
    "playwright-browser-validation",
    "node-engineering",
    "postgres-prisma",
    "docker-cloud",
    "linear-integration",
    "notion-integration",
    "python-ml",
    "ios-engineering",
    "source-code-context",
    "code-structure-cleanup",
    "review-fix-loop",
    "autonomy-budget",
    "harness-gc",
    "dependency-supply-chain",
    "capability-planning",
    "execution-telemetry",
    "candidate-promotion",
    "experience-skill-training",
    "compass-evaluator",
    "experience-routing",
    "persistent-role-promotion",
    "bounded-autonomy",
    "knowledge-steward",
    "technology-intelligence-live",
    "procedure-playbooks",
    "skill-lifecycle",
    "external-knowledge-ingest",
    "embedding-providers",
    "package-registry-ti",
)

AGENT_PROFILES = (
    "repository-scout",
    "architecture-agent",
    "implementation-agent",
    "test-engineer",
    "security-reviewer",
    "accessibility-reviewer",
    "adversarial-reviewer",
    "documentation-agent",
    "compass-evaluator",
    "knowledge-steward",
)


@dataclass
class CompileResult:
    registry: dict
    warnings: list[str] = field(default_factory=list)


class RegistryCompileError(ValueError):
    """Raised when registry compilation fails."""


def _reject_path_traversal(path: str) -> None:
    if ".." in path.split("/"):
        raise RegistryCompileError(f"path traversal rejected in source.path: {path}")


def _normalize_skill_capability(
    slug: str,
    frontmatter: dict[str, str],
    sidecar: dict | None,
    warnings: list[str],
) -> dict:
    name = frontmatter["name"]
    description = frontmatter.get("description", "")
    if sidecar is None:
        warnings.append(f"{slug}: missing capability.yaml; using inferred metadata")
        capability = infer_capability(slug, name, description)
    else:
        capability = dict(sidecar)
        capability.setdefault("provenance", {})
        if isinstance(capability["provenance"], dict):
            capability["provenance"].setdefault("inferred", False)
    if capability.get("id") != name:
        raise RegistryCompileError(
            f"{slug}: capability.id {capability.get('id')!r} must match SKILL name {name!r}"
        )
    source = capability.setdefault("source", {})
    if not isinstance(source, dict):
        raise RegistryCompileError(f"{slug}: source must be an object")
    source.setdefault("type", "compass-skill")
    source.setdefault("path", f".cursor/skills/{slug}/SKILL.md")
    _reject_path_traversal(str(source["path"]))
    validate_document(capability, "capability.schema.json")
    return capability


def load_reference_profile(repo_root: Path, profile_id: str) -> dict:
    path = repo_root / "orchestrator" / "reference-profiles" / f"{profile_id}.json"
    if not path.is_file():
        raise RegistryCompileError(f"missing reference profile: {path}")
    with path.open(encoding="utf-8") as handle:
        profile = json.load(handle)
    validate_document(profile, "capability.schema.json")
    if profile.get("id") != profile_id:
        raise RegistryCompileError(
            f"profile id {profile.get('id')!r} must match filename {profile_id!r}"
        )
    return profile


def compile_registry(repo_root: Path) -> CompileResult:
    warnings: list[str] = []
    skills: list[dict] = []
    seen_ids: set[str] = set()

    for slug in SKILL_SLUGS:
        frontmatter, sidecar, _ = load_skill_entry(repo_root, slug)
        capability = _normalize_skill_capability(slug, frontmatter, sidecar, warnings)
        cap_id = capability["id"]
        if cap_id in seen_ids:
            raise RegistryCompileError(f"duplicate capability id: {cap_id}")
        seen_ids.add(cap_id)
        skills.append(capability)

    profiles: list[dict] = []
    seen_profile_ids: set[str] = set()
    for profile_id in AGENT_PROFILES:
        profile = load_reference_profile(repo_root, profile_id)
        pid = profile["id"]
        if pid in seen_profile_ids:
            raise RegistryCompileError(f"duplicate reference profile id: {pid}")
        seen_profile_ids.add(pid)
        profiles.append(profile)

    registry = {
        "version": "1.0.0",
        "compiled_from": "orchestrator.registry.compiler",
        "skills": skills,
        "reference_profiles": profiles,
    }
    return CompileResult(registry=registry, warnings=warnings)


def write_registry(repo_root: Path, output_path: Path | None = None) -> CompileResult:
    result = compile_registry(repo_root)
    out = output_path or (repo_root / ".agent" / "capabilities" / "compiled" / "registry.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(result.registry, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return result


def main() -> int:
    import sys

    repo_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    try:
        result = write_registry(repo_root)
    except (RegistryCompileError, RegistryLoadError, ValidationError) as exc:
        print(f"registry compile failed: {exc}", file=sys.stderr)
        return 1
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    print(f"registry written: {repo_root / '.agent/capabilities/compiled/registry.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
