"""Stdlib NorthStar ingress HTTP server (GitHub webhooks)."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from orchestrator.branding import display_name
from orchestrator.integrations.ingress.github_webhook import (
    GitHubWebhookError,
    map_github_delivery,
    remember_delivery,
    write_ingress_receipt,
)
from orchestrator.integrations.ingress.signatures import verify_github_signature
from orchestrator.integrations.product_allowlist import (
    DEFAULT_PRODUCT_REPOSITORY,
    require_allowed_repository,
)

MAX_BODY_BYTES = 1 * 1024 * 1024


class IngressHTTPServer(ThreadingHTTPServer):
    """ThreadingHTTPServer with NorthStar ingress config on the instance."""

    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: type[BaseHTTPRequestHandler],
        *,
        repo_root: Path,
        mode: str = "fixtures",
        product_repository: str = DEFAULT_PRODUCT_REPOSITORY,
        webhook_secret: str = "",
        routine_runner: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        self.repo_root = Path(repo_root)
        self.mode = mode
        self.product_repository = product_repository
        self.webhook_secret = webhook_secret
        self.routine_runner = routine_runner


class NorthStarIngressHandler(BaseHTTPRequestHandler):
    server: IngressHTTPServer  # type: ignore[assignment]

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep default quiet-ish; never log secrets.
        sys_stderr_write = getattr(self, "_quiet", False)
        if sys_stderr_write:
            return
        super().log_message(fmt, *args)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/healthz":
            self._send_json(
                200,
                {
                    "ok": True,
                    "product": display_name(),
                    "mode": self.server.mode,
                },
            )
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/webhooks/github":
            self._send_json(404, {"ok": False, "error": "not_found"})
            return

        if self.server.mode != "live":
            self._send_json(
                503,
                {"ok": False, "error": "fixture_mode", "message": "webhooks disabled in fixtures mode"},
            )
            return

        length_hdr = self.headers.get("Content-Length") or "0"
        try:
            length = int(length_hdr)
        except ValueError:
            self._send_json(400, {"ok": False, "error": "invalid_content_length"})
            return
        if length < 0 or length > MAX_BODY_BYTES:
            self._send_json(413, {"ok": False, "error": "payload_too_large"})
            return

        body = self.rfile.read(length)
        secret = self.server.webhook_secret or os.environ.get(
            "NORTHSTAR_GITHUB_WEBHOOK_SECRET", ""
        )
        signature = self.headers.get("X-Hub-Signature-256")
        if not verify_github_signature(body=body, signature_header=signature, secret=secret):
            self._send_json(401, {"ok": False, "error": "invalid_signature"})
            return

        delivery_id = self.headers.get("X-GitHub-Delivery") or ""
        event_name = self.headers.get("X-GitHub-Event") or ""
        if not delivery_id or not event_name:
            self._send_json(400, {"ok": False, "error": "missing_delivery_headers"})
            return

        if event_name == "ping":
            self._send_json(200, {"ok": True, "pong": True})
            return

        if not remember_delivery(self.server.repo_root, delivery_id=delivery_id, body=body):
            self._send_json(200, {"ok": True, "duplicate": True, "delivery_id": delivery_id})
            return

        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        if not isinstance(payload, dict):
            self._send_json(400, {"ok": False, "error": "invalid_json_object"})
            return

        try:
            require_allowed_repository(self.server.product_repository)
            raw_event = map_github_delivery(
                event_name=event_name,
                delivery_id=delivery_id,
                payload=payload,
            )
        except GitHubWebhookError as exc:
            self._send_json(exc.status, {"ok": False, "error": str(exc)})
            return
        except Exception as exc:  # allowlist / other
            msg = str(exc)
            status = 403 if "BLOCKED_SCOPE" in msg else 400
            self._send_json(status, {"ok": False, "error": msg})
            return

        if raw_event is None:
            self._send_json(200, {"ok": True, "pong": True})
            return

        runner = self.server.routine_runner
        if runner is None:
            from orchestrator.integrations.routine import run_northstar_routine

            runner = run_northstar_routine

        try:
            if raw_event.get("event_type") == "approval":
                result = runner(
                    self.server.repo_root,
                    raw_event=raw_event,
                    provider="github",
                    mode="live",
                    product_repository=self.server.product_repository,
                    approve=False,
                    live_approval=raw_event,
                )
            else:
                result = runner(
                    self.server.repo_root,
                    raw_event=raw_event,
                    provider="github",
                    mode="live",
                    product_repository=self.server.product_repository,
                    approve=False,
                )
        except Exception as exc:
            result = {"ok": False, "error": str(exc)}
            evidence = self.server.repo_root / ".agent" / "evidence" / f"ingress-{delivery_id}"
            evidence.mkdir(parents=True, exist_ok=True)
            write_ingress_receipt(
                evidence,
                delivery_id=delivery_id,
                event_name=event_name,
                raw_event=raw_event,
                result=result,
            )
            self._send_json(500, {"ok": False, "error": "routine_failed", "message": str(exc)})
            return

        evidence_dir = Path(result.get("evidence_dir") or (
            self.server.repo_root / ".agent" / "evidence" / str(result.get("run_id") or delivery_id)
        ))
        write_ingress_receipt(
            evidence_dir,
            delivery_id=delivery_id,
            event_name=event_name,
            raw_event=raw_event,
            result=result,
        )
        self._send_json(
            200,
            {
                "ok": bool(result.get("ok", True)),
                "delivery_id": delivery_id,
                "run_id": result.get("run_id"),
                "state": result.get("state"),
                "duplicate": bool(result.get("duplicate")),
            },
        )


def serve_ingress(
    *,
    repo_root: Path,
    host: str = "127.0.0.1",
    port: int = 8787,
    mode: str = "fixtures",
    product_repository: str = DEFAULT_PRODUCT_REPOSITORY,
    webhook_secret: str | None = None,
    routine_runner: Callable[..., dict[str, Any]] | None = None,
) -> IngressHTTPServer:
    """Create (but do not serve forever) an ingress server instance."""
    secret = webhook_secret if webhook_secret is not None else os.environ.get(
        "NORTHSTAR_GITHUB_WEBHOOK_SECRET", ""
    )
    if mode == "live" and not secret:
        raise RuntimeError(
            "BLOCKED_CONNECTION: NORTHSTAR_GITHUB_WEBHOOK_SECRET required for live ingress"
        )
    if mode == "live":
        require_allowed_repository(product_repository)
    server = IngressHTTPServer(
        (host, port),
        NorthStarIngressHandler,
        repo_root=repo_root,
        mode=mode,
        product_repository=product_repository,
        webhook_secret=secret or "",
        routine_runner=routine_runner,
    )
    return server


def run_ingress_forever(**kwargs: Any) -> None:
    server = serve_ingress(**kwargs)
    try:
        server.serve_forever()
    finally:
        server.server_close()
