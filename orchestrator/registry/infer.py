"""Infer minimal capability metadata from Skill frontmatter."""

from __future__ import annotations

KEYWORD_CAPABILITIES: dict[str, list[str]] = {
    "react": ["react-component-development", "typescript-ui"],
    "node": ["node-api-development"],
    "python": ["python-service-development"],
    "prisma": ["prisma-schema-design", "database-migration"],
    "postgres": ["postgres-query"],
    "docker": ["dockerfile-authoring"],
    "playwright": ["playwright-execution", "e2e-testing"],
    "security": ["auth-review", "secrets-scan"],
    "accessibility": ["keyboard-navigation-review"],
    "github": ["github-issue-create", "github-pr-create"],
    "linear": ["linear-issue-read"],
    "notion": ["notion-requirements-read"],
    "ios": ["swiftui-development"],
    "test": ["unit-test-execution", "validation-evidence-capture"],
    "plan": ["implementation-plan-authoring"],
    "budget": ["budget-ledger-management"],
    "worktree": ["feature-branch-create", "worktree-create"],
    "ml": ["ml-training", "ml-evaluation"],
}


def infer_capability(slug: str, name: str, description: str) -> dict:
    haystack = f"{slug} {name} {description}".lower()
    caps: list[str] = []
    for keyword, provided in KEYWORD_CAPABILITIES.items():
        if keyword in haystack:
            caps.extend(provided)
    if not caps:
        caps = [f"{slug.replace('-', '_')}-procedure"]
    # dedupe preserving order
    seen: set[str] = set()
    unique = []
    for cap in caps:
        if cap not in seen:
            seen.add(cap)
            unique.append(cap)
    return {
        "id": name,
        "version": "1.0.0",
        "kind": "skill",
        "source": {
            "type": "compass-skill",
            "path": f".cursor/skills/{slug}/SKILL.md",
        },
        "provenance": {
            "authored_by": "compass-inferred",
            "inferred": True,
            "confidence": 0.3,
        },
        "lifecycle_stage": "AVAILABLE_SKILL",
        "categories": ["inferred"],
        "tags": [slug],
        "capabilities_provided": unique,
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["implementation-agent"],
        "maturity": "inferred",
        "confidence": 0.3,
    }
