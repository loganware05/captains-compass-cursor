"""ExecutionAdapter protocol + fixture T3 adapter."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

from orchestrator.integrations.events import utc_now


@runtime_checkable
class ExecutionAdapter(Protocol):
    """NorthStar-owned execution surface (fixture or live T3)."""

    name: str

    def capabilities(self) -> dict[str, Any]:
        ...

    def start(self, task: dict[str, Any]) -> dict[str, Any]:
        ...

    def status(self, execution_id: str) -> dict[str, Any]:
        ...

    def collect(self, execution_id: str) -> dict[str, Any]:
        ...

    def cancel(self, execution_id: str) -> dict[str, Any]:
        ...


class FixtureT3ExecutionAdapter:
    """Hermetic T3 adapter for CI — no live MCP calls."""

    name = "t3-fixture"

    def __init__(self) -> None:
        self._runs: dict[str, dict[str, Any]] = {}

    def capabilities(self) -> dict[str, Any]:
        return {
            "adapter": self.name,
            "mode": "fixture",
            "providers": ["cursor", "fixture"],
            "operations": ["capabilities", "start", "status", "collect", "cancel"],
            "live": False,
            "plan_gate_required": True,
            "approved_for_execution": False,
            "authority_mutation": False,
        }

    def start(self, task: dict[str, Any]) -> dict[str, Any]:
        execution_id = str(task.get("execution_id") or f"t3-exec-{uuid4().hex[:12]}")
        thread_ref = f"fixture-thread-{execution_id[-8:]}"
        now = utc_now()
        doc = {
            "execution_id": execution_id,
            "thread_ref": thread_ref,
            "status": "started",
            "provider": str(task.get("provider") or "fixture"),
            "model": str(task.get("model") or "fixture-model"),
            "objective": str(task.get("objective") or ""),
            "plan_id": str(task.get("plan_id") or ""),
            "created_at": now,
            "updated_at": now,
            "artifacts": [],
            "collected_summary": "",
        }
        self._runs[execution_id] = doc
        return dict(doc)

    def status(self, execution_id: str) -> dict[str, Any]:
        run = self._runs.get(execution_id)
        if not run:
            raise KeyError(execution_id)
        # Fixture advances started → running on first status poll.
        if run["status"] == "started":
            run["status"] = "running"
            run["updated_at"] = utc_now()
        return dict(run)

    def collect(self, execution_id: str) -> dict[str, Any]:
        run = self._runs.get(execution_id)
        if not run:
            raise KeyError(execution_id)
        run["status"] = "completed"
        run["updated_at"] = utc_now()
        summary = (
            f"Fixture collect for {execution_id}: objective="
            f"{run.get('objective')!r} (no live T3 thread)."
        )
        run["collected_summary"] = summary
        run["artifacts"] = [f"fixture://{execution_id}/summary.txt"]
        return dict(run)

    def cancel(self, execution_id: str) -> dict[str, Any]:
        run = self._runs.get(execution_id)
        if not run:
            raise KeyError(execution_id)
        run["status"] = "cancelled"
        run["updated_at"] = utc_now()
        run["collected_summary"] = run.get("collected_summary") or "cancelled (fixture)"
        return dict(run)


class LiveT3ExecutionAdapter:
    """Live skeleton — fail closed unless a transport injectable is provided later."""

    name = "t3-live"

    def capabilities(self) -> dict[str, Any]:
        return {
            "adapter": self.name,
            "mode": "live",
            "providers": [],
            "operations": ["capabilities"],
            "live": True,
            "available": False,
            "reason": (
                "Live T3 MCP transport not injected in v1.79.0 skeleton; "
                "use fixture mode or inject a future transport."
            ),
            "plan_gate_required": True,
            "approved_for_execution": False,
            "authority_mutation": False,
        }

    def start(self, task: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError(
            "live T3 start unavailable — fixture mode only unless transport injected"
        )

    def status(self, execution_id: str) -> dict[str, Any]:
        raise RuntimeError("live T3 status unavailable")

    def collect(self, execution_id: str) -> dict[str, Any]:
        raise RuntimeError("live T3 collect unavailable")

    def cancel(self, execution_id: str) -> dict[str, Any]:
        raise RuntimeError("live T3 cancel unavailable")
