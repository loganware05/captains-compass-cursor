"""Multi-repo XRV readiness portfolio (W3)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.xrv.readiness import Profile, assess_readiness, resolve_control_root
from orchestrator.xrv.readiness_gates import require_xrv_readiness_enabled


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_portfolio(control_root: Path, doc: dict[str, Any]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        for key in (
            "approved_for_execution",
            "authority_mutation",
            "auto_promoted",
            "scores_invented",
        ):
            if doc.get(key) is not False:
                raise ValueError(f"{key} must be false")
        return
    schema = json.loads(
        (
            Path(control_root)
            / "orchestrator"
            / "schemas"
            / "xrv-portfolio-scorecard.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=doc, schema=schema)


def assess_portfolio(
    entries: list[tuple[str, Path, Profile | None]],
    *,
    require_gate: bool = True,
    write_evidence: bool = True,
    control_root: Path | None = None,
) -> dict[str, Any]:
    """Assess multiple repos and emit a portfolio scorecard under the control repo."""
    if require_gate:
        require_xrv_readiness_enabled()
    ctrl = resolve_control_root(control_root)
    rows: list[dict[str, Any]] = []
    per_repo: list[dict[str, Any]] = []
    for label, repo_path, profile in entries:
        result = assess_readiness(
            Path(repo_path),
            require_gate=False,
            write_evidence=False,
            profile=profile,
            control_root=ctrl,
        )
        sc = result["scorecard"]
        rows.append(
            {
                "label": label,
                "repo_path": str(Path(repo_path)),
                "profile": sc.get("profile") or result.get("profile"),
                "repository_sha": sc.get("repository_sha"),
                "readiness_status": sc["repository_readiness"]["overall_status"],
                "readiness_score": sc["repository_readiness"]["overall_score"],
                "effectiveness_status": sc["northstar_effectiveness"]["overall_status"],
                "effectiveness_score": sc["northstar_effectiveness"]["overall_score"],
                "scorecard_id": sc["scorecard_id"],
            }
        )
        per_repo.append(sc)
    blob = json.dumps({"rows": rows}, sort_keys=True)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]
    portfolio = {
        "schema_version": "xrv-portfolio-1",
        "portfolio_id": f"xrv-port-{digest}",
        "created_at": _utc_now(),
        "summary": (
            f"{len(rows)} repos assessed; "
            + ", ".join(
                f"{r['label']}={r['readiness_status']}/{r['effectiveness_status']}"
                for r in rows
            )
        ),
        "repos": rows,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "scores_invented": False,
    }
    _validate_portfolio(ctrl, portfolio)
    result: dict[str, Any] = {
        "status": "ok",
        "portfolio": portfolio,
        "scorecards": per_repo,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "scores_invented": False,
    }
    if write_evidence:
        out_dir = ctrl / ".agent" / "evidence" / "xrv-portfolio"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{portfolio['portfolio_id']}.json"
        out_path.write_text(
            json.dumps(portfolio, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result["path"] = str(out_path)
    return result
