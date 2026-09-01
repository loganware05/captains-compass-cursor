"""Plan context selection profiles and Captain-approved apply (M17 Stage 3)."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.schemas.validate import validate_document

CONTEXT_SLICES = (
    "knowledge",
    "performance",
    "procedure",
    "artifact",
    "technology_intelligence",
    "experience_signals",
)

DEFAULT_SLICE_CONFIG: dict[str, dict[str, Any]] = {
    "knowledge": {"enabled": True, "top_n": 5},
    "performance": {"enabled": True, "top_n": 5},
    "procedure": {"enabled": True, "top_n": 5},
    "artifact": {"enabled": True, "top_n": 5},
    "technology_intelligence": {"enabled": True, "top_n": 10},
    "experience_signals": {"enabled": True, "top_n": 5},
}

PROCEDURE_SKILLS = frozenset(
    {"procedure-playbooks", "bounded-autonomy", "experience-routing", "knowledge-steward"}
)
PERFORMANCE_SKILLS = frozenset(
    {"execution-telemetry", "experience-skill-training", "compass-evaluator"}
)
TI_SKILLS = frozenset(
    {
        "technology-intelligence-live",
        "candidate-promotion",
        "package-registry-ti",
    }
)

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")


class ContextSelectionError(ValueError):
    """Raised when context selection operations fail."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_context_profile() -> dict[str, Any]:
    return {
        "profile_id": "default",
        "slices": deepcopy(DEFAULT_SLICE_CONFIG),
        "source": "builtin-default",
    }


def normalize_slice_config(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slices = raw.get("slices") if isinstance(raw.get("slices"), dict) else raw
    if not isinstance(slices, dict):
        raise ContextSelectionError("context profile requires slices object")
    out: dict[str, dict[str, Any]] = {}
    for key in CONTEXT_SLICES:
        entry = slices.get(key, DEFAULT_SLICE_CONFIG[key])
        if not isinstance(entry, dict):
            raise ContextSelectionError(f"slice config must be object: {key}")
        enabled = bool(entry.get("enabled", True))
        top_n = int(entry.get("top_n", DEFAULT_SLICE_CONFIG[key]["top_n"]))
        if top_n < 0:
            raise ContextSelectionError(f"top_n must be non-negative for {key}")
        out[key] = {"enabled": enabled, "top_n": top_n}
    return out


def normalize_context_profile(raw: dict[str, Any]) -> dict[str, Any]:
    profile_id = str(raw.get("profile_id") or "custom")
    if not _SAFE_ID.match(profile_id.replace("_", "-")):
        raise ContextSelectionError(f"unsafe profile_id: {profile_id!r}")
    return {
        "profile_id": profile_id,
        "slices": normalize_slice_config(raw),
        "source": str(raw.get("source") or "captain-approved"),
        "updated_at": str(raw.get("updated_at") or _utc_now()),
    }


def active_profile_path(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "routing" / "context-selection-active.json"


def proposals_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "routing" / "proposals"


def applied_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "routing" / "applied"


def load_active_context_profile(repo_root: Path) -> dict[str, Any]:
    path = active_profile_path(repo_root)
    if not path.is_file():
        return default_context_profile()
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ContextSelectionError(f"context profile must be object: {path}")
    return normalize_context_profile(raw)


def write_active_context_profile(repo_root: Path, profile: dict[str, Any]) -> Path:
    normalized = normalize_context_profile(profile)
    path = active_profile_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(normalized, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def build_context_selection_proposal(
    experiences: list[dict],
    *,
    proposal_id: str | None = None,
    notes: str = "",
) -> dict:
    """Derive slice tuning suggestions from Experience outcomes (proposal-only)."""
    profile = default_context_profile()
    slices = deepcopy(profile["slices"])
    experience_ids: list[str] = []
    procedure_hits = 0
    performance_hits = 0
    ti_hits = 0

    for exp in experiences:
        eid = str(exp.get("experience_id") or "")
        if eid:
            experience_ids.append(eid)
        if exp.get("outcome") != "success":
            continue
        for skill in exp.get("skills_used") or []:
            skill = str(skill)
            if skill in PROCEDURE_SKILLS:
                procedure_hits += 1
            if skill in PERFORMANCE_SKILLS:
                performance_hits += 1
            if skill in TI_SKILLS:
                ti_hits += 1

    rationales: list[str] = []
    if procedure_hits:
        slices["procedure"]["top_n"] = min(8, slices["procedure"]["top_n"] + 2)
        slices["artifact"]["enabled"] = False
        rationales.append(
            f"Procedure-heavy successes ({procedure_hits}); raise procedure top_n, disable artifact slice"
        )
    if performance_hits:
        slices["performance"]["top_n"] = min(8, slices["performance"]["top_n"] + 2)
        rationales.append(
            f"Performance telemetry successes ({performance_hits}); raise performance top_n"
        )
    if ti_hits:
        slices["technology_intelligence"]["top_n"] = min(12, slices["technology_intelligence"]["top_n"] + 2)
        rationales.append(f"TI-related successes ({ti_hits}); raise technology_intelligence top_n")

    suggestion_profile = normalize_context_profile(
        {
            "profile_id": "experience-tuned",
            "slices": slices,
            "source": "context-selection-proposal",
        }
    )

    return {
        "proposal_id": proposal_id or f"ctxsel-{uuid4().hex[:12]}",
        "kind": "context-selection-proposal",
        "based_on_experiences": experience_ids,
        "context_profile_suggestions": suggestion_profile,
        "auto_apply": False,
        "captain_approved": False,
        "captain_approval_required": True,
        "notes": notes
        or (
            "; ".join(rationales)
            if rationales
            else "Proposal-only until Captain sets captain_approved=true and runs apply-context-selection-proposal.sh"
        ),
        "created_at": _utc_now(),
    }


def write_context_selection_proposal(repo_root: Path, proposal: dict) -> Path:
    if proposal.get("auto_apply") is not False:
        raise ContextSelectionError("auto_apply must be false")
    validate_document(proposal, "context-selection-proposal.schema.json")
    pid = str(proposal["proposal_id"])
    if not _SAFE_ID.match(pid):
        raise ContextSelectionError(f"unsafe proposal_id: {pid!r}")
    out_dir = proposals_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{pid}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(proposal, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def apply_context_selection_proposal(
    repo_root: Path,
    proposal_path: Path,
    *,
    budget_path: Path | None = None,
) -> dict[str, Any]:
    from orchestrator.routing.apply import check_autonomy_budget, increment_weight_apply_budget

    repo_root = Path(repo_root)
    with Path(proposal_path).open(encoding="utf-8") as handle:
        proposal = json.load(handle)
    if not isinstance(proposal, dict):
        raise ContextSelectionError("proposal must be object")
    if proposal.get("kind") != "context-selection-proposal":
        raise ContextSelectionError("kind must be context-selection-proposal")
    if proposal.get("auto_apply") is not False:
        raise ContextSelectionError("auto_apply must remain false")
    if proposal.get("captain_approved") is not True:
        raise ContextSelectionError("captain_approved must be true before apply")

    suggestions = proposal.get("context_profile_suggestions")
    if not isinstance(suggestions, dict):
        raise ContextSelectionError("context_profile_suggestions must be an object")

    budget = check_autonomy_budget(budget_path)
    before = load_active_context_profile(repo_root)
    after = normalize_context_profile(suggestions)
    profile_path = write_active_context_profile(repo_root, after)

    applied_id = f"applied-{uuid4().hex[:12]}"
    audit = {
        "applied_id": applied_id,
        "kind": "context-selection-apply",
        "proposal_id": str(proposal.get("proposal_id") or ""),
        "proposal_path": str(Path(proposal_path)),
        "profile_path": str(profile_path),
        "profile_before": before,
        "profile_after": after,
        "captain_approved": True,
        "budget": budget,
        "applied_at": _utc_now(),
    }
    out_dir = applied_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_path = out_dir / f"{applied_id}.json"
    with audit_path.open("w", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2, sort_keys=True)
        handle.write("\n")

    increment_weight_apply_budget(budget_path)
    return {"audit": audit, "audit_path": str(audit_path), "profile_path": str(profile_path)}


def fetch_plan_context_slices(
    repo_root: Path,
    objective: str,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Query knowledge/TI/experience slices per active context profile."""
    repo_root = Path(repo_root)
    active = profile or load_active_context_profile(repo_root)
    slices = active["slices"]
    knowledge_search_mode = "keyword"

    result: dict[str, Any] = {
        "knowledge_context": [],
        "performance_context": [],
        "procedure_context": [],
        "artifact_context": [],
        "technology_intelligence_candidates": [],
        "experience_signals": [],
        "knowledge_search_mode": knowledge_search_mode,
        "context_profile_id": active.get("profile_id", "default"),
    }

    try:
        from orchestrator.knowledge.vector_index import select_knowledge_search_mode

        knowledge_search_mode = select_knowledge_search_mode(repo_root)
        result["knowledge_search_mode"] = knowledge_search_mode
    except Exception:
        pass

    if slices["knowledge"]["enabled"] and slices["knowledge"]["top_n"] > 0:
        try:
            from orchestrator.knowledge.query import query_knowledge

            result["knowledge_context"] = query_knowledge(
                repo_root,
                objective,
                top_n=slices["knowledge"]["top_n"],
                rebuild_index=False,
                mode=knowledge_search_mode,
            )
        except Exception:
            pass

    if slices["performance"]["enabled"] and slices["performance"]["top_n"] > 0:
        try:
            from orchestrator.knowledge.query import query_knowledge

            result["performance_context"] = query_knowledge(
                repo_root,
                objective,
                kind="performance",
                top_n=slices["performance"]["top_n"],
                rebuild_index=False,
                mode=knowledge_search_mode,
            )
        except Exception:
            pass

    if slices["procedure"]["enabled"] and slices["procedure"]["top_n"] > 0:
        try:
            from orchestrator.knowledge.query import query_knowledge

            result["procedure_context"] = query_knowledge(
                repo_root,
                objective,
                kind="procedure",
                top_n=slices["procedure"]["top_n"],
                rebuild_index=False,
                mode=knowledge_search_mode,
            )
        except Exception:
            pass

    if slices["artifact"]["enabled"] and slices["artifact"]["top_n"] > 0:
        try:
            from orchestrator.knowledge.query import query_knowledge

            result["artifact_context"] = query_knowledge(
                repo_root,
                objective,
                kind="artifact",
                top_n=slices["artifact"]["top_n"],
                rebuild_index=False,
                mode=knowledge_search_mode,
            )
        except Exception:
            pass

    if slices["technology_intelligence"]["enabled"]:
        try:
            from orchestrator.providers.technology_intelligence.file_provider import select_ti_provider

            ti_top = int(slices["technology_intelligence"]["top_n"])
            provider = select_ti_provider(repo_root)
            candidates = [
                item.to_dict()
                for item in provider.discover_candidates(objective, {})
            ][:ti_top]
        except Exception:
            candidates = []

        from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates

        validate_ti_candidates(candidates)
        result["technology_intelligence_candidates"] = candidates

    if slices["experience_signals"]["enabled"]:
        max_items = int(slices["experience_signals"]["top_n"])
        signals: list[dict] = []
        for folder in (
            repo_root / "tests" / "fixtures" / "experience",
            repo_root / ".agent" / "experience",
        ):
            if not folder.is_dir():
                continue
            for path in sorted(folder.glob("*.json")):
                if len(signals) >= max_items:
                    break
                try:
                    with path.open(encoding="utf-8") as handle:
                        doc = json.load(handle)
                    if isinstance(doc, dict) and doc.get("experience_id"):
                        signals.append(
                            {
                                "experience_id": doc.get("experience_id"),
                                "outcome": doc.get("outcome"),
                                "skills_used": list(doc.get("skills_used") or [])[:8],
                            }
                        )
                except (OSError, json.JSONDecodeError):
                    continue
        result["experience_signals"] = signals

    return result
