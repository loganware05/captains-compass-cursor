"""Reconcile NorthStar run state across providers; GitHub wins on conflict."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.integrations.events import redact_secrets, utc_now


def reconcile_run(
    run: dict[str, Any],
    *,
    github: Any,
    linear: Any | None = None,
    slack: Any | None = None,
    cursor: Any | None = None,
) -> dict[str, Any]:
    """Reconcile connectors. Missing Linear/Slack/Cursor follow fallback policy."""
    results: dict[str, Any] = {"at": utc_now(), "run_id": run.get("run_id"), "providers": {}}

    gh = github.reconcile(run)
    results["providers"]["github"] = gh
    if not github.connected:
        results["fatal"] = "missing_github"
        results["ok"] = False
        return results

    if linear is not None:
        results["providers"]["linear"] = linear.reconcile(run)
    else:
        results["providers"]["linear"] = {"ok": False, "fallback": "github"}

    if slack is not None:
        if slack.connected:
            results["providers"]["slack"] = slack.reconcile(run)
        else:
            results["providers"]["slack"] = {
                "ok": False,
                "suppressed": True,
                "reason": "slack_unavailable",
            }
    else:
        results["providers"]["slack"] = {"ok": False, "suppressed": True}

    if cursor is not None:
        results["providers"]["cursor"] = cursor.reconcile(run)
    else:
        results["providers"]["cursor"] = {
            "ok": False,
            "reason": "cursor_unavailable",
            "work_packet_ready": bool(run.get("work_packet")),
        }

    # Conflict policy: GitHub + approved plan are authoritative.
    results["authority"] = {
        "engineering": "github",
        "plan_digest": run.get("plan_digest"),
        "plan_approved": bool(run.get("plan_approved")),
        "state": run.get("state"),
    }
    results["ok"] = True
    return redact_secrets(results)


def persist_run(run: dict[str, Any], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(redact_secrets(run), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def load_run(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
