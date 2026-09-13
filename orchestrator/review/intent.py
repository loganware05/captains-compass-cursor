"""Normalize review intent from IMPLEMENTATION_PLAN.md or intent-pack JSON (M29).

Intent packs are evidence for Code Reviewer. They never originate Captain approval.
Linear exports are read-only flight-recorder inputs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA_VERSION = "northstar.intent_pack.v1"

_AC_LINE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(?:\[.\]\s*)?(.+)$")
_HEADING = re.compile(r"^#{1,6}\s+(.*)$")


class IntentError(ValueError):
    """Raised when an intent pack cannot be loaded or validated."""


def _extract_section_bullets(text: str, headings: tuple[str, ...]) -> list[str]:
    lines = text.splitlines()
    collecting = False
    items: list[str] = []
    for line in lines:
        heading = _HEADING.match(line)
        if heading:
            title = heading.group(1).strip().casefold()
            collecting = any(h in title for h in headings)
            continue
        if not collecting:
            continue
        if not line.strip():
            continue
        match = _AC_LINE.match(line)
        if match:
            items.append(match.group(1).strip())
        elif line.startswith("#"):
            collecting = False
    return items


def _extract_status(text: str) -> str:
    for line in text.splitlines()[:40]:
        if "status" in line.casefold() and ":" in line:
            value = line.split(":", 1)[1].strip().strip("|").strip("*").strip()
            if value:
                return value
    return ""


def intent_from_plan_markdown(
    plan_path: Path | None,
    *,
    source: str = "plan",
) -> dict[str, Any]:
    """Parse IMPLEMENTATION_PLAN.md (or INTENT_PACK.md) into a normalized pack."""
    if plan_path is None or not Path(plan_path).is_file():
        return empty_intent_pack(source=source)

    plan_path = Path(plan_path)
    text = plan_path.read_text(encoding="utf-8", errors="replace")
    pack = {
        "schema_version": SCHEMA_VERSION,
        "source": source if source in {"plan", "linear", "fixture", "json"} else "plan",
        "plan_path": str(plan_path),
        "linear_issue_id": "",
        "title": plan_path.name,
        "status": _extract_status(text),
        "acceptance_criteria": _extract_section_bullets(
            text,
            (
                "acceptance criteria",
                "acceptance",
                "definition of done",
                "desired outcomes",
            ),
        ),
        "non_goals": _extract_section_bullets(
            text,
            ("non-goals", "non goals", "deferred", "out of scope"),
        ),
        "rollback": _extract_section_bullets(
            text,
            ("rollback", "rollback plan", "rollback instructions"),
        ),
        "security_notes": _extract_section_bullets(
            text,
            ("security notes", "security / domains"),
        ),
        "domains": _extract_section_bullets(
            text,
            ("review domains",),
        ),
        "excerpt": "\n".join(text.splitlines()[:80]),
        "captain_approval": False,
    }
    return validate_intent_pack(pack)


def intent_from_json(path: Path) -> dict[str, Any]:
    """Load a normalized intent-pack JSON file."""
    path = Path(path)
    if not path.is_file():
        raise IntentError(f"intent json not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IntentError(f"invalid intent json: {exc}") from exc
    if not isinstance(data, dict):
        raise IntentError("intent json must be an object")
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("source", "json")
    data.setdefault("plan_path", "")
    data.setdefault("linear_issue_id", "")
    data.setdefault("title", path.name)
    data.setdefault("status", "")
    data.setdefault("acceptance_criteria", [])
    data.setdefault("non_goals", [])
    data.setdefault("rollback", [])
    data.setdefault("security_notes", [])
    data.setdefault("domains", [])
    data.setdefault("excerpt", "")
    data["captain_approval"] = False
    if data.get("plan_path") is None:
        data["plan_path"] = ""
    if data.get("linear_issue_id") is None:
        data["linear_issue_id"] = ""
    return validate_intent_pack(data)


def empty_intent_pack(*, source: str = "plan") -> dict[str, Any]:
    return validate_intent_pack(
        {
            "schema_version": SCHEMA_VERSION,
            "source": source if source in {"plan", "linear", "fixture", "json"} else "plan",
            "plan_path": "",
            "linear_issue_id": "",
            "title": "",
            "status": "",
            "acceptance_criteria": [],
            "non_goals": [],
            "rollback": [],
            "security_notes": [],
            "domains": [],
            "excerpt": "",
            "captain_approval": False,
        }
    )


def validate_intent_pack(pack: dict[str, Any]) -> dict[str, Any]:
    """Validate against intent-pack.schema.json; force captain_approval=false."""
    pack = dict(pack)
    pack["captain_approval"] = False
    if pack.get("schema_version") != SCHEMA_VERSION:
        pack["schema_version"] = SCHEMA_VERSION
    for key in ("plan_path", "linear_issue_id", "title", "status", "excerpt"):
        if pack.get(key) is None:
            pack[key] = ""
    for key in (
        "acceptance_criteria",
        "non_goals",
        "rollback",
        "security_notes",
        "domains",
    ):
        if not isinstance(pack.get(key), list):
            pack[key] = []
    try:
        validate_document(pack, "intent-pack.schema.json")
    except (FileNotFoundError, ValidationError) as exc:
        raise IntentError(str(exc)) from exc
    return pack


def load_intent_pack(
    *,
    plan_path: Path | None = None,
    intent_json: Path | None = None,
) -> dict[str, Any]:
    """Prefer explicit intent JSON; otherwise parse plan markdown."""
    if intent_json is not None:
        return intent_from_json(Path(intent_json))
    return intent_from_plan_markdown(plan_path)


def to_detection_intent(pack: dict[str, Any]) -> dict[str, Any]:
    """Shape used by detect/specialists (backward compatible keys)."""
    return {
        "plan_path": pack.get("plan_path") or None,
        "acceptance_criteria": list(pack.get("acceptance_criteria") or []),
        "non_goals": list(pack.get("non_goals") or []),
        "rollback": list(pack.get("rollback") or []),
        "security_notes": list(pack.get("security_notes") or []),
        "domains": list(pack.get("domains") or []),
        "excerpt": str(pack.get("excerpt") or ""),
        "source": pack.get("source"),
        "status": pack.get("status") or "",
        "linear_issue_id": pack.get("linear_issue_id") or None,
        "captain_approval": False,
        "intent_pack": pack,
    }


def write_intent_pack(path: Path, pack: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    validated = validate_intent_pack(pack)
    path.write_text(
        json.dumps(validated, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return path
