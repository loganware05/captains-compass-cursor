#!/usr/bin/env python3
"""Write capability.yaml sidecars and reference agent profile JSON (Phase B seed)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKILLS: dict[str, dict] = {
    "accessibility-review": {
        "categories": ["quality", "accessibility", "validation"],
        "tags": ["a11y", "wcag", "keyboard", "contrast"],
        "capabilities_provided": [
            "keyboard-navigation-review",
            "screen-reader-review",
            "semantic-markup-review",
            "color-contrast-check",
            "accessibility-evidence-capture",
        ],
        "compatible_stacks": ["web", "react", "ios", "any"],
        "security_sensitivity": "low",
        "agent_affinity": ["accessibility-reviewer", "test-engineer"],
    },
    "autonomy-budget": {
        "categories": ["process", "governance", "autonomy"],
        "tags": ["budget", "limits", "iterations"],
        "capabilities_provided": [
            "budget-ledger-management",
            "iteration-tracking",
            "budget-limit-enforcement",
            "budget-stop-reporting",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["implementation-agent", "documentation-agent"],
    },
    "candidate-promotion": {
        "categories": ["process", "security", "orchestration"],
        "tags": ["candidates", "promotion", "technology-intelligence"],
        "capabilities_provided": [
            "candidate-lifecycle-advancement",
            "skill-sidecar-draft-proposal",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "high",
        "agent_affinity": ["security-reviewer", "architecture-agent"],
    },
    "skill-lifecycle": {
        "categories": ["process", "learning", "orchestration", "promotion"],
        "tags": ["skill-lifecycle", "promotion", "proficiency", "proven"],
        "capabilities_provided": [
            "skill-lifecycle-promotion",
            "skill-proven-graduation",
            "skill-proficiency-training",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": [
            "knowledge-steward",
            "candidate-promotion",
            "experience-skill-training",
            "documentation-agent",
        ],
    },
    "external-knowledge-ingest": {
        "categories": ["process", "knowledge", "orchestration", "research"],
        "tags": ["notion", "notebooklm", "external-knowledge", "ingest"],
        "capabilities_provided": [
            "external-notion-ingest",
            "external-notebooklm-ingest",
            "external-knowledge-query",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": [
            "knowledge-steward",
            "notion-integration",
            "documentation-agent",
        ],
    },
    "compass-evaluator": {
        "categories": ["process", "evaluation", "orchestration"],
        "tags": ["evaluator", "experiments", "comparison"],
        "capabilities_provided": [
            "bounded-experiment-recording",
            "alternative-comparison",
            "evaluation-evidence-capture",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": ["compass-evaluator", "adversarial-reviewer"],
    },
    "code-structure-cleanup": {
        "categories": ["refactoring", "quality"],
        "tags": ["cleanup", "refactor", "services"],
        "capabilities_provided": [
            "duplication-identification",
            "service-layer-extraction",
            "behavior-preserving-refactor",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["implementation-agent", "architecture-agent"],
    },
    "dependency-supply-chain": {
        "categories": ["security", "dependencies", "supply-chain"],
        "tags": ["npm", "pypi", "lockfile", "audit"],
        "capabilities_provided": [
            "dependency-risk-assessment",
            "lockfile-discipline",
            "package-provenance-review",
            "supply-chain-approval-gate",
        ],
        "compatible_stacks": ["node", "python", "rust", "swift", "any"],
        "security_sensitivity": "high",
        "agent_affinity": ["security-reviewer", "architecture-agent"],
    },
    "docker-cloud": {
        "categories": ["infrastructure", "deployment", "containers"],
        "tags": ["docker", "compose", "cloud", "preview"],
        "capabilities_provided": [
            "dockerfile-authoring",
            "docker-compose-config",
            "preview-deployment",
            "deployment-rollback-planning",
        ],
        "compatible_stacks": ["node", "python", "web", "any"],
        "security_sensitivity": "high",
        "agent_affinity": ["implementation-agent", "architecture-agent"],
    },
    "execution-telemetry": {
        "categories": ["process", "orchestration", "telemetry"],
        "tags": ["telemetry", "experience", "execution-run"],
        "capabilities_provided": [
            "execution-run-recording",
            "experience-store-population",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": ["documentation-agent", "test-engineer"],
    },
    "experience-skill-training": {
        "categories": ["process", "learning", "orchestration"],
        "tags": ["experience", "training", "skills"],
        "capabilities_provided": [
            "experience-to-skill-draft",
            "control-repo-skill-training",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": ["documentation-agent", "architecture-agent"],
    },
    "experience-routing": {
        "categories": ["process", "learning", "orchestration"],
        "tags": ["experience", "routing", "proposals"],
        "capabilities_provided": [
            "experience-routing-proposal",
            "matcher-weight-suggestion",
            "agent-proficiency-recording",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": ["documentation-agent", "architecture-agent", "compass-evaluator"],
    },
    "github-integration": {
        "categories": ["integration", "delivery", "git"],
        "tags": ["github", "gh-cli", "issues", "pull-requests"],
        "capabilities_provided": [
            "github-issue-create",
            "github-pr-create",
            "github-ci-status-inspection",
            "github-auth-fallback",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": ["documentation-agent", "implementation-agent"],
    },
    "harness-gc": {
        "categories": ["process", "governance", "maintenance"],
        "tags": ["compass", "rules", "skills", "drift"],
        "capabilities_provided": [
            "harness-drift-detection",
            "rules-inventory",
            "skills-inventory",
            "harness-cleanup-reporting",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["documentation-agent", "repository-scout"],
    },
    "implementation-planning": {
        "categories": ["process", "planning", "governance"],
        "tags": ["planning", "approval", "scope"],
        "capabilities_provided": [
            "implementation-plan-authoring",
            "approval-gate-enforcement",
            "scope-definition",
            "workstream-definition",
            "rollback-planning",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["architecture-agent", "repository-scout"],
    },
    "ios-engineering": {
        "categories": ["mobile", "implementation", "frontend"],
        "tags": ["swift", "swiftui", "xcode", "ios"],
        "capabilities_provided": [
            "swiftui-development",
            "xcode-project-management",
            "ios-accessibility-labels",
            "simulator-testing",
        ],
        "compatible_stacks": ["ios", "swift"],
        "security_sensitivity": "medium",
        "agent_affinity": ["implementation-agent", "test-engineer"],
    },
    "linear-integration": {
        "categories": ["integration", "project-management"],
        "tags": ["linear", "mcp", "issues"],
        "capabilities_provided": [
            "linear-issue-read",
            "linear-task-create",
            "linear-status-update",
            "linear-pr-linking",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": ["documentation-agent", "architecture-agent"],
    },
    "node-engineering": {
        "categories": ["backend", "implementation", "api"],
        "tags": ["node", "express", "api", "auth"],
        "capabilities_provided": [
            "node-api-development",
            "auth-boundary-enforcement",
            "request-validation",
            "server-integration-tests",
        ],
        "compatible_stacks": ["node"],
        "security_sensitivity": "high",
        "agent_affinity": ["implementation-agent", "test-engineer"],
    },
    "notion-integration": {
        "categories": ["integration", "documentation", "planning"],
        "tags": ["notion", "mcp", "requirements"],
        "capabilities_provided": [
            "notion-requirements-read",
            "notion-research-read",
            "notion-release-summary-write",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "medium",
        "agent_affinity": ["documentation-agent", "repository-scout"],
    },
    "playwright-browser-validation": {
        "categories": ["testing", "validation", "ui"],
        "tags": ["playwright", "e2e", "browser", "screenshots"],
        "capabilities_provided": [
            "playwright-execution",
            "e2e-testing",
            "browser-screenshots",
            "ui-evidence-capture",
        ],
        "compatible_stacks": ["web", "react", "node"],
        "security_sensitivity": "medium",
        "agent_affinity": ["test-engineer", "accessibility-reviewer"],
    },
    "postgres-prisma": {
        "categories": ["database", "backend", "data"],
        "tags": ["postgres", "prisma", "migrations"],
        "capabilities_provided": [
            "prisma-schema-design",
            "database-migration",
            "postgres-query",
            "migration-rollback-planning",
        ],
        "compatible_stacks": ["node", "postgres"],
        "security_sensitivity": "high",
        "agent_affinity": ["implementation-agent", "architecture-agent"],
    },
    "pull-request-preparation": {
        "categories": ["process", "delivery", "quality"],
        "tags": ["pr", "evidence", "completion"],
        "capabilities_provided": [
            "definition-of-done-check",
            "pr-description-assembly",
            "evidence-packaging",
            "completion-reporting",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["documentation-agent", "test-engineer"],
    },
    "python-ml": {
        "categories": ["backend", "ml", "data"],
        "tags": ["python", "ml", "training", "inference"],
        "capabilities_provided": [
            "python-service-development",
            "data-pipeline",
            "ml-training",
            "ml-evaluation",
            "experiment-reproducibility",
        ],
        "compatible_stacks": ["python"],
        "security_sensitivity": "medium",
        "agent_affinity": ["implementation-agent", "test-engineer"],
    },
    "react-engineering": {
        "categories": ["frontend", "implementation", "ui"],
        "tags": ["react", "typescript", "vite", "nextjs"],
        "capabilities_provided": [
            "react-component-development",
            "typescript-ui",
            "client-state-management",
            "component-testing",
        ],
        "compatible_stacks": ["react", "web", "node"],
        "security_sensitivity": "medium",
        "agent_affinity": ["implementation-agent", "test-engineer"],
    },
    "repository-discovery": {
        "categories": ["discovery", "onboarding", "architecture"],
        "tags": ["onboarding", "architecture", "tooling"],
        "capabilities_provided": [
            "repo-structure-mapping",
            "tooling-identification",
            "convention-discovery",
            "skill-recommendation",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["repository-scout", "architecture-agent"],
    },
    "review-fix-loop": {
        "categories": ["process", "quality", "delivery"],
        "tags": ["pr", "review", "feedback"],
        "capabilities_provided": [
            "review-feedback-triage",
            "iterative-fix-loop",
            "review-resolution-summary",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["implementation-agent", "adversarial-reviewer"],
    },
    "security-review": {
        "categories": ["security", "quality", "validation"],
        "tags": ["security", "auth", "secrets", "injection"],
        "capabilities_provided": [
            "auth-review",
            "authorization-review",
            "secrets-scan",
            "injection-review",
            "dependency-security-review",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "high",
        "agent_affinity": ["security-reviewer", "adversarial-reviewer"],
    },
    "source-code-context": {
        "categories": ["development", "integration", "research"],
        "tags": ["opensrc", "packages", "api", "source"],
        "capabilities_provided": [
            "package-source-fetch",
            "dependency-source-search",
            "api-discovery",
        ],
        "compatible_stacks": ["node", "python", "rust", "any"],
        "security_sensitivity": "medium",
        "agent_affinity": ["implementation-agent", "repository-scout"],
    },
    "testing-validation": {
        "categories": ["testing", "quality", "validation"],
        "tags": ["testing", "validation", "lint", "evidence"],
        "capabilities_provided": [
            "lint-execution",
            "unit-test-execution",
            "integration-test-execution",
            "validation-evidence-capture",
            "definition-of-done-validation",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["test-engineer", "implementation-agent"],
    },
    "worktree-orchestration": {
        "categories": ["process", "git", "orchestration"],
        "tags": ["git", "worktree", "branch", "rollback"],
        "capabilities_provided": [
            "feature-branch-create",
            "worktree-create",
            "rollback-checkpoint",
            "parallel-workstream-provisioning",
        ],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": ["implementation-agent", "architecture-agent"],
    },
}

PROFILES: dict[str, dict] = {
    "accessibility-reviewer": {
        "categories": ["quality", "accessibility", "review"],
        "tags": ["a11y", "review"],
        "capabilities_provided": [
            "keyboard-navigation-review",
            "screen-reader-label-review",
            "color-contrast-check",
            "accessibility-evidence-capture",
        ],
        "agent_affinity": ["accessibility-reviewer"],
    },
    "adversarial-reviewer": {
        "categories": ["quality", "review", "validation"],
        "tags": ["adversarial", "review"],
        "capabilities_provided": [
            "adversarial-code-review",
            "scope-drift-detection",
            "edge-case-identification",
            "test-quality-review",
        ],
        "agent_affinity": ["adversarial-reviewer"],
    },
    "architecture-agent": {
        "categories": ["architecture", "planning", "design"],
        "tags": ["architecture", "contracts"],
        "capabilities_provided": [
            "component-boundary-design",
            "api-contract-definition",
            "security-boundary-definition",
            "migration-rollback-strategy",
        ],
        "agent_affinity": ["architecture-agent"],
    },
    "documentation-agent": {
        "categories": ["documentation", "process", "memory"],
        "tags": ["docs", "memory"],
        "capabilities_provided": [
            "project-memory-update",
            "progress-tracking",
            "changelog-update",
            "plan-status-update",
        ],
        "agent_affinity": ["documentation-agent"],
    },
    "implementation-agent": {
        "categories": ["implementation", "development"],
        "tags": ["implementation"],
        "capabilities_provided": [
            "feature-implementation",
            "scoped-code-change",
            "convention-following",
            "local-validation",
        ],
        "agent_affinity": ["implementation-agent"],
    },
    "repository-scout": {
        "categories": ["discovery", "onboarding", "architecture"],
        "tags": ["discovery", "scout"],
        "capabilities_provided": [
            "read-only-discovery",
            "repo-structure-mapping",
            "tooling-identification",
            "skill-recommendation",
        ],
        "agent_affinity": ["repository-scout"],
    },
    "security-reviewer": {
        "categories": ["security", "quality", "review"],
        "tags": ["security", "review"],
        "capabilities_provided": [
            "auth-review",
            "authorization-review",
            "secrets-exposure-scan",
            "injection-review",
        ],
        "agent_affinity": ["security-reviewer"],
    },
    "test-engineer": {
        "categories": ["testing", "quality", "validation"],
        "tags": ["testing"],
        "capabilities_provided": [
            "unit-test-authoring",
            "integration-test-authoring",
            "e2e-test-authoring",
            "test-evidence-capture",
        ],
        "agent_affinity": ["test-engineer"],
    },
}


def _yaml_list(items: list[str], indent: int = 0) -> str:
    pad = " " * indent
    return "\n".join(f"{pad}- {item}" for item in items)


def render_sidecar(slug: str, meta: dict) -> str:
    lines = [
        f"id: {slug}",
        'version: "1.0.0"',
        "kind: skill",
        "source:",
        "  type: compass-skill",
        f"  path: .cursor/skills/{slug}/SKILL.md",
        "provenance:",
        "  authored_by: compass",
        "  inferred: false",
        "  confidence: 0.9",
        "lifecycle_stage: PROVEN_SKILL",
        f"categories: [{', '.join(meta['categories'])}]",
        "tags:",
        _yaml_list(meta["tags"], 2),
        "capabilities_provided:",
        _yaml_list(meta["capabilities_provided"], 2),
        "compatible_stacks:",
        _yaml_list(meta["compatible_stacks"], 2),
        f"security_sensitivity: {meta['security_sensitivity']}",
        "agent_affinity:",
        _yaml_list(meta["agent_affinity"], 2),
        "maturity: proven",
        "confidence: 0.9",
        "",
    ]
    return "\n".join(lines)


def render_profile(profile_id: str, meta: dict) -> dict:
    return {
        "id": profile_id,
        "version": "1.0.0",
        "kind": "agent-profile",
        "source": {
            "type": "compass-agent",
            "path": f".cursor/agents/{profile_id}.md",
        },
        "provenance": {
            "authored_by": "compass",
            "inferred": False,
            "confidence": 0.9,
        },
        "lifecycle_stage": "PROVEN_SKILL",
        "categories": meta["categories"],
        "tags": meta["tags"],
        "capabilities_provided": meta["capabilities_provided"],
        "compatible_stacks": ["any"],
        "security_sensitivity": "low",
        "agent_affinity": meta["agent_affinity"],
        "maturity": "proven",
        "confidence": 0.9,
    }


def main() -> None:
    for slug, meta in SKILLS.items():
        path = ROOT / ".cursor" / "skills" / slug / "capability.yaml"
        path.write_text(render_sidecar(slug, meta), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")

    profiles_dir = ROOT / "orchestrator" / "reference-profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    for profile_id, meta in PROFILES.items():
        path = profiles_dir / f"{profile_id}.json"
        path.write_text(
            json.dumps(render_profile(profile_id, meta), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
