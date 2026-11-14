"""Parse wave definitions from IMPLEMENTATION_PLAN.md."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from orchestrator.integrations.t3.plan_gate import parse_plan_document
from orchestrator.plan_waves.errors import PlanWavesError

_WAVE_HEADING = re.compile(
    r"^#{2,3}\s+Wave\s+([A-Za-z0-9]+)\s*[—\-–:]\s*(.+?)\s*$",
    re.MULTILINE,
)
_OPTIONAL = re.compile(r"\boptional\b", re.IGNORECASE)
_YAML_WAVES = re.compile(
    r"```ya?ml\s*\nwaves:\s*\n((?:[ \t]+.+\n)+)```",
    re.IGNORECASE,
)


def revision_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def require_approved_plan(text: str, plan_id: str) -> tuple[str, str]:
    active_id, status = parse_plan_document(text)
    if not active_id:
        raise PlanWavesError("could not parse Plan ID from IMPLEMENTATION_PLAN.md")
    if active_id != plan_id:
        raise PlanWavesError(
            f"plan_id {plan_id!r} does not match active plan {active_id!r}"
        )
    upper = (status or "").upper()
    if "APPROVED" not in upper and "IN PROGRESS" not in upper:
        raise PlanWavesError(
            f"plan {plan_id!r} status {status!r} is not APPROVED — refuse "
            "(never forge APPROVED)"
        )
    return active_id, status


def _wave_from_yaml_block(text: str) -> list[dict[str, Any]] | None:
    match = _YAML_WAVES.search(text or "")
    if not match:
        return None
    waves: list[dict[str, Any]] = []
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        # - id: A  title: Foo  optional: true
        wid = ""
        title = ""
        optional = False
        body = line.lstrip("-").strip()
        for part in re.split(r"\s{2,}|\s+(?=\w+:)", body):
            if ":" not in part:
                continue
            key, val = part.split(":", 1)
            key = key.strip().lower()
            val = val.strip().strip("\"'")
            if key in ("id", "wave_id", "wave"):
                wid = val
            elif key == "title":
                title = val
            elif key == "optional":
                optional = val.lower() in ("1", "true", "yes", "on")
        if not wid:
            continue
        waves.append(
            {
                "wave_id": wid if wid.lower().startswith("wave") else f"wave-{wid}",
                "title": title or f"Wave {wid}",
                "optional": optional,
            }
        )
    return waves or None


def parse_waves_from_plan(text: str) -> list[dict[str, Any]]:
    yaml_waves = _wave_from_yaml_block(text)
    if yaml_waves:
        return yaml_waves
    found: list[dict[str, Any]] = []
    for match in _WAVE_HEADING.finditer(text or ""):
        label = match.group(1).strip()
        title = match.group(2).strip()
        optional = bool(_OPTIONAL.search(title))
        found.append(
            {
                "wave_id": f"wave-{label.lower()}",
                "title": f"Wave {label} — {title}",
                "optional": optional,
            }
        )
    if not found:
        raise PlanWavesError(
            "no Wave headings (##/### Wave X — …) or yaml waves: block found"
        )
    return found
