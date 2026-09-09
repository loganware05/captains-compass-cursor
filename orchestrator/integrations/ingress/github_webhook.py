"""Map GitHub webhook deliveries to NorthStar raw events."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.integrations.events import IdempotencyStore, redact_secrets, sha256_hex
from orchestrator.integrations.product_allowlist import require_allowed_repository

APPROVE_RE = re.compile(
    r"NORTHSTAR_APPROVE\s+plan_digest=([0-9a-fA-F]{64})\b"
)


class GitHubWebhookError(ValueError):
    """Webhook mapping rejected (scope, shape, or policy)."""

    def __init__(self, message: str, *, status: int = 400) -> None:
        super().__init__(message)
        self.status = status


def _repo_full_name(payload: dict[str, Any]) -> str:
    repo = payload.get("repository") or {}
    if isinstance(repo, dict):
        return str(repo.get("full_name") or "").strip()
    return str(repo or "").strip()


def _labels(issue: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for label in issue.get("labels") or []:
        if isinstance(label, dict):
            names.add(str(label.get("name") or "").casefold())
        else:
            names.add(str(label).casefold())
    return names


def map_github_delivery(
    *,
    event_name: str,
    delivery_id: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Map a verified GitHub delivery to a raw_event for GitHubAdapter.

    Returns None for ping (caller should ack without routine).
    Raises GitHubWebhookError for BLOCKED_SCOPE / unsupported.
    """
    if event_name == "ping":
        return None

    repository = _repo_full_name(payload)
    try:
        require_allowed_repository(repository)
    except Exception as exc:  # NorthStarRoutineError
        raise GitHubWebhookError(str(exc), status=403) from exc

    if event_name == "issues":
        action = str(payload.get("action") or "")
        issue = payload.get("issue") or {}
        labels = _labels(issue if isinstance(issue, dict) else {})
        # Also accept label added via issues labeled event.
        if action == "labeled":
            labeled = payload.get("label") or {}
            if isinstance(labeled, dict):
                labels.add(str(labeled.get("name") or "").casefold())
        intake_ok = "northstar" in labels or "northstar-intake" in labels
        if action in {"opened", "reopened", "labeled", "edited"} and intake_ok:
            return {
                "event_id": delivery_id,
                "delivery_id": delivery_id,
                "event_type": "objective",
                "repository": repository,
                "issue": str((issue or {}).get("number") or (issue or {}).get("html_url") or ""),
                "label": "northstar",
                "intake": True,
                "title": (issue or {}).get("title"),
                "body": (issue or {}).get("body"),
                "actor_id": str(
                    ((payload.get("sender") or {}) if isinstance(payload.get("sender"), dict) else {}).get(
                        "login"
                    )
                    or ""
                ),
                "product_name": "NorthStar",
                "github_event": event_name,
                "github_action": action,
            }
        raise GitHubWebhookError("issues delivery missing northstar intake label", status=400)

    if event_name == "issue_comment":
        action = str(payload.get("action") or "")
        if action not in {"created", "edited"}:
            raise GitHubWebhookError(f"unsupported issue_comment action: {action!r}", status=400)
        comment = payload.get("comment") or {}
        issue = payload.get("issue") or {}
        body = str((comment or {}).get("body") or "")
        match = APPROVE_RE.search(body)
        if not match:
            raise GitHubWebhookError(
                "issue_comment is not a NORTHSTAR_APPROVE plan_digest command",
                status=400,
            )
        return {
            "event_id": delivery_id,
            "delivery_id": delivery_id,
            "event_type": "approval",
            "repository": repository,
            "issue": str((issue or {}).get("number") or ""),
            "pull_request": None,
            "title": (issue or {}).get("title"),
            "body": body,
            "plan_digest": match.group(1).lower(),
            "approval_ref": f"github:issue-comment:{delivery_id}",
            "actor_id": str(
                ((comment or {}).get("user") or {}).get("login")
                or ((payload.get("sender") or {}) if isinstance(payload.get("sender"), dict) else {}).get(
                    "login"
                )
                or ""
            ),
            "product_name": "NorthStar",
            "github_event": event_name,
            "github_action": action,
            "intake": False,
        }

    raise GitHubWebhookError(f"unsupported GitHub event: {event_name!r}", status=400)


def remember_delivery(
    repo_root: Path,
    *,
    delivery_id: str,
    body: bytes,
) -> bool:
    """Return True if delivery is new; False if duplicate."""
    store = IdempotencyStore(Path(repo_root) / ".agent" / "northstar" / "ingress-idempotency.json")
    digest = sha256_hex(body)
    return store.remember(delivery_id, digest)


def write_ingress_receipt(
    evidence_dir: Path,
    *,
    delivery_id: str,
    event_name: str,
    raw_event: dict[str, Any] | None,
    result: dict[str, Any],
) -> Path:
    evidence_dir = Path(evidence_dir)
    path = evidence_dir / "connectors" / "ingress"
    path.mkdir(parents=True, exist_ok=True)
    out = path / f"delivery-{delivery_id}.json"
    payload = redact_secrets(
        {
            "delivery_id": delivery_id,
            "event_name": event_name,
            "raw_event": raw_event,
            "result": result,
        }
    )
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
