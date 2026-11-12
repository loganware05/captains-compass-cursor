"""Local-first C2 session memory (progressive index → detail).

Inspired by claude-mem progressive retrieval (DISCOVERED; not installed).
Never rewrites canonical project memory docs. Authority locks always false.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.cognitive.enabled import require_session_memory_enabled
from orchestrator.schemas.validate import validate_document

_SECRET_HINT = re.compile(
    r"(?i)(api[_-]?key|secret|passwd|password|token|authorization|cookie)\s*[:=]\s*\S+"
)


class SessionMemoryError(ValueError):
    """Operator-facing session memory errors."""


def session_memory_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "session-memory"


def observations_dir(repo_root: Path) -> Path:
    return session_memory_root(repo_root) / "observations"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_observation_id() -> str:
    return f"obs-{uuid.uuid4().hex[:12]}"


def _reject_secrets(text: str) -> None:
    if _SECRET_HINT.search(text or ""):
        raise SessionMemoryError(
            "refusing to ingest text that looks like a secret "
            "(api key / password / token / cookie pattern)"
        )


def _ensure_locks(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    out["approved_for_execution"] = False
    out["authority_mutation"] = False
    if "schema_version" not in out:
        out["schema_version"] = "1"
    if "keywords" not in out or out["keywords"] is None:
        out["keywords"] = []
    return out


def _observation_path(repo_root: Path, observation_id: str) -> Path:
    safe = observation_id.strip()
    if not safe or "/" in safe or "\\" in safe or ".." in safe:
        raise SessionMemoryError(f"invalid observation_id: {observation_id!r}")
    return observations_dir(repo_root) / f"{safe}.json"


def list_observations(repo_root: Path) -> list[dict[str, Any]]:
    require_session_memory_enabled()
    root = observations_dir(repo_root)
    if not root.is_dir():
        return []
    docs: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict) and doc.get("observation_id"):
            docs.append(doc)
    docs.sort(key=lambda d: str(d.get("created_at") or ""), reverse=True)
    return docs


def show_observation(repo_root: Path, observation_id: str) -> dict[str, Any]:
    require_session_memory_enabled()
    path = _observation_path(repo_root, observation_id)
    if not path.is_file():
        raise SessionMemoryError(f"observation not found: {observation_id}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise SessionMemoryError(f"invalid observation file: {path}")
    doc = _ensure_locks(doc)
    validate_document(doc, "session-observation.schema.json")
    return doc


def ingest_observation(
    repo_root: Path,
    *,
    path: Path | None = None,
    document: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Ingest from a JSON file or in-memory document. Hermetic; no network."""
    require_session_memory_enabled()
    if path is None and document is None:
        raise SessionMemoryError("ingest requires --path or an in-memory document")
    if path is not None and document is not None:
        raise SessionMemoryError("pass either path or document, not both")

    if path is not None:
        src = Path(path)
        if not src.is_file():
            raise SessionMemoryError(f"ingest path not found: {src}")
        with src.open(encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise SessionMemoryError("ingest file must be a JSON object")
        doc = _ensure_locks(raw)
        source = dict(doc.get("source") or {})
        source.setdefault("type", "fixture" if "fixture" in str(src) else "cli")
        source["path"] = str(src)
        doc["source"] = source
    else:
        assert document is not None
        doc = _ensure_locks(document)
        source = dict(doc.get("source") or {})
        source.setdefault("type", "manual")
        doc["source"] = source

    if not doc.get("observation_id"):
        doc["observation_id"] = _new_observation_id()
    if not doc.get("created_at"):
        doc["created_at"] = _utc_now()

    for field in ("title", "summary", "body"):
        if not str(doc.get(field) or "").strip():
            raise SessionMemoryError(f"missing required field: {field}")
        _reject_secrets(str(doc[field]))

    validate_document(doc, "session-observation.schema.json")

    out_dir = observations_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = _observation_path(repo_root, str(doc["observation_id"]))
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {
        "status": "ingested",
        "observation_id": doc["observation_id"],
        "path": str(out_path),
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9_]{2,}", (text or "").lower()) if t}


def _score(query: str, doc: dict[str, Any]) -> float:
    q_tokens = _tokenize(query)
    if not q_tokens:
        return 0.0
    blob = " ".join(
        [
            str(doc.get("title") or ""),
            str(doc.get("summary") or ""),
            " ".join(doc.get("keywords") or []),
        ]
    )
    d_tokens = _tokenize(blob)
    if not d_tokens:
        return 0.0
    overlap = len(q_tokens & d_tokens)
    return overlap / max(len(q_tokens), 1)


def search_observations(
    repo_root: Path,
    query: str,
    *,
    top_n: int = 10,
) -> dict[str, Any]:
    """Return compact index only — no full bodies."""
    require_session_memory_enabled()
    q = (query or "").strip()
    if top_n < 1:
        top_n = 1
    if top_n > 50:
        top_n = 50

    scored: list[tuple[float, dict[str, Any]]] = []
    for doc in list_observations(repo_root):
        score = _score(q, doc) if q else 0.0
        if q and score <= 0:
            continue
        if not q:
            score = 1.0
        scored.append((score, doc))
    scored.sort(key=lambda pair: (-pair[0], str(pair[1].get("created_at") or "")))

    results = [
        {
            "observation_id": str(doc.get("observation_id") or ""),
            "title": str(doc.get("title") or ""),
            "summary": str(doc.get("summary") or "")[:500],
            "created_at": str(doc.get("created_at") or ""),
            "query_score": float(score),
        }
        for score, doc in scored[:top_n]
    ]
    payload = {
        "schema_version": "1",
        "query": q,
        "results": results,
        "notes": (
            "Compact session-memory index. Use brain memory show --id "
            "to fetch full observation bodies."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    validate_document(payload, "session-memory-search-response.schema.json")
    return payload


def timeline_observations(repo_root: Path, *, limit: int = 20) -> dict[str, Any]:
    require_session_memory_enabled()
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    docs = list_observations(repo_root)[:limit]
    results = [
        {
            "observation_id": str(doc.get("observation_id") or ""),
            "title": str(doc.get("title") or ""),
            "summary": str(doc.get("summary") or "")[:500],
            "created_at": str(doc.get("created_at") or ""),
            "query_score": 1.0,
        }
        for doc in docs
    ]
    payload = {
        "schema_version": "1",
        "query": "",
        "results": results,
        "notes": "Session-memory timeline (newest first); summaries only.",
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    validate_document(payload, "session-memory-search-response.schema.json")
    return payload
