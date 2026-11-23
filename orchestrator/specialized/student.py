"""Opt-in local specialized students (argv / HTTPS); stub remains CI default."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Protocol, runtime_checkable

from orchestrator.integrations.transport import HttpTransport, UrllibTransport

STUDENT_ARGV_ENV = "COMPASS_SPECIALIZED_STUDENT"
STUDENT_URL_ENV = "COMPASS_SPECIALIZED_STUDENT_URL"
STUDENT_TIMEOUT_ENV = "COMPASS_SPECIALIZED_STUDENT_TIMEOUT"


class SpecializedStudentError(ValueError):
    """Raised when a local student cannot produce an answer."""


@runtime_checkable
class SpecializedStudent(Protocol):
    name: str
    mode: str  # "stub" | "local"

    def answer(self, task: dict[str, Any]) -> str:
        ...


def _task_prompt(task: dict[str, Any]) -> str:
    bundle = task.get("prompt_bundle") or {}
    if isinstance(bundle, dict):
        parts = [
            str(bundle.get(k) or "").strip()
            for k in ("objective", "evidence", "constraints", "output_format")
        ]
        text = "\n\n".join(p for p in parts if p)
        if text:
            return text
    return str(task.get("prompt") or task.get("objective") or task.get("id") or "")


class GoldStubStudent:
    """Hermetic CI default: canned gold ``stub_student_answer``."""

    name = "gold-stub"
    mode = "stub"

    def answer(self, task: dict[str, Any]) -> str:
        return str(task.get("stub_student_answer") or "")


class FixtureMapStudent:
    """Hermetic test double: map task id → answer text."""

    name = "fixture-map"
    mode = "local"

    def __init__(self, answers: dict[str, str]) -> None:
        self._answers = {str(k): str(v) for k, v in answers.items()}

    def answer(self, task: dict[str, Any]) -> str:
        tid = str(task.get("id") or "")
        if tid in self._answers:
            return self._answers[tid]
        raise SpecializedStudentError(f"fixture student missing answer for {tid}")


class ArgvStudent:
    """Local argv student: JSON stdin → answer on stdout."""

    name = "argv"
    mode = "local"

    def __init__(self, command: str, *, timeout: float = 60.0) -> None:
        cmd = command.strip()
        if not cmd:
            raise SpecializedStudentError(f"{STUDENT_ARGV_ENV} is empty")
        self._command = cmd
        self._timeout = timeout

    def answer(self, task: dict[str, Any]) -> str:
        payload = {
            "task_id": str(task.get("id") or ""),
            "prompt": _task_prompt(task),
            "expected_keywords": list(task.get("expected_keywords") or []),
        }
        try:
            proc = subprocess.run(
                self._command,
                input=json.dumps(payload, separators=(",", ":")),
                capture_output=True,
                text=True,
                shell=True,
                timeout=self._timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SpecializedStudentError(f"argv student failed: {exc}") from exc
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()[:400]
            raise SpecializedStudentError(
                f"argv student exit {proc.returncode}: {err or 'no output'}"
            )
        text = (proc.stdout or "").strip()
        if not text:
            raise SpecializedStudentError("argv student returned empty answer")
        # Allow either raw text or {"answer": "..."}.
        if text.startswith("{"):
            try:
                doc = json.loads(text)
            except json.JSONDecodeError:
                return text
            if isinstance(doc, dict) and doc.get("answer") is not None:
                return str(doc.get("answer") or "")
        return text


class HttpStudent:
    """Local HTTPS student: POST JSON → {\"answer\": \"...\"}."""

    name = "http"
    mode = "local"

    def __init__(
        self,
        url: str,
        *,
        transport: HttpTransport | None = None,
        timeout: float = 60.0,
    ) -> None:
        base = url.strip()
        if not base.startswith("https://"):
            raise SpecializedStudentError(f"{STUDENT_URL_ENV} must be https://")
        self._url = base
        self._http = transport or UrllibTransport()
        self._timeout = timeout

    def answer(self, task: dict[str, Any]) -> str:
        body = json.dumps(
            {
                "task_id": str(task.get("id") or ""),
                "prompt": _task_prompt(task),
                "expected_keywords": list(task.get("expected_keywords") or []),
            },
            separators=(",", ":"),
        ).encode("utf-8")
        resp = self._http.request(
            "POST",
            self._url,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            body=body,
            timeout=self._timeout,
        )
        if resp.status >= 400:
            raise SpecializedStudentError(f"http student failed: HTTP {resp.status}")
        try:
            doc = json.loads(resp.body.decode("utf-8") or "null")
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SpecializedStudentError("http student returned invalid JSON") from exc
        if isinstance(doc, dict) and doc.get("answer") is not None:
            return str(doc.get("answer") or "")
        if isinstance(doc, str):
            return doc
        raise SpecializedStudentError("http student JSON missing answer")


def _timeout() -> float:
    raw = (os.environ.get(STUDENT_TIMEOUT_ENV) or "60").strip() or "60"
    try:
        val = float(raw)
    except ValueError as exc:
        raise SpecializedStudentError(f"{STUDENT_TIMEOUT_ENV} must be a number") from exc
    if val <= 0 or val > 600:
        raise SpecializedStudentError(f"{STUDENT_TIMEOUT_ENV} out of range")
    return val


def resolve_student(
    *,
    transport: HttpTransport | None = None,
    student: SpecializedStudent | None = None,
) -> SpecializedStudent:
    """Resolve student: explicit inject → HTTPS URL → argv → gold stub."""
    if student is not None:
        return student
    url = (os.environ.get(STUDENT_URL_ENV) or "").strip()
    if url:
        return HttpStudent(url, transport=transport, timeout=_timeout())
    argv = (os.environ.get(STUDENT_ARGV_ENV) or "").strip()
    if argv:
        return ArgvStudent(argv, timeout=_timeout())
    return GoldStubStudent()
