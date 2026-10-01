"""Persist instruction registry entries and PICCO prompt bundles (M48)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.schemas.validate import ValidationError, validate_document

INSTRUCTION_SCHEMA_VERSION = "1"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class InstructionStoreError(ValueError):
    """Raised when instruction persistence is unsafe or invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def instructions_root(repo_root: Path) -> Path:
    return (
        Path(repo_root)
        / ".agent"
        / "evaluations"
        / "behavior"
        / "instructions"
    )


def proposals_dir(repo_root: Path) -> Path:
    return instructions_root(repo_root) / "proposals"


def bundles_dir(repo_root: Path) -> Path:
    return instructions_root(repo_root) / "bundles"


def registry_path(repo_root: Path) -> Path:
    return instructions_root(repo_root) / "registry.json"


def ensure_layout(repo_root: Path) -> None:
    root = instructions_root(repo_root)
    for sub in ("global", "agents", "task-types", "models", "proposals", "bundles"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    keep = root / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")
    if not registry_path(repo_root).is_file():
        _write_json(
            registry_path(repo_root),
            {
                "schema_version": INSTRUCTION_SCHEMA_VERSION,
                "instruction_ids": [],
                "updated_at": _utc_now(),
            },
        )


def _safe_id(value: str, *, label: str) -> str:
    if not _SAFE_ID.match(value):
        raise InstructionStoreError(f"unsafe {label}: {value!r}")
    return value


def _write_json(path: Path, doc: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(doc, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)
    return path


def _preserve_created_at(path: Path, doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    if path.is_file():
        try:
            with path.open(encoding="utf-8") as handle:
                existing = json.load(handle)
        except (OSError, json.JSONDecodeError):
            existing = None
        if isinstance(existing, dict) and existing.get("created_at"):
            out["created_at"] = str(existing["created_at"])
            out["updated_at"] = _utc_now()
    return out


def instruction_id_for_key(*, scope: str, title: str, agent: str = "", skill_id: str = "") -> str:
    raw = f"{scope}|{title}|{agent}|{skill_id}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"instr-{digest}"


def build_instruction(
    *,
    title: str,
    body: str,
    scope: str = "proposal",
    agent: str = "",
    skill_id: str = "",
    task_type: str = "",
    model_hint: str = "",
    body_path: str = "",
    source_candidate_ids: list[str] | None = None,
    evidence_pattern_ids: list[str] | None = None,
    approval_state: str = "draft",
    instruction_id: str | None = None,
) -> dict[str, Any]:
    iid = instruction_id or instruction_id_for_key(
        scope=scope, title=title, agent=agent, skill_id=skill_id
    )
    _safe_id(iid, label="instruction_id")
    return {
        "instruction_id": iid,
        "scope": scope,
        "title": title,
        "body": body,
        "body_path": body_path,
        "agent": agent,
        "skill_id": skill_id,
        "task_type": task_type,
        "model_hint": model_hint,
        "source_candidate_ids": list(source_candidate_ids or []),
        "evidence_pattern_ids": list(evidence_pattern_ids or []),
        "approval_state": approval_state,
        "schema_version": INSTRUCTION_SCHEMA_VERSION,
        "created_at": _utc_now(),
        "approved_for_execution": False,
        "authority_mutation": False,
    }


def write_instruction(repo_root: Path, instruction: dict[str, Any]) -> Path:
    iid = _safe_id(str(instruction["instruction_id"]), label="instruction_id")
    ensure_layout(repo_root)
    if instruction.get("scope") == "proposal" or instruction.get("approval_state") == "draft":
        path = proposals_dir(repo_root) / f"{iid}.json"
    else:
        path = instructions_root(repo_root) / f"{iid}.json"
    payload = _preserve_created_at(path, instruction)
    try:
        validate_document(payload, "instruction.schema.json")
    except ValidationError as exc:
        raise InstructionStoreError(str(exc)) from exc
    _write_json(path, payload)
    _register_instruction_id(repo_root, iid)
    return path


def _register_instruction_id(repo_root: Path, instruction_id: str) -> None:
    path = registry_path(repo_root)
    ensure_layout(repo_root)
    try:
        with path.open(encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError):
        doc = {"schema_version": INSTRUCTION_SCHEMA_VERSION, "instruction_ids": []}
    ids = [str(x) for x in (doc.get("instruction_ids") or []) if str(x)]
    if instruction_id not in ids:
        ids.append(instruction_id)
        ids.sort()
    doc["instruction_ids"] = ids
    doc["schema_version"] = INSTRUCTION_SCHEMA_VERSION
    doc["updated_at"] = _utc_now()
    _write_json(path, doc)


def list_instructions(repo_root: Path) -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    out: list[dict[str, Any]] = []
    roots = [
        instructions_root(repo_root),
        proposals_dir(repo_root),
    ]
    seen: set[str] = set()
    for base in roots:
        for path in sorted(base.glob("instr-*.json")):
            try:
                with path.open(encoding="utf-8") as handle:
                    doc = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(doc, dict):
                continue
            iid = str(doc.get("instruction_id") or "")
            if not iid or iid in seen:
                continue
            seen.add(iid)
            out.append(doc)
    out.sort(key=lambda d: str(d.get("instruction_id") or ""))
    return out


def load_instruction(repo_root: Path, instruction_id: str) -> dict[str, Any]:
    iid = _safe_id(instruction_id, label="instruction_id")
    for base in (proposals_dir(repo_root), instructions_root(repo_root)):
        path = base / f"{iid}.json"
        if path.is_file():
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
            validate_document(doc, "instruction.schema.json")
            return doc
    raise InstructionStoreError(f"instruction not found: {iid}")


def hash_prompt_bundle_content(bundle: dict[str, Any]) -> str:
    """Stable hash over PICCO fields (excludes timestamps / ids)."""
    payload = {
        "persona": bundle.get("persona") or "",
        "instructions": list(bundle.get("instructions") or []),
        "context": dict(bundle.get("context") or {}),
        "constraints": list(bundle.get("constraints") or []),
        "output": bundle.get("output") or "",
        "instruction_ids": list(bundle.get("instruction_ids") or []),
        "agent": bundle.get("agent") or "",
        "skill_id": bundle.get("skill_id") or "",
        "task_type": bundle.get("task_type") or "",
        "model_hint": bundle.get("model_hint") or "",
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def bundle_id_for_hash(prompt_bundle_hash: str) -> str:
    digest = prompt_bundle_hash.replace("sha256:", "")[:12]
    return f"pbundle-{digest}"


def write_bundle(repo_root: Path, bundle: dict[str, Any]) -> Path:
    ensure_layout(repo_root)
    bid = _safe_id(str(bundle["bundle_id"]), label="bundle_id")
    path = bundles_dir(repo_root) / f"{bid}.json"
    payload = _preserve_created_at(path, bundle)
    try:
        validate_document(payload, "prompt-bundle.schema.json")
    except ValidationError as exc:
        raise InstructionStoreError(str(exc)) from exc
    return _write_json(path, payload)


def list_bundles(repo_root: Path) -> list[dict[str, Any]]:
    ensure_layout(repo_root)
    out: list[dict[str, Any]] = []
    for path in sorted(bundles_dir(repo_root).glob("pbundle-*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                doc = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict):
            out.append(doc)
    return out


def load_bundle(repo_root: Path, bundle_id: str) -> dict[str, Any]:
    bid = _safe_id(bundle_id, label="bundle_id")
    path = bundles_dir(repo_root) / f"{bid}.json"
    if not path.is_file():
        raise InstructionStoreError(f"bundle not found: {bid}")
    with path.open(encoding="utf-8") as handle:
        doc = json.load(handle)
    validate_document(doc, "prompt-bundle.schema.json")
    return doc


def seed_global_operating_brief(repo_root: Path) -> dict[str, Any]:
    """Ensure a minimal global operating-brief instruction exists."""
    ensure_layout(repo_root)
    brief_path = instructions_root(repo_root) / "global" / "operating-brief.md"
    body = (
        "NorthStar behavioral operating brief (proposal-only).\n"
        "- Preserve Captain approval boundaries.\n"
        "- Prefer evidence over assertion.\n"
        "- Do not mutate Skills, routing, or authority without an explicit gate.\n"
    )
    if not brief_path.is_file():
        brief_path.write_text(body, encoding="utf-8")
    instruction = build_instruction(
        title="operating-brief",
        body=body.strip(),
        scope="global",
        body_path="global/operating-brief.md",
        approval_state="candidate",
    )
    # M48: even seed entries stay non-executing
    instruction["approved_for_execution"] = False
    instruction["authority_mutation"] = False
    write_instruction(repo_root, instruction)
    return instruction
