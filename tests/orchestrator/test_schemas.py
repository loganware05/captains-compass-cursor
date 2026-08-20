"""Phase A schema contract tests."""

from __future__ import annotations

import unittest

from orchestrator.model_profiles import load_catalog
from orchestrator.providers.technology_intelligence import StubTechnologyIntelligenceProvider
from orchestrator.schemas.validate import (
    ValidationError,
    all_schema_files_present,
    load_schema,
    validate,
    validate_document,
)


class SchemaPresenceTests(unittest.TestCase):
    def test_all_schema_files_present(self) -> None:
        self.assertEqual(all_schema_files_present(), [])


class CapabilitySchemaTests(unittest.TestCase):
    def test_valid_capability(self) -> None:
        doc = {
            "id": "react-engineering",
            "version": "1.0.0",
            "kind": "skill",
            "source": {
                "type": "compass-skill",
                "path": ".cursor/skills/react-engineering/SKILL.md",
            },
            "lifecycle_stage": "PROVEN_SKILL",
            "capabilities_provided": ["ui-component-implementation"],
            "security_sensitivity": "low",
        }
        validate_document(doc, "capability.schema.json")

    def test_missing_required_capability_field(self) -> None:
        doc = {"id": "x", "version": "1.0.0", "kind": "skill"}
        with self.assertRaises(ValidationError):
            validate_document(doc, "capability.schema.json")


class CandidateSchemaTests(unittest.TestCase):
    def test_candidate_not_approved_for_execution(self) -> None:
        doc = {
            "id": "external-lib",
            "version": "0.1.0",
            "kind": "candidate",
            "source": {"type": "external-candidate", "path": "github.com/example/repo"},
            "capabilities_provided": ["pdf-parsing"],
            "approved_for_execution": False,
            "lifecycle_stage": "DISCOVERED",
        }
        validate_document(doc, "candidate-capability.schema.json")

    def test_candidate_rejects_approved_for_execution_true(self) -> None:
        doc = {
            "id": "external-lib",
            "version": "0.1.0",
            "kind": "candidate",
            "source": {"type": "external-candidate", "path": "github.com/example/repo"},
            "capabilities_provided": ["pdf-parsing"],
            "approved_for_execution": True,
            "lifecycle_stage": "DISCOVERED",
        }
        with self.assertRaises(ValidationError):
            validate_document(doc, "candidate-capability.schema.json")


class TaskGraphSchemaTests(unittest.TestCase):
    def test_valid_task(self) -> None:
        doc = {
            "id": "task-impl",
            "objective": "Implement API endpoint",
            "dependencies": ["task-arch"],
            "required_capabilities": ["api-implementation"],
            "parallelizable": False,
        }
        validate_document(doc, "task.schema.json")


class AgentManifestSchemaTests(unittest.TestCase):
    def test_valid_manifest(self) -> None:
        doc = {
            "task_id": "task-impl",
            "role": "implementation-worker",
            "reference_profile": "implementation-agent",
            "model": {"class": "coding-strong", "recommendation": "inherit"},
            "skills": ["node-engineering"],
            "rationale": "Backend API task matches node Skill.",
            "scoring_breakdown": [
                {"factor": "capability overlap", "score": 0.9, "note": "api-implementation"}
            ],
        }
        validate_document(doc, "agent-manifest.schema.json")


class ModelCatalogTests(unittest.TestCase):
    def test_catalog_loads(self) -> None:
        catalog = load_catalog()
        self.assertGreaterEqual(len(catalog["profiles"]), 4)


class TechnologyIntelligenceStubTests(unittest.TestCase):
    def test_stub_returns_no_candidates(self) -> None:
        provider = StubTechnologyIntelligenceProvider()
        self.assertEqual(provider.discover_candidates("build auth", {}), [])


class ExecutionRunSchemaTests(unittest.TestCase):
    def test_valid_execution_run_stub(self) -> None:
        doc = {
            "run_id": "run-001",
            "plan_id": "m1-capability-aware-planning",
            "task_id": "task-impl",
            "outcome": "pending",
            "provenance": {"branch": "feature/35-example"},
        }
        validate_document(doc, "execution-run.schema.json")


if __name__ == "__main__":
    unittest.main()
