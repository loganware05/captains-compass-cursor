"""Open UI CLI service — emit surfaces and gated actions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestrator.openui.approval import ApprovalError, apply_plan_decision
from orchestrator.openui.enabled import openui_enabled, require_openui_gate
from orchestrator.openui.emitters import (
    emit_closeout_ledger,
    emit_control_tower,
    emit_hermetic_scorecard,
    emit_plan_approval,
)
from orchestrator.openui.lang import OpenUILangError, validate_openui_lang, wrap_fence


class OpenUIServiceError(ValueError):
    """Operator-facing Open UI errors."""


SURFACES = frozenset({"plan", "tower", "scorecard", "closeout"})


def emit_surface(
    repo_root: Path,
    surface: str,
    *,
    report: dict[str, Any] | None = None,
    fence: bool = True,
) -> str:
    require_openui_gate()
    name = surface.strip().lower()
    if name not in SURFACES:
        raise OpenUIServiceError(
            f"unknown surface: {surface} (expected one of {sorted(SURFACES)})"
        )
    try:
        if name == "plan":
            lang = emit_plan_approval(repo_root)
        elif name == "tower":
            lang = emit_control_tower(repo_root)
        elif name == "scorecard":
            lang = emit_hermetic_scorecard(repo_root, report=report)
        else:
            lang = emit_closeout_ledger(repo_root, report=report)
        validate_openui_lang(lang)
    except OpenUILangError as exc:
        raise OpenUIServiceError(
            f"Open UI fail-closed: invalid OpenUI Lang ({exc}); "
            "use markdown/CLI workflow"
        ) from exc
    return wrap_fence(lang) if fence else lang


def persist_emit(
    repo_root: Path,
    surface: str,
    *,
    lang: str,
) -> Path:
    out_dir = Path(repo_root) / ".agent" / "ui"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{surface}.openui"
    # store raw lang without fence for renderer
    body = lang
    if body.strip().startswith("```"):
        parts = body.strip().split("\n", 1)
        body = parts[1] if len(parts) > 1 else ""
        if body.rstrip().endswith("```"):
            body = body.rstrip()[:-3].rstrip() + "\n"
    path.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
    return path


def run_ui_command(
    repo_root: Path,
    command: str,
    *,
    surface: str | None = None,
    decision: str | None = None,
    feedback: str = "",
    fence: bool = True,
    persist: bool = True,
) -> dict[str, Any]:
    cmd = command.strip().lower()
    if cmd == "emit":
        if not surface:
            raise OpenUIServiceError("emit requires --surface")
        lang = emit_surface(repo_root, surface, fence=fence)
        result: dict[str, Any] = {
            "status": "emitted",
            "surface": surface,
            "openui_enabled": openui_enabled(),
            "lang": lang,
            "auto_approved": False,
            "authority_mutation": False,
        }
        if persist:
            raw = emit_surface(repo_root, surface, fence=False)
            path = persist_emit(repo_root, surface, lang=raw)
            result["path"] = str(path)
        return result

    if cmd == "validate":
        path = Path(repo_root) / ".agent" / "ui" / f"{surface or 'plan'}.openui"
        if not path.is_file():
            raise OpenUIServiceError(f"missing {path}")
        try:
            meta = validate_openui_lang(path.read_text(encoding="utf-8"))
        except OpenUILangError as exc:
            raise OpenUIServiceError(f"fail-closed: {exc}") from exc
        return {"status": "valid", "path": str(path), "meta": meta}

    if cmd in {"approve", "reject"}:
        require_openui_gate()
        try:
            outcome = apply_plan_decision(
                repo_root,
                decision=decision or cmd,
                feedback=feedback,
            )
        except ApprovalError as exc:
            raise OpenUIServiceError(str(exc)) from exc
        return {"status": "decision_applied", **outcome}

    raise OpenUIServiceError(f"unknown ui command: {command}")


def dump_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)
