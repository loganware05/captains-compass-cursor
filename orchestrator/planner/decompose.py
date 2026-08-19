"""Rule-based objective decomposition into a dependency-aware task graph."""

from __future__ import annotations

from dataclasses import dataclass, field

from orchestrator.intent.infer_capabilities import IntentResult


@dataclass
class TaskNode:
    id: str
    objective: str
    acceptance_criteria: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    parallelizable: bool = False
    expected_artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objective": self.objective,
            "acceptance_criteria": list(self.acceptance_criteria),
            "dependencies": list(self.dependencies),
            "required_capabilities": list(self.required_capabilities),
            "parallelizable": self.parallelizable,
            "expected_artifacts": list(self.expected_artifacts),
        }


def _domain_flags(intent: IntentResult, objective: str) -> dict[str, bool]:
    haystack = f"{objective} {' '.join(intent.domains_detected)} {' '.join(intent.stacks)}".lower()
    stacks = set(intent.stacks)
    domains = set(intent.domains_detected)

    def has(*tokens: str) -> bool:
        return any(token in haystack or token in domains or token in stacks for token in tokens)

    return {
        "frontend": has("react", "frontend", "ui", "dashboard", "component"),
        "backend": has("node", "api", "backend", "rest", "graphql"),
        "database": has("prisma", "postgres", "database", "migration", "schema"),
        "ml": has("python", "ml", "model", "training", "inference"),
        "docker": has("docker", "container", "compose", "deploy", "cloud", "preview"),
        "ios": has("ios", "swift", "swiftui", "xcode"),
        "accessibility": has("accessibility", "a11y", "wcag", "keyboard"),
        "browser_e2e": has("playwright", "browser", "e2e", "screenshot"),
    }


def decompose(objective: str, intent: IntentResult) -> list[dict]:
    """Convert objective + inferred intent into an ordered task graph payload."""
    flags = _domain_flags(intent, objective)
    tasks: list[TaskNode] = []

    tasks.append(
        TaskNode(
            id="task-discovery",
            objective="Discover repository structure, tooling, risks, and conventions",
            acceptance_criteria=[
                "Repository discovery report covers stack, entry points, tests, and CI",
                "Relevant Skills recommended for downstream tasks",
            ],
            dependencies=[],
            required_capabilities=[
                "repo-structure-mapping",
                "tooling-identification",
                "convention-discovery",
            ],
            parallelizable=False,
            expected_artifacts=["repository-discovery-report"],
        )
    )

    tasks.append(
        TaskNode(
            id="task-architecture",
            objective="Define components, contracts, data changes, and rollback strategy",
            acceptance_criteria=[
                "Architecture brief documents boundaries, contracts, and migration/rollback",
                "Assumptions are explicit",
            ],
            dependencies=["task-discovery"],
            required_capabilities=[
                "component-boundary-design",
                "api-contract-definition",
                "migration-rollback-strategy",
            ],
            parallelizable=False,
            expected_artifacts=["architecture-brief"],
        )
    )

    implementation_ids: list[str] = []

    if flags["frontend"]:
        task = TaskNode(
            id="task-impl-frontend",
            objective="Implement frontend/UI changes for the approved scope",
            acceptance_criteria=[
                "UI matches approved plan and project conventions",
                "Client tests updated or added for changed behavior",
            ],
            dependencies=["task-architecture"],
            required_capabilities=[
                "react-component-development",
                "typescript-ui",
                "component-testing",
            ],
            parallelizable=True,
            expected_artifacts=["frontend-diff", "component-tests"],
        )
        if flags["accessibility"]:
            task.required_capabilities.extend(
                ["keyboard-navigation-review", "accessibility-evidence-capture"]
            )
        tasks.append(task)
        implementation_ids.append(task.id)

    if flags["backend"]:
        task = TaskNode(
            id="task-impl-backend",
            objective="Implement backend/API changes for the approved scope",
            acceptance_criteria=[
                "API behavior matches approved contracts",
                "Auth boundaries and validation enforced",
            ],
            dependencies=["task-architecture"],
            required_capabilities=[
                "node-api-development",
                "auth-boundary-enforcement",
                "request-validation",
            ],
            parallelizable=True,
            expected_artifacts=["backend-diff", "api-integration-tests"],
        )
        tasks.append(task)
        implementation_ids.append(task.id)

    if flags["database"]:
        task = TaskNode(
            id="task-impl-database",
            objective="Design and apply database schema/migration changes safely",
            acceptance_criteria=[
                "Prisma/schema changes migrate cleanly with rollback notes",
                "Indexes and constraints documented",
            ],
            dependencies=["task-architecture"],
            required_capabilities=[
                "prisma-schema-design",
                "database-migration",
                "migration-rollback-planning",
            ],
            parallelizable=True,
            expected_artifacts=["schema-diff", "migration-files"],
        )
        tasks.append(task)
        implementation_ids.append(task.id)

    if flags["ml"]:
        task = TaskNode(
            id="task-impl-ml",
            objective="Implement ML/data pipeline changes with reproducible experiments",
            acceptance_criteria=[
                "Training/eval steps are reproducible",
                "Dataset and model contracts documented",
            ],
            dependencies=["task-architecture"],
            required_capabilities=[
                "python-service-development",
                "ml-training",
                "ml-evaluation",
                "experiment-reproducibility",
            ],
            parallelizable=True,
            expected_artifacts=["ml-code-diff", "experiment-notes"],
        )
        tasks.append(task)
        implementation_ids.append(task.id)

    if flags["ios"]:
        task = TaskNode(
            id="task-impl-ios",
            objective="Implement iOS/SwiftUI feature changes",
            acceptance_criteria=[
                "Simulator validation completed for changed flows",
                "Accessibility labels present on new UI",
            ],
            dependencies=["task-architecture"],
            required_capabilities=[
                "swiftui-development",
                "simulator-testing",
                "ios-accessibility-labels",
            ],
            parallelizable=True,
            expected_artifacts=["ios-diff", "simulator-notes"],
        )
        tasks.append(task)
        implementation_ids.append(task.id)

    if flags["docker"]:
        task = TaskNode(
            id="task-impl-docker",
            objective="Containerize and document preview/deploy configuration",
            acceptance_criteria=[
                "Docker/Compose config builds successfully",
                "Preview deploy and rollback steps documented",
            ],
            dependencies=["task-architecture"],
            required_capabilities=[
                "dockerfile-authoring",
                "docker-compose-config",
                "preview-deployment",
            ],
            parallelizable=True,
            expected_artifacts=["docker-config", "deploy-notes"],
        )
        tasks.append(task)
        implementation_ids.append(task.id)

    if not implementation_ids:
        task = TaskNode(
            id="task-implementation",
            objective=f"Implement approved changes for: {objective}",
            acceptance_criteria=[
                "Implementation matches approved plan acceptance criteria",
                "No silent scope expansion",
            ],
            dependencies=["task-architecture"],
            required_capabilities=["feature-implementation", "convention-following"],
            parallelizable=False,
            expected_artifacts=["implementation-diff"],
        )
        tasks.append(task)
        implementation_ids.append(task.id)

    validation_deps = list(implementation_ids)
    validation_caps = [
        "unit-test-execution",
        "integration-test-execution",
        "definition-of-done-validation",
        "validation-evidence-capture",
    ]
    if flags["browser_e2e"] or flags["frontend"]:
        validation_caps.extend(["playwright-execution", "e2e-testing", "ui-evidence-capture"])

    tasks.append(
        TaskNode(
            id="task-validation",
            objective="Run applicable validation layers and capture evidence",
            acceptance_criteria=[
                "Applicable lint/tests/build pass without weakened assertions",
                "Evidence stored under .agent/evidence/",
            ],
            dependencies=validation_deps,
            required_capabilities=validation_caps,
            parallelizable=False,
            expected_artifacts=["validation-report", "evidence-paths"],
        )
    )

    doc_deps = ["task-validation"]
    if intent.security_sensitive or flags["backend"] or flags["database"]:
        tasks.append(
            TaskNode(
                id="task-security-review",
                objective="Review security-sensitive changes for auth, secrets, and injection risks",
                acceptance_criteria=[
                    "No committed secrets or critical auth regressions",
                    "Findings recorded with severity and remediation",
                ],
                dependencies=validation_deps,
                required_capabilities=[
                    "auth-review",
                    "authorization-review",
                    "secrets-scan",
                    "injection-review",
                ],
                parallelizable=True,
                expected_artifacts=["security-review-notes"],
            )
        )
        doc_deps.append("task-security-review")

    tasks.append(
        TaskNode(
            id="task-documentation",
            objective="Update project memory docs and completion records",
            acceptance_criteria=[
                "PROGRESS.md and relevant memory docs updated",
                "Plan completion record prepared when appropriate",
            ],
            dependencies=doc_deps,
            required_capabilities=[
                "project-memory-update",
                "progress-tracking",
                "completion-reporting",
            ],
            parallelizable=False,
            expected_artifacts=["documentation-diff"],
        )
    )

    return [task.to_dict() for task in tasks]
