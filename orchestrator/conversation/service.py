"""Operator service for northstar conversation ingest|show|list."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.conversation.enabled import require_conversation_ingest_enabled
from orchestrator.conversation.parser import (
    ConversationParseError,
    default_model_or_source,
    normalize_source,
    parse_obsidian_chatgpt_export,
)
from orchestrator.conversation.store import (
    ConversationStoreError,
    list_trajectory_docs,
    load_trajectory,
    write_exemplar_draft,
    write_ingest_log,
    write_trajectory,
)
from orchestrator.knowledge.store import (
    KnowledgeStoreError,
    reject_secret_path,
    write_knowledge_item,
)

_EXCERPT_LEN = 480
_SAFE_SLUG = re.compile(r"[^a-z0-9-]+")


class ConversationServiceError(ValueError):
    """Operator-facing conversation ingest errors."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _excerpt(text: str, limit: int = _EXCERPT_LEN) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _safe_conv_slug(conversation_id: str) -> str:
    raw = conversation_id
    if raw.startswith("chatgpt_"):
        raw = raw[len("chatgpt_") :]
    slug = _SAFE_SLUG.sub("-", raw.lower()).strip("-")
    return (slug or "conversation")[:48]


def _trajectory_id(conversation_id: str, turn_index: int) -> str:
    return f"conv-{_safe_conv_slug(conversation_id)}-t{turn_index:03d}"


def _keywords_for(user_prompt: str, section_title: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", user_prompt.lower())
    out: list[str] = ["conversation", "external", "chatgpt"]
    for word in words[:12]:
        if word not in out:
            out.append(word)
    title_slug = _SAFE_SLUG.sub("-", section_title.lower()).strip("-")
    if title_slug and title_slug not in out:
        out.append(title_slug[:40])
    return out[:24]


def _knowledge_item_from_trajectory(traj: dict[str, Any]) -> dict[str, Any]:
    title = f"Conversation turn {traj['turn_index']}: {_excerpt(traj['user_prompt'], 80)}"
    summary = (
        f"User: {_excerpt(traj['user_prompt'], 400)} | "
        f"Suggestion ({traj['model_or_source']}): {traj['assistant_suggestion_excerpt']}"
    )
    now = _utc_now()
    return {
        "item_id": f"know-{traj['trajectory_id']}",
        "kind": "knowledge",
        "title": title,
        "summary": summary[:2000],
        "keywords": list(traj.get("keywords") or ["conversation", "external"]),
        "confidence": 0.7,
        "source_artifact": {
            "type": "conversation-trajectory",
            "id": traj["trajectory_id"],
            "path": traj["source_path"],
        },
        "provenance": {
            "external_source": traj["source"],
            "export_mode": "file",
            "claim_kind": "external",
            "conversation_id": traj["conversation_id"],
            "model_or_source": traj["model_or_source"],
            "trajectory_id": traj["trajectory_id"],
            "approved_for_execution": False,
            "authority_mutation": False,
            "auto_promoted": False,
        },
        "created_at": now,
        "updated_at": now,
    }


def ingest_conversation_export(
    repo_root: Path,
    path: Path,
    *,
    source: str = "obsidian-ai-exporter",
    model: str | None = None,
    draft_exemplar: str | None = None,
    write_knowledge: bool = True,
) -> dict[str, Any]:
    """Ingest a ChatGPT/Obsidian markdown export into trajectories + knowledge."""
    require_conversation_ingest_enabled()
    repo_root = Path(repo_root)
    path = Path(path).resolve()
    try:
        reject_secret_path(str(path))
    except Exception as exc:  # KnowledgeStoreError
        raise ConversationServiceError(str(exc)) from exc
    if not path.is_file():
        raise ConversationServiceError(f"export not found: {path}")
    if path.suffix.lower() != ".md":
        raise ConversationServiceError(f"expected .md export: {path}")

    try:
        source_norm = normalize_source(source)
    except ConversationParseError as exc:
        raise ConversationServiceError(str(exc)) from exc

    text = path.read_text(encoding="utf-8")
    digest = _sha256_text(text)
    try:
        parsed = parse_obsidian_chatgpt_export(text)
    except ConversationParseError as exc:
        raise ConversationServiceError(str(exc)) from exc

    rel = str(path.relative_to(repo_root)) if path.is_relative_to(repo_root) else str(path)
    model_or_source = default_model_or_source(source_norm, model)
    ingested_at = _utc_now()
    written: list[dict[str, Any]] = []
    knowledge_ids: list[str] = []

    for turn in parsed.turns:
        traj_id = _trajectory_id(parsed.conversation_id, turn.turn_index)
        doc: dict[str, Any] = {
            "schema_version": "1",
            "trajectory_id": traj_id,
            "conversation_id": parsed.conversation_id,
            "turn_index": turn.turn_index,
            "source": source_norm,
            "model_or_source": model_or_source,
            "user_prompt": turn.user_prompt,
            "assistant_suggestion": turn.assistant_suggestion,
            "assistant_suggestion_excerpt": _excerpt(turn.assistant_suggestion),
            "claim_kind": "external",
            "source_path": rel,
            "source_sha256": digest,
            "source_url": parsed.source_url,
            "exported_at": parsed.exported_at,
            "ingested_at": ingested_at,
            "thread_title": parsed.title,
            "keywords": _keywords_for(turn.user_prompt, turn.section_title),
            "approved_for_execution": False,
            "authority_mutation": False,
            "auto_promoted": False,
        }
        try:
            write_trajectory(repo_root, doc)
        except ConversationStoreError as exc:
            raise ConversationServiceError(str(exc)) from exc
        written.append(doc)

        if write_knowledge:
            try:
                item = _knowledge_item_from_trajectory(doc)
                write_knowledge_item(repo_root, item)
                knowledge_ids.append(item["item_id"])
            except (KnowledgeStoreError, OSError, ValueError) as exc:
                raise ConversationServiceError(f"knowledge write failed: {exc}") from exc

    exemplar_path = None
    if draft_exemplar:
        polarity = draft_exemplar.strip().lower()
        if polarity not in {"positive", "negative"}:
            raise ConversationServiceError("draft_exemplar must be positive|negative")
        first = written[0]
        draft_id = f"draft-{first['trajectory_id']}-{polarity}"
        payload = {
            "draft_id": draft_id,
            "polarity": polarity,
            "trajectory_id": first["trajectory_id"],
            "conversation_id": first["conversation_id"],
            "summary": (
                f"{polarity} exemplar draft from conversation trajectory "
                f"{first['trajectory_id']}"
            ),
            "notes": (
                "Proposal-only conversation exemplar draft. Captain must review "
                "before any learning use. Not auto-promoted."
            ),
            "user_prompt_excerpt": _excerpt(first["user_prompt"], 240),
            "assistant_suggestion_excerpt": first["assistant_suggestion_excerpt"],
            "model_or_source": first["model_or_source"],
            "auto_promoted": False,
            "approved_for_execution": False,
            "authority_mutation": False,
            "created_at": ingested_at,
        }
        exemplar_path = str(write_exemplar_draft(repo_root, draft_id, payload))

    log_id = f"ingest-{uuid4().hex[:12]}"
    log_payload = {
        "log_id": log_id,
        "source_path": rel,
        "source_sha256": digest,
        "source": source_norm,
        "conversation_id": parsed.conversation_id,
        "trajectory_ids": [t["trajectory_id"] for t in written],
        "knowledge_item_ids": knowledge_ids,
        "turn_count": len(written),
        "exemplar_draft_path": exemplar_path,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "ingested_at": ingested_at,
    }
    write_ingest_log(repo_root, log_id, log_payload)

    return {
        "status": "ingested",
        "conversation_id": parsed.conversation_id,
        "thread_title": parsed.title,
        "turn_count": len(written),
        "trajectory_ids": [t["trajectory_id"] for t in written],
        "knowledge_item_ids": knowledge_ids,
        "exemplar_draft_path": exemplar_path,
        "source_sha256": digest,
        "log_id": log_id,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
    }


def show_trajectory(repo_root: Path, trajectory_id: str) -> dict[str, Any]:
    require_conversation_ingest_enabled()
    try:
        return load_trajectory(repo_root, trajectory_id)
    except ConversationStoreError as exc:
        raise ConversationServiceError(str(exc)) from exc


def list_trajectories(repo_root: Path) -> dict[str, Any]:
    require_conversation_ingest_enabled()
    docs = list_trajectory_docs(repo_root)
    return {
        "count": len(docs),
        "trajectories": [
            {
                "trajectory_id": d["trajectory_id"],
                "conversation_id": d["conversation_id"],
                "turn_index": d["turn_index"],
                "model_or_source": d["model_or_source"],
                "thread_title": d.get("thread_title") or "",
                "ingested_at": d["ingested_at"],
            }
            for d in docs
        ],
        "approved_for_execution": False,
        "authority_mutation": False,
    }
