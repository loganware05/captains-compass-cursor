"""Non-canonical CSV export for behavior evaluations (M46)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from orchestrator.behavior.ledger import list_records
from orchestrator.behavior.signals import BEHAVIOR_SIGNALS


def export_csv(repo_root: Path, dest: Path) -> Path:
    records = list_records(repo_root)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "evaluation_id",
        "execution_id",
        "task_id",
        "plan_id",
        "agent",
        "model",
        "outcome",
        "provider",
        "schema_version",
        "created_at",
        "abstain",
        *BEHAVIOR_SIGNALS,
    ]
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row: dict[str, Any] = {
                "evaluation_id": record.get("evaluation_id", ""),
                "execution_id": record.get("execution_id", ""),
                "task_id": record.get("task_id", ""),
                "plan_id": record.get("plan_id", ""),
                "agent": record.get("agent", ""),
                "model": record.get("model", ""),
                "outcome": record.get("outcome", ""),
                "provider": (record.get("evaluator") or {}).get("provider", ""),
                "schema_version": record.get("schema_version", ""),
                "created_at": record.get("created_at", ""),
                "abstain": record.get("abstain", False),
            }
            signals = dict(record.get("signals") or {})
            for name in BEHAVIOR_SIGNALS:
                row[name] = signals.get(name, "")
            writer.writerow(row)
    return dest
