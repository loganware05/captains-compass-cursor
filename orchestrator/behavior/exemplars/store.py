"""Persist proposal-only behavior exemplars (M53)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.providers.decision.state import redact_text
from orchestrator.schemas.validate import ValidationError, validate_document

SCHEMA_VERSION = "1"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class ExemplarStoreError(ValueError):
    """Raised when exemplar persistence is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def examples_root(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "examples"


def polarity_dir(repo_root: Path, polarity: str) -> Path:
    return examples_root(repo_root) / polarity


def ensure_layout(repo_root: Path) -> None:
    for polarity in ("positive", "negative"):
        path = polarity_dir(repo_root, polarity)
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise ExemplarStoreError(f"unsafe {label}: {value!r}")
    return value


def exemplar_id_for(payload: dict[str, Any]) -> str:
    material = {
        "polarity": payload.get("polarity"),
        "evaluation_id": payload.get("evaluation_id"),
        "execution_id": payload.get("execution_id"),
        "summary": payload.get("summary"),
    }
    digest = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:12]
    return f"ex-{digest}"


def write_exemplar(repo_root: Path, doc: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    payload = dict(doc)
    payload["auto_promoted"] = False
    payload["approved_for_execution"] = False
    payload["authority_mutation"] = False
    payload["schema_version"] = SCHEMA_VERSION
    payload.setdefault("created_at", _utc_now())
    payload["summary"] = redact_text(str(payload.get("summary") or ""))
    if payload.get("notes"):
        payload["notes"] = redact_text(str(payload["notes"]))
    payload["evidence"] = [redact_text(str(x)) for x in (payload.get("evidence") or [])]
    try:
        validate_document(payload, "behavior-exemplar.schema.json")
    except ValidationError as exc:
        raise ExemplarStoreError(str(exc)) from exc
    polarity = str(payload["polarity"])
    if polarity not in {"positive", "negative"}:
        raise ExemplarStoreError(f"invalid polarity: {polarity!r}")
    eid = _safe_id(str(payload["exemplar_id"]), label="exemplar_id")
    out_dir = polarity_dir(repo_root, polarity) / eid
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "exemplar.json"
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    (out_dir / "README.md").write_text(
        "# Behavior exemplar (M53)\n\n"
        "Proposal-only. Never auto-promotes Skills or Policies.\n"
        f"Polarity: `{polarity}`\n",
        encoding="utf-8",
    )
    doc.clear()
    doc.update(payload)
    return path


def load_exemplar(repo_root: Path, exemplar_id: str) -> dict[str, Any]:
    eid = _safe_id(exemplar_id, label="exemplar_id")
    for polarity in ("positive", "negative"):
        path = polarity_dir(repo_root, polarity) / eid / "exemplar.json"
        if path.is_file():
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
            validate_document(doc, "behavior-exemplar.schema.json")
            return doc
    raise ExemplarStoreError(f"exemplar not found: {exemplar_id}")


def list_exemplars(repo_root: Path, *, polarity: str = "") -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    polarities = [polarity] if polarity in {"positive", "negative"} else ["positive", "negative"]
    out: list[dict[str, Any]] = []
    for pol in polarities:
        root = polarity_dir(repo_root, pol)
        for path in sorted(root.glob("ex-*/exemplar.json")):
            try:
                with path.open(encoding="utf-8") as handle:
                    doc = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(doc, dict):
                out.append(doc)
    return out
