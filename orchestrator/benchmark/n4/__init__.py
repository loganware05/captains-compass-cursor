"""N4 cross-stack baseline vs evidence-informed benchmark."""

from orchestrator.benchmark.n4.enabled import n4_enabled, require_n4_gate
from orchestrator.benchmark.n4.service import N4ServiceError, run_n4_benchmark

__all__ = [
    "N4ServiceError",
    "n4_enabled",
    "require_n4_gate",
    "run_n4_benchmark",
]
