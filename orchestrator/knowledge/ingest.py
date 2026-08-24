"""Ingest learning artifacts into the knowledge store (explicit CLI only)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.knowledge.index import write_index
from orchestrator.knowledge.store import (
    KnowledgeStoreError,
    ensure_store_layout,
    ingest_log_dir,
    reject_secret_path,
    write_knowledge_item,
)
from orchestrator.schemas.validate import validate_document

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
_ADR_HEADING = re.compile(r"^##\s+(ADR-\d+:\s*.+)$", re.MULTILINE)

STORE_ROOTS: dict[str, tuple[str, ...]] = {
    "experience": (".agent/experience", "tests/fixtures/experience"),
    "evaluations": (".agent/evaluations",),
    "routing": (".agent/routing/proposals", ".agent/routing/applied"),
    "runs": (".agent/runs",),
    "decisions": ("DECISIONS.md",),
}


class IngestError(ValueError):
    """Raised when knowledge ingestion fails."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _base_item(
    *,
    item_id: str,
    kind: str,
    title: str,
    summary: str,
    source_type: str,
    source_id: str,
    source_path: str,
    keywords: list[str] | None = None,
    confidence: float = 0.7,
    provenance: dict[str, Any] | None = None,
    performance_metrics: dict[str, Any] | None = None,
) -> dict:
    item = {
        "item_id": item_id,
        "kind": kind,
        "title": title,
        "summary": summary,
        "keywords": list(keywords or []),
        "confidence": confidence,
        "source_artifact": {
            "type": source_type,
            "id": source_id,
            "path": source_path,
        },
        "provenance": dict(provenance or {}),
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    if performance_metrics:
        item["performance_metrics"] = performance_metrics
    return item


def _metrics_from_execution_run(doc: dict) -> dict[str, Any]:
    return {
        "outcome": str(doc.get("outcome") or "unknown"),
        "retries": int(doc.get("retries") or 0),
        "skills": list(doc.get("skills") or []),
        "agents": list(doc.get("agents") or []),
        "models": list(doc.get("models") or []),
        "plan_id": str(doc.get("plan_id") or ""),
        "task_id": str(doc.get("task_id") or ""),
        "experience_id": str(doc.get("experience_id") or ""),
    }


def _metrics_from_experience(doc: dict) -> dict[str, Any]:
    return {
        "outcome": str(doc.get("outcome") or "unknown"),
        "skills": list(doc.get("skills_used") or []),
        "capabilities_exercised": list(doc.get("capabilities_exercised") or []),
        "plan_id": str(doc.get("plan_id") or ""),
        "run_id": str(doc.get("run_id") or ""),
    }


def item_from_experience(doc: dict, source_path: str) -> dict:
    eid = str(doc["experience_id"])
    outcome = str(doc.get("outcome") or "unknown")
    skills = list(doc.get("skills_used") or [])
    lessons = list(doc.get("lessons") or [])
    summary = (
        f"Experience {eid} outcome={outcome}. "
        f"Skills: {', '.join(skills) or 'none'}. "
        f"Lessons: {'; '.join(lessons) if lessons else 'none recorded'}."
    )
    metrics = _metrics_from_experience(doc)
    return _base_item(
        item_id=f"know-exp-{eid}",
        kind="performance",
        title=f"Experience {eid} ({outcome})",
        summary=summary,
        source_type="experience",
        source_id=eid,
        source_path=source_path,
        keywords=skills + [outcome, "experience", "performance"],
        confidence=0.85 if outcome == "success" else 0.5,
        provenance=dict(doc.get("provenance") or {}),
        performance_metrics=metrics,
    )


def item_from_evaluation(doc: dict, source_path: str) -> dict:
    eid = str(doc["evaluation_id"])
    recommendation = str(doc.get("recommendation") or "")
    winner = str(doc.get("winner_alternative_id") or "")
    summary = (
        f"Evaluation {eid}: {doc.get('objective', '')}. "
        f"Recommendation: {recommendation}. Winner: {winner or 'none'}."
    )
    return _base_item(
        item_id=f"know-eval-{eid}",
        kind="decision",
        title=f"Evaluation {eid}",
        summary=summary[:2000],
        source_type="evaluation",
        source_id=eid,
        source_path=source_path,
        keywords=["evaluation", "decision", winner] if winner else ["evaluation", "decision"],
        confidence=0.8,
        provenance=dict(doc.get("provenance") or {}),
    )


def item_from_routing(doc: dict, source_path: str) -> dict:
    pid = str(doc.get("proposal_id") or doc.get("applied_id") or uuid4().hex[:12])
    kind_label = str(doc.get("kind") or "routing-artifact")
    summary = str(doc.get("notes") or f"Routing artifact {pid} ({kind_label}).")
    return _base_item(
        item_id=f"know-route-{pid}",
        kind="artifact",
        title=f"Routing {pid}",
        summary=summary[:2000],
        source_type=kind_label,
        source_id=pid,
        source_path=source_path,
        keywords=["routing", "artifact"],
        confidence=0.6,
    )


def item_from_execution_run(doc: dict, source_path: str) -> dict:
    rid = str(doc["run_id"])
    outcome = str(doc.get("outcome") or "unknown")
    metrics = _metrics_from_execution_run(doc)
    skills = list(doc.get("skills") or [])
    summary = (
        f"ExecutionRun {rid} plan={doc.get('plan_id', 'n/a')} task={doc.get('task_id', 'n/a')} "
        f"outcome={outcome} retries={metrics['retries']}. "
        f"Skills: {', '.join(skills) or 'none'}."
    )
    return _base_item(
        item_id=f"know-run-{rid}",
        kind="performance",
        title=f"Execution run {rid} ({outcome})",
        summary=summary[:2000],
        source_type="execution-run",
        source_id=rid,
        source_path=source_path,
        keywords=["execution-run", outcome, "performance"] + skills,
        confidence=0.75 if outcome == "success" else 0.55,
        performance_metrics=metrics,
    )


def items_from_decisions_md(text: str, source_path: str) -> list[dict]:
    """Auto-ingest ADR headings from DECISIONS.md."""
    items: list[dict] = []
    matches = list(_ADR_HEADING.finditer(text))
    for idx, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        # First paragraph or first 500 chars as summary
        summary = body.split("\n\n")[0].strip() if body else heading
        summary = summary[:2000] if summary else heading
        adr_id = heading.split(":")[0].strip().lower().replace(" ", "-")
        item_id = f"know-{adr_id}"
        items.append(
            _base_item(
                item_id=item_id,
                kind="decision",
                title=heading,
                summary=summary,
                source_type="decisions-md",
                source_id=adr_id,
                source_path=source_path,
                keywords=["adr", "decision", adr_id.replace("adr-", "")],
                confidence=0.9,
                provenance={"auto_ingest": "adr-heading"},
            )
        )
    return items


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise IngestError(f"expected object JSON: {path}")
    return doc


def ingest_path(repo_root: Path, path: Path) -> list[dict]:
    """Ingest a single file; returns written knowledge items."""
    repo_root = Path(repo_root)
    path = Path(path).resolve()
    reject_secret_path(str(path))
    rel = str(path.relative_to(repo_root)) if path.is_relative_to(repo_root) else str(path)

    written: list[dict] = []
    if path.suffix == ".json":
        doc = _load_json(path)
        if "experience_id" in doc:
            validate_document(doc, "experience.schema.json")
            item = item_from_experience(doc, rel)
        elif "evaluation_id" in doc:
            validate_document(doc, "evaluation.schema.json")
            item = item_from_evaluation(doc, rel)
        elif doc.get("kind") == "routing-proposal" or doc.get("kind") == "routing-apply":
            item = item_from_routing(doc, rel)
        elif "run_id" in doc:
            validate_document(doc, "execution-run.schema.json")
            item = item_from_execution_run(doc, rel)
        else:
            raise IngestError(f"unsupported JSON artifact: {path}")
        write_knowledge_item(repo_root, item)
        written.append(item)
    elif path.name == "DECISIONS.md" or path.suffix == ".md" and "DECISIONS" in path.name:
        text = path.read_text(encoding="utf-8")
        for item in items_from_decisions_md(text, rel):
            write_knowledge_item(repo_root, item)
            written.append(item)
    else:
        raise IngestError(f"unsupported ingest path: {path}")
    return written


def ingest_store_roots(
    repo_root: Path,
    roots: list[str],
) -> dict[str, Any]:
    """Ingest from named store roots (explicit CLI only)."""
    repo_root = Path(repo_root)
    ensure_store_layout(repo_root)
    all_written: list[dict] = []
    sources: list[str] = []

    for root_name in roots:
        key = root_name.strip().lower()
        if key not in STORE_ROOTS:
            raise IngestError(f"unknown store root: {root_name!r}")
        for rel in STORE_ROOTS[key]:
            base = repo_root / rel
            if not base.exists():
                continue
            if base.is_file():
                all_written.extend(ingest_path(repo_root, base))
                sources.append(rel)
                continue
            for path in sorted(base.rglob("*")):
                if path.suffix == ".json" or path.name == "DECISIONS.md":
                    try:
                        all_written.extend(ingest_path(repo_root, path))
                        sources.append(str(path.relative_to(repo_root)))
                    except IngestError:
                        continue

    write_index(repo_root)
    batch_id = f"ingest-{uuid4().hex[:12]}"
    audit = {
        "batch_id": batch_id,
        "kind": "knowledge-ingest",
        "sources": sources,
        "item_count": len(all_written),
        "item_ids": [str(i["item_id"]) for i in all_written],
        "ingested_at": _utc_now(),
    }
    log_dir = ingest_log_dir(repo_root)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{batch_id}.json"
    with log_path.open("w", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {"audit": audit, "audit_path": str(log_path), "items": all_written}
