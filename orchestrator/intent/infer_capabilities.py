"""Infer required capabilities from objective text and repository context."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Objective keyword groups → required capability IDs (deterministic order preserved)
OBJECTIVE_RULES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (
        ("react", "frontend", "ui", "component", "dashboard", "typescript ui"),
        (
            "react-component-development",
            "typescript-ui",
            "component-testing",
            "keyboard-navigation-review",
        ),
    ),
    (
        ("playwright", "browser", "e2e", "screenshot"),
        (
            "playwright-execution",
            "e2e-testing",
            "ui-evidence-capture",
        ),
    ),
    (
        ("node", "api", "backend", "rest", "graphql", "express", "fastify"),
        (
            "node-api-development",
            "auth-boundary-enforcement",
            "request-validation",
            "server-integration-tests",
        ),
    ),
    (
        ("prisma", "postgres", "database", "migration", "schema"),
        (
            "prisma-schema-design",
            "database-migration",
            "postgres-query",
            "migration-rollback-planning",
        ),
    ),
    (
        ("python", "ml", "model", "training", "inference", "dataset"),
        (
            "python-service-development",
            "ml-training",
            "ml-evaluation",
            "experiment-reproducibility",
        ),
    ),
    (
        ("docker", "container", "compose", "deploy", "cloud", "preview"),
        (
            "dockerfile-authoring",
            "docker-compose-config",
            "preview-deployment",
            "deployment-rollback-planning",
        ),
    ),
    (
        ("ios", "swift", "swiftui", "xcode"),
        (
            "swiftui-development",
            "simulator-testing",
            "ios-accessibility-labels",
        ),
    ),
    (
        ("security", "auth", "secrets", "injection", "oauth", "jwt", "pci"),
        (
            "auth-review",
            "authorization-review",
            "secrets-scan",
            "injection-review",
            "supply-chain-approval-gate",
        ),
    ),
    (
        ("accessibility", "a11y", "wcag", "screen reader", "keyboard"),
        (
            "keyboard-navigation-review",
            "screen-reader-review",
            "color-contrast-check",
            "accessibility-evidence-capture",
        ),
    ),
    (
        ("plan", "implementation plan", "approval", "workstream"),
        (
            "implementation-plan-authoring",
            "approval-gate-enforcement",
            "scope-definition",
            "rollback-planning",
        ),
    ),
    (
        ("test", "validation", "lint", "coverage"),
        (
            "unit-test-execution",
            "integration-test-execution",
            "definition-of-done-validation",
            "validation-evidence-capture",
        ),
    ),
    (
        ("github", "pull request", "issue", "pr"),
        (
            "github-issue-create",
            "github-pr-create",
            "pr-description-assembly",
        ),
    ),
)

# Stack signals from discovery / PROJECT_CONTEXT → additional required capabilities
STACK_RULES: dict[str, tuple[str, ...]] = {
    "react": ("react-component-development", "typescript-ui"),
    "node": ("node-api-development",),
    "postgres": ("postgres-query", "prisma-schema-design"),
    "python": ("python-service-development",),
    "ios": ("swiftui-development",),
    "docker": ("dockerfile-authoring",),
}

# Niche objectives with no Compass Skill coverage (capability-gap fixture)
GAP_ONLY_RULES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (
        ("quantum compiler", "quantum circuit", "qubit"),
        (
            "quantum-circuit-synthesis",
            "quantum-error-correction",
        ),
    ),
)


@dataclass
class IntentResult:
    objective: str
    required_capabilities: list[str]
    domains_detected: list[str]
    security_sensitive: bool
    stacks: list[str] = field(default_factory=list)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _match_rules(haystack: str, rules: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]) -> tuple[list[str], list[str]]:
    caps: list[str] = []
    domains: list[str] = []
    for keywords, required in rules:
        if any(keyword in haystack for keyword in keywords):
            caps.extend(required)
            domains.append(keywords[0])
    return caps, domains


def infer_capabilities(objective: str, context: dict | None = None) -> IntentResult:
    """Map objective + optional context to required capability IDs."""
    context = context or {}
    haystack = _normalize(objective)
    project_text = _normalize(str(context.get("project_context", "")))
    discovery_text = _normalize(str(context.get("discovery_summary", "")))
    combined = f"{haystack} {project_text} {discovery_text}".strip()

    caps: list[str] = []
    domains: list[str] = []

    for rule_set in (OBJECTIVE_RULES, GAP_ONLY_RULES):
        matched_caps, matched_domains = _match_rules(combined, rule_set)
        caps.extend(matched_caps)
        domains.extend(matched_domains)

    stacks = [str(s).lower() for s in context.get("stacks", [])]
    for stack in stacks:
        caps.extend(STACK_RULES.get(stack, ()))

    explicit = context.get("required_capabilities")
    if isinstance(explicit, list):
        caps.extend(str(c) for c in explicit)

    if not caps:
        caps.append("implementation-plan-authoring")
        domains.append("general")

    security_sensitive = bool(
        context.get("security_sensitive")
        or any(
            token in combined
            for token in (
                "security",
                "auth",
                "secret",
                "pci",
                "hipaa",
                "injection",
                "oauth",
            )
        )
    )

    return IntentResult(
        objective=objective,
        required_capabilities=_dedupe(caps),
        domains_detected=_dedupe(domains),
        security_sensitive=security_sensitive,
        stacks=stacks,
    )
