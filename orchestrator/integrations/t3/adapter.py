"""ExecutionAdapter protocol + fixture / live T3 adapters."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

from orchestrator.integrations.events import utc_now
from orchestrator.integrations.t3.client import T3ClientError, T3LiveClient
from orchestrator.integrations.transport import HttpTransport


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


def _map_remote_status(raw: Any) -> str:
    text = str(raw or "").strip().lower()
    if text in {"started", "queued", "pending", "created"}:
        return "started"
    if text in {"running", "working", "in_progress", "active"}:
        return "running"
    if text in {"completed", "done", "settled", "idle", "success"}:
        return "completed"
    if text in {"cancelled", "canceled", "interrupted", "stopped"}:
        return "cancelled"
    if text in {"failed", "error"}:
        return "failed"
    return "running"


def _summarize_messages(payload: dict[str, Any]) -> str:
    messages = payload.get("messages")
    if isinstance(messages, list):
        parts: list[str] = []
        for item in messages[-8:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or item.get("type") or "item")
            text = str(item.get("text") or item.get("content") or "").strip()
            if text:
                parts.append(f"{role}: {text[:500]}")
        if parts:
            return "\n".join(parts)
    summary = payload.get("summary") or payload.get("collected_summary")
    if summary:
        return str(summary)
    return f"Live T3 thread {payload.get('threadId') or payload.get('id') or ''} collected."


class LiveT3ExecutionAdapter:
    """Live T3 adapter — injectable HttpTransport; fail-closed without client."""

    name = "t3-live"

    def __init__(
        self,
        *,
        transport: HttpTransport | None = None,
        api_base: str | None = None,
        token: str | None = None,
        client: T3LiveClient | None = None,
    ) -> None:
        self._transport = transport
        self._api_base = api_base
        self._token = token
        self._client = client
        self._runs: dict[str, dict[str, Any]] = {}

    def _get_client(self) -> T3LiveClient:
        if self._client is not None:
            return self._client
        try:
            self._client = T3LiveClient(
                transport=self._transport,
                api_base=self._api_base,
                token=self._token,
            )
        except T3ClientError as exc:
            raise RuntimeError(str(exc)) from exc
        return self._client

    def capabilities(self) -> dict[str, Any]:
        base = {
            "adapter": self.name,
            "mode": "live",
            "live": True,
            "plan_gate_required": True,
            "approved_for_execution": False,
            "authority_mutation": False,
            "operations": ["capabilities", "start", "status", "collect", "cancel"],
        }
        try:
            client = self._get_client()
            remote = client.capabilities()
        except (RuntimeError, T3ClientError, PermissionError) as exc:
            return {
                **base,
                "providers": [],
                "available": False,
                "reason": str(exc),
            }
        providers = remote.get("providers")
        if not isinstance(providers, list):
            providers = ["t3"]
        return {
            **base,
            "providers": [str(p) for p in providers],
            "available": True,
            "remote": {
                k: remote[k]
                for k in ("models", "runtimeModes", "version")
                if k in remote
            },
        }

    def start(self, task: dict[str, Any]) -> dict[str, Any]:
        execution_id = str(task.get("execution_id") or f"t3-exec-{uuid4().hex[:12]}")
        objective = str(task.get("objective") or "").strip()
        plan_id = str(task.get("plan_id") or "").strip()
        provider = str(task.get("provider") or "t3")
        model = str(task.get("model") or "")
        title = str(task.get("title") or f"northstar:{plan_id or execution_id}")[:200]
        try:
            remote = self._get_client().start_thread(
                title=title,
                message=objective,
                client_request_id=execution_id,
                provider=provider,
                model=model,
            )
        except T3ClientError as exc:
            raise RuntimeError(str(exc)) from exc

        thread_ref = str(
            remote.get("threadId")
            or remote.get("thread_id")
            or remote.get("id")
            or ""
        )
        if not thread_ref:
            raise RuntimeError("live T3 start missing threadId")
        now = utc_now()
        doc = {
            "execution_id": execution_id,
            "thread_ref": thread_ref,
            "status": _map_remote_status(remote.get("status") or "started"),
            "provider": provider,
            "model": model or str(remote.get("model") or ""),
            "objective": objective,
            "plan_id": plan_id,
            "created_at": now,
            "updated_at": now,
            "artifacts": [],
            "collected_summary": "",
            "link": str(remote.get("link") or ""),
        }
        self._runs[execution_id] = doc
        # Also index by thread for status/collect when service passes thread_ref.
        self._runs[thread_ref] = doc
        return dict(doc)

    def status(self, execution_id: str) -> dict[str, Any]:
        run = self._runs.get(execution_id)
        thread_ref = str((run or {}).get("thread_ref") or execution_id)
        try:
            remote = self._get_client().read_thread(thread_ref, view="activity")
        except T3ClientError as exc:
            raise RuntimeError(str(exc)) from exc
        status = _map_remote_status(
            remote.get("status") or remote.get("runStatus") or remote.get("state")
        )
        now = utc_now()
        if run is None:
            run = {
                "execution_id": execution_id,
                "thread_ref": thread_ref,
                "status": status,
                "provider": "t3",
                "model": "",
                "objective": "",
                "plan_id": "",
                "created_at": now,
                "updated_at": now,
                "artifacts": [],
                "collected_summary": "",
            }
        else:
            run = dict(run)
            run["status"] = status
            run["updated_at"] = now
        self._runs[execution_id] = run
        self._runs[thread_ref] = run
        return dict(run)

    def collect(self, execution_id: str) -> dict[str, Any]:
        run = self._runs.get(execution_id)
        thread_ref = str((run or {}).get("thread_ref") or execution_id)
        try:
            remote = self._get_client().read_thread(thread_ref, view="messages")
        except T3ClientError as exc:
            raise RuntimeError(str(exc)) from exc
        now = utc_now()
        summary = _summarize_messages(remote)
        artifacts = [f"t3://{thread_ref}/messages"]
        link = str(remote.get("link") or (run or {}).get("link") or "")
        if link:
            artifacts.append(link)
        status = _map_remote_status(
            remote.get("status") or remote.get("runStatus") or "completed"
        )
        if status not in {"completed", "cancelled", "failed"}:
            status = "completed"
        doc = {
            "execution_id": str((run or {}).get("execution_id") or execution_id),
            "thread_ref": thread_ref,
            "status": status,
            "provider": str((run or {}).get("provider") or "t3"),
            "model": str((run or {}).get("model") or ""),
            "objective": str((run or {}).get("objective") or ""),
            "plan_id": str((run or {}).get("plan_id") or ""),
            "created_at": str((run or {}).get("created_at") or now),
            "updated_at": now,
            "artifacts": artifacts,
            "collected_summary": summary,
            "link": link,
        }
        self._runs[execution_id] = doc
        self._runs[thread_ref] = doc
        return dict(doc)

    def cancel(self, execution_id: str) -> dict[str, Any]:
        run = self._runs.get(execution_id)
        thread_ref = str((run or {}).get("thread_ref") or execution_id)
        try:
            remote = self._get_client().interrupt_thread(
                thread_ref, reason="northstar cancel"
            )
        except T3ClientError as exc:
            raise RuntimeError(str(exc)) from exc
        now = utc_now()
        doc = dict(run) if run else {
            "execution_id": execution_id,
            "thread_ref": thread_ref,
            "provider": "t3",
            "model": "",
            "objective": "",
            "plan_id": "",
            "created_at": now,
            "artifacts": [],
        }
        doc["status"] = "cancelled"
        doc["updated_at"] = now
        doc["collected_summary"] = str(
            remote.get("reason") or doc.get("collected_summary") or "cancelled (live)"
        )
        self._runs[execution_id] = doc
        self._runs[thread_ref] = doc
        return dict(doc)
