"""Read-only persistent oversight — compose brain + Overseer without authority."""

from orchestrator.oversight.service import OversightServiceError, run_oversight

__all__ = ["OversightServiceError", "run_oversight"]
