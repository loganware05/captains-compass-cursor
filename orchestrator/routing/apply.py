"""Captain-flagged apply of routing proposals under autonomy budget (Level 3 bounded)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from orchestrator.matcher.score import (
    DEFAULT_WEIGHTS,
    default_weights_path,
    normalize_weights,
    reload_weights,
    write_weights,
)

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
_WEIGHT_APPLY_USED = re.compile(
    r"^- Weight-apply operations used:\s*(\d+)\s*$", re.MULTILINE
)
_WEIGHT_APPLY_MAX = re.compile(
    r"^- Maximum weight-apply operations per plan:\s*(\d+)\s*$", re.MULTILINE
)


class ApplyError(ValueError):
    """Raised when a routing proposal cannot be applied safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def applied_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".agent" / "routing" / "applied"


def load_proposal(path: Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise ApplyError(f"proposal must be object: {path}")
    return doc


def check_autonomy_budget(budget_path: Path | None) -> dict[str, int]:
    """Ensure weight-apply usage is under the plan budget when a ledger exists."""
    if budget_path is None:
        return {"used": 0, "maximum": 3, "remaining": 3}
    path = Path(budget_path)
    if not path.is_file():
        raise ApplyError(f"autonomy budget ledger not found: {path}")
    text = path.read_text(encoding="utf-8")
    used_match = _WEIGHT_APPLY_USED.search(text)
    max_match = _WEIGHT_APPLY_MAX.search(text)
    used = int(used_match.group(1)) if used_match else 0
    maximum = int(max_match.group(1)) if max_match else 3
    if used >= maximum:
        raise ApplyError(
            f"autonomy budget exhausted: weight-apply {used}/{maximum}"
        )
    return {"used": used, "maximum": maximum, "remaining": maximum - used}


def increment_weight_apply_budget(budget_path: Path | None) -> None:
    if budget_path is None:
        return
    path = Path(budget_path)
    text = path.read_text(encoding="utf-8")
    used_match = _WEIGHT_APPLY_USED.search(text)
    if not used_match:
        # Append usage line if ledger predates M4 field
        if not text.endswith("\n"):
            text += "\n"
        text += "- Weight-apply operations used: 1\n"
        path.write_text(text, encoding="utf-8")
        return
    used = int(used_match.group(1))
    text = _WEIGHT_APPLY_USED.sub(
        f"- Weight-apply operations used: {used + 1}", text, count=1
    )
    path.write_text(text, encoding="utf-8")


def eval_gate_rankings_stable(
    skills: list[dict],
    required_capabilities: list[str],
    *,
    before_weights: dict[str, float],
    after_weights: dict[str, float],
) -> None:
    """Fail closed if apply would make ranking non-deterministic or empty unexpectedly."""
    from orchestrator.matcher.score import rank_skills

    before = [r.skill_id for r in rank_skills(skills, required_capabilities, weights=before_weights)]
    after = [r.skill_id for r in rank_skills(skills, required_capabilities, weights=after_weights)]
    if not before and not after:
        return
    if not after and before:
        raise ApplyError("eval gate failed: applied weights produced empty ranking")
    # Determinism check: same inputs → same outputs
    again = [r.skill_id for r in rank_skills(skills, required_capabilities, weights=after_weights)]
    if again != after:
        raise ApplyError("eval gate failed: rankings not deterministic after apply")


def apply_routing_proposal(
    repo_root: Path,
    proposal_path: Path,
    *,
    budget_path: Path | None = None,
    weights_path: Path | None = None,
    run_eval_gate: bool = True,
    skills_for_gate: list[dict] | None = None,
    required_capabilities_for_gate: list[str] | None = None,
) -> dict[str, Any]:
    """
    Apply matcher weight suggestions from a routing proposal.

    Requires captain_approved=true on the proposal. Never mutates Skills/agents.
    auto_apply remains false — apply is an explicit Captain-flagged CLI step.
    """
    repo_root = Path(repo_root)
    proposal = load_proposal(proposal_path)
    if proposal.get("kind") != "routing-proposal":
        raise ApplyError("kind must be routing-proposal")
    if proposal.get("auto_apply") is not False:
        raise ApplyError("auto_apply must remain false; use explicit apply CLI")
    if proposal.get("captain_approved") is not True:
        raise ApplyError(
            "captain_approved must be true on the proposal before apply"
        )

    pid = str(proposal.get("proposal_id") or "")
    if not _SAFE_ID.match(pid):
        raise ApplyError(f"unsafe proposal_id: {pid!r}")

    suggestions = proposal.get("matcher_weight_suggestions")
    if not isinstance(suggestions, dict):
        raise ApplyError("matcher_weight_suggestions must be an object")

    before = dict(DEFAULT_WEIGHTS)
    target_weights = Path(weights_path) if weights_path else (repo_root / "orchestrator" / "matcher" / "weights.json")
    if target_weights.is_file():
        with target_weights.open(encoding="utf-8") as handle:
            before = normalize_weights(json.load(handle))
    elif default_weights_path().is_file():
        with default_weights_path().open(encoding="utf-8") as handle:
            before = normalize_weights(json.load(handle))

    after = normalize_weights(suggestions)
    budget = check_autonomy_budget(budget_path)

    if run_eval_gate:
        skills = skills_for_gate
        caps = required_capabilities_for_gate or ["capability-planning"]
        if skills is None:
            try:
                from orchestrator.registry.load import load_registry, registry_skills

                skills = registry_skills(load_registry(repo_root))
            except Exception:
                skills = []
        if skills:
            eval_gate_rankings_stable(
                skills,
                caps,
                before_weights=before,
                after_weights=after,
            )

    write_weights(target_weights, after)
    if target_weights.resolve() == default_weights_path().resolve():
        reload_weights()

    applied_id = f"applied-{uuid4().hex[:12]}"
    audit = {
        "applied_id": applied_id,
        "kind": "routing-apply",
        "proposal_id": pid,
        "proposal_path": str(Path(proposal_path)),
        "weights_path": str(target_weights),
        "weights_before": before,
        "weights_after": after,
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
    return {"audit": audit, "audit_path": str(audit_path), "weights_path": str(target_weights)}


def restore_default_weights(repo_root: Path | None = None) -> Path:
    """Rollback helper: restore checked-in DEFAULT_WEIGHTS to weights.json."""
    path = (
        Path(repo_root) / "orchestrator" / "matcher" / "weights.json"
        if repo_root
        else default_weights_path()
    )
    write_weights(path, DEFAULT_WEIGHTS)
    if path.resolve() == default_weights_path().resolve():
        reload_weights()
    return path
