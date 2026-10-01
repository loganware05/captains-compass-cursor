"""M48 Instruction Registry + Prompt Composer (proposal-only).

Import submodules directly (e.g. ``orchestrator.behavior.instructions.service``).
"""

from orchestrator.behavior.enabled import (
    instructions_enabled,
    require_instructions_enabled,
)

__all__ = [
    "instructions_enabled",
    "require_instructions_enabled",
]
