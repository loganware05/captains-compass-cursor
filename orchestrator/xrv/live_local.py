"""XRV live-local ops smoke — doctor + reconstruct against a real tip SHA.

No production deploy. live_deploy stays false unless explicitly forced
(and still recorded as a refused production claim when unset).
Proposal/evidence only — never grants authority.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.xrv.eer import reconstruct_cycle, validate_eer_document
from orchestrator.xrv.gates import require_xrv_eer_enabled

_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
_TRUTHY = frozenset({"1", "true", "yes", "on"})


class LiveLocalError(ValueError):
    """Raised when live-local smoke cannot proceed safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_id(value: str, label: str = "id") -> str:
    if not _SAFE_ID.match(value):
        raise LiveLocalError(f"unsafe {label}: {value!r}")
    return value


def resolve_tip_sha(repo_root: Path, *, tip_sha: str | None = None) -> str:
    """Return a real git tip SHA (or an explicit override for hermetic tests)."""
    if tip_sha:
        sha = tip_sha.strip().lower()
        if not _SHA_RE.match(sha):
            raise LiveLocalError(f"invalid tip_sha: {tip_sha!r}")
        return sha
    root = Path(repo_root).resolve()
    try:
        completed = subprocess.run(  # noqa: S603
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LiveLocalError(f"git rev-parse failed: {exc}") from exc
    if completed.returncode != 0:
        raise LiveLocalError(
            f"git rev-parse failed: {(completed.stderr or completed.stdout or '').strip()}"
        )
    sha = (completed.stdout or "").strip().lower()
    if not _SHA_RE.match(sha):
        raise LiveLocalError(f"unexpected git SHA: {sha!r}")
    return sha


def _run_doctor(repo_root: Path) -> dict[str, Any]:
    doctor = Path(repo_root) / "scripts" / "doctor.sh"
    if not doctor.is_file():
        raise LiveLocalError(f"doctor.sh missing: {doctor}")
    try:
        completed = subprocess.run(  # noqa: S603
            ["bash", str(doctor)],
            cwd=str(repo_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=600,
            env={k: v for k, v in os.environ.items() if k != "COMPASS_CAPTAIN_APPROVE"},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LiveLocalError(f"doctor failed: {exc}") from exc
    tail = "\n".join((completed.stdout or "").splitlines()[-40:])
    return {
        "command": "scripts/doctor.sh",
        "exit_code": completed.returncode,
        "ok": completed.returncode == 0,
        "stdout_tail": tail,
        "stderr_tail": (completed.stderr or "")[-2000:],
    }


def _build_eer(
    *,
    tip_sha: str,
    smoke_id: str,
    issue: str | None,
    plan_id: str,
    evidence_paths: list[str],
) -> dict[str, Any]:
    now = _utc_now()
    return {
        "schema_version": "xrv-eer-1",
        "eer_id": f"eer-ops-live-local-{smoke_id}",
        "created_at": now,
        "repository": {
            "owner": "loganware05",
            "name": "captains-compass-cursor",
            "url": "https://github.com/loganware05/captains-compass-cursor",
        },
        "commit_sha": tip_sha,
        "plan_id": plan_id,
        "issue": issue,
        "pull_request": None,
        "branch": None,
        "lifecycle_state": "operationally_verified",
        "skills_selected": [
            "implementation-planning",
            "testing-validation",
            "github-integration",
        ],
        "budget_ref": ".agent/budgets/xrv-ops-live-local.md",
        "permissions": [
            "live-local-smoke",
            "no-production-deploy",
        ],
        "test_evidence": evidence_paths,
        "failure_repair": [],
        "review_refs": [
            "Live-local ops smoke (doctor + reconstruct; live_deploy=false)",
        ],
        "rollback_ref": "rollback/pre-xrv-ops-live-local",
        "latency_cost": {
            "notes": "Local doctor + reconstruct smoke; no external hosts",
        },
        "verified_outcome": (
            "Local operational smoke bound to authentic tip SHA; "
            "auditor reconstruct complete; production deploy not claimed."
        ),
        "experience_id": None,
        "execution_run_id": None,
        "related_evidence_paths": [
            "docs/plans/XRV_OPS_LIVE_LOCAL.md",
            "orchestrator/xrv/live_local.py",
        ],
        "notes": (
            "Live-local smoke. ops_verification.live_deploy=false. "
            "Does not claim production/remote deploy."
        ),
        "ops_verification": {
            "smoke_id": smoke_id,
            "verified_at": now,
            "repository_sha": tip_sha,
            "evidence_paths": evidence_paths,
            "live_deploy": False,
            "notes": "Local control-repo tip smoke only",
        },
        "approved_for_execution": False,
        "authority_mutation": False,
        "issues_auto_closed": False,
        "auto_promoted": False,
    }


def run_live_local_smoke(
    repo_root: Path,
    *,
    require_gate: bool = True,
    tip_sha: str | None = None,
    run_doctor: bool = True,
    smoke_id: str | None = None,
    plan_id: str = "xrv-ops-live-local",
    issue: str | None = "https://github.com/loganware05/captains-compass-cursor/issues/316",
    allow_live_deploy: bool = False,
) -> dict[str, Any]:
    """Execute local ops smoke and write evidence + ops-verified EER.

    ``allow_live_deploy`` is refused unless COMPASS_XRV_LIVE_DEPLOY=1 — and even
    then this path keeps live_deploy=false (production deploy remains out of scope).
    """
    if require_gate:
        require_xrv_eer_enabled()

    if allow_live_deploy or (
        (os.environ.get("COMPASS_XRV_LIVE_DEPLOY") or "").strip().lower() in _TRUTHY
    ):
        # Explicitly refuse production claim in this wave.
        raise LiveLocalError(
            "production live_deploy is out of scope for xrv-ops-live-local "
            "(keep live_deploy=false)"
        )

    root = Path(repo_root).resolve()
    sha = resolve_tip_sha(root, tip_sha=tip_sha)
    sid = _safe_id(smoke_id or f"live-local-{sha[:12]}")
    out_dir = root / ".agent" / "evidence" / "xrv-ops-live-local" / sid
    out_dir.mkdir(parents=True, exist_ok=True)

    doctor_result: dict[str, Any]
    if run_doctor:
        doctor_result = _run_doctor(root)
        (out_dir / "doctor.txt").write_text(
            doctor_result.get("stdout_tail") or "", encoding="utf-8"
        )
        if not doctor_result.get("ok"):
            raise LiveLocalError(
                f"doctor failed (exit {doctor_result.get('exit_code')})"
            )
    else:
        doctor_result = {
            "command": "scripts/doctor.sh",
            "exit_code": 0,
            "ok": True,
            "skipped": True,
            "note": "doctor skipped (hermetic/unit path)",
        }

    evidence_paths = [
        f".agent/evidence/xrv-ops-live-local/{sid}/smoke.json",
        f".agent/evidence/xrv-ops-live-local/{sid}/eer.json",
    ]
    eer = _build_eer(
        tip_sha=sha,
        smoke_id=sid,
        issue=issue,
        plan_id=plan_id,
        evidence_paths=evidence_paths,
    )
    validate_eer_document(root, eer)
    cycle = reconstruct_cycle(eer)
    if not cycle.get("ops_verified") or not cycle.get("cycle_complete_for_state"):
        raise LiveLocalError("reconstruct cycle incomplete for operationally_verified")

    eer_path = out_dir / "eer.json"
    eer_path.write_text(json.dumps(eer, indent=2) + "\n", encoding="utf-8")
    (out_dir / "reconstruct.json").write_text(
        json.dumps(cycle, indent=2) + "\n", encoding="utf-8"
    )

    smoke = {
        "smoke_id": sid,
        "plan_id": plan_id,
        "mode": "live-local",
        "live_deploy": False,
        "repository_sha": sha,
        "verified_at": _utc_now(),
        "doctor": doctor_result,
        "reconstruct": {
            "ops_verified": True,
            "cycle_complete_for_state": True,
            "lifecycle_state": cycle.get("lifecycle_state"),
        },
        "status": "pass",
        "approved_for_execution": False,
        "authority_mutation": False,
        "issues_auto_closed": False,
        "auto_promoted": False,
        "notes": "Local tip smoke only; production deploy not claimed.",
    }
    (out_dir / "smoke.json").write_text(
        json.dumps(smoke, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                f"# XRV live-local smoke `{sid}`",
                "",
                f"- Tip SHA: `{sha}`",
                f"- live_deploy: **false**",
                f"- Doctor ok: `{doctor_result.get('ok')}`",
                f"- Reconstruct ops_verified: **true**",
                f"- EER: `.agent/evidence/xrv-ops-live-local/{sid}/eer.json`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    return {
        "status": "ok",
        "smoke_id": sid,
        "repository_sha": sha,
        "live_deploy": False,
        "eer_path": str(eer_path),
        "evidence_dir": str(out_dir),
        "ops_verified": True,
        "doctor_ok": bool(doctor_result.get("ok")),
        "approved_for_execution": False,
        "authority_mutation": False,
        "issues_auto_closed": False,
        "auto_promoted": False,
    }
