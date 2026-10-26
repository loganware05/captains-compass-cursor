"""Load and shuffle N4 task pack fixtures."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

CONTROL_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FIXTURE_DIR = CONTROL_ROOT / "tests" / "fixtures" / "n4" / "tasks"

REQUIRED_TASK_KEYS = (
    "task_id",
    "stack_id",
    "difficulty",
    "objective",
    "held_out",
    "hermetic",
)


class TaskPackError(ValueError):
    """Invalid or incomplete N4 task pack."""


def load_task_pack(fixture_dir: Path | None = None) -> list[dict[str, Any]]:
    root = Path(fixture_dir or DEFAULT_FIXTURE_DIR)
    if not root.is_dir():
        raise TaskPackError(f"task fixture dir missing: {root}")
    tasks: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TaskPackError(f"invalid task fixture {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise TaskPackError(f"task fixture must be object: {path}")
        for key in REQUIRED_TASK_KEYS:
            if key not in data:
                raise TaskPackError(f"{path.name} missing {key}")
        if data["difficulty"] not in {"easy", "medium", "hard"}:
            raise TaskPackError(f"{path.name} bad difficulty")
        tasks.append(data)
    if len(tasks) < 12:
        raise TaskPackError(f"need >=12 tasks, found {len(tasks)}")
    return tasks


def seeded_order(tasks: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    ordered = list(tasks)
    rng = random.Random(int(seed))
    rng.shuffle(ordered)
    return ordered


def stack_summary() -> list[dict[str, Any]]:
    """Static stack table aligned with STACKS.md (hermetic defaults)."""
    return [
        {
            "stack_id": "traphouse",
            "role": "order-status",
            "substituted": False,
            "pin_ref": "main",
            "pin_sha": "f7c4719ba016feae17308c5d39a929187671aa72",
            "notes": "TrapHouseKitchen",
        },
        {
            "stack_id": "sandbox",
            "role": "verdant-substitute",
            "substituted": True,
            "pin_ref": "main",
            "pin_sha": "5a1d32e0a8d49ffebcd62c598c12201e3f19985e",
            "notes": "Substitutes Verdant.sys (no NorthStar install at pin time)",
        },
        {
            "stack_id": "bitcoin",
            "role": "idempotent-recovery",
            "substituted": False,
            "pin_ref": "cursor/m35-c2-northstar-install-5182",
            "pin_sha": "468c9483a1731afc80bec0e1bcfc45bfe09e5b2e",
            "notes": "Pinned M35 NorthStar install branch; not default feature branch",
        },
    ]
