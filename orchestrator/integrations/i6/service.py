"""I6 hermetic cross-provider validation for I1–I5."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from orchestrator.integrations.i6.gates import require_i6_enabled

CONTROL = Path(__file__).resolve().parents[3]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _scorecard_id(blob: str) -> str:
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]
    return f"i6-score-{digest}"


def _load_schema(repo_root: Path) -> dict[str, Any]:
    path = (
        Path(repo_root)
        / "orchestrator"
        / "schemas"
        / "i6-cross-provider-scorecard.schema.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_scorecard(repo_root: Path, doc: dict[str, Any]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        for key in (
            "approved_for_execution",
            "authority_mutation",
            "auto_promoted",
        ):
            if doc.get(key) is not False:
                raise ValueError(f"{key} must be false")
        return
    jsonschema.validate(instance=doc, schema=_load_schema(repo_root))


@contextmanager
def _cleared_env(*names: str) -> Iterator[None]:
    saved = {n: os.environ.pop(n, None) for n in names}
    try:
        yield
    finally:
        for n, v in saved.items():
            if v is None:
                os.environ.pop(n, None)
            else:
                os.environ[n] = v


@contextmanager
def _set_env(pairs: dict[str, str]) -> Iterator[None]:
    saved = {k: os.environ.get(k) for k in pairs}
    os.environ.update(pairs)
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _check_fail_closed(require_fn: Any, *gate_names: str) -> tuple[bool, str]:
    with _cleared_env(*gate_names):
        try:
            require_fn()
            return False, "expected PermissionError when gate unset"
        except PermissionError as exc:
            return True, str(exc)[:200]


def _probe_sentry(tmp: Path) -> tuple[bool, str]:
    from orchestrator.integrations.sentry import service as sentry_service
    from orchestrator.integrations.sentry.enabled import require_sentry_ingest_enabled

    ok_fc, detail_fc = _check_fail_closed(
        require_sentry_ingest_enabled, "COMPASS_SENTRY_INGEST_ENABLED"
    )
    if not ok_fc:
        return False, detail_fc
    with _set_env({"COMPASS_SENTRY_INGEST_ENABLED": "1"}):
        result = sentry_service.fetch_incidents(tmp)
    if result.get("status") != "fetched" or int(result.get("count") or 0) < 1:
        return False, f"sentry fixture fetch unexpected: {result.get('status')}"
    return True, "fail-closed + fixture fetch ok"


def _probe_t3(tmp: Path) -> tuple[bool, str]:
    from orchestrator.integrations.t3 import service as t3_service
    from orchestrator.integrations.t3.enabled import require_t3_exec_enabled

    ok_fc, detail_fc = _check_fail_closed(
        require_t3_exec_enabled, "COMPASS_T3_EXEC_ENABLED"
    )
    if not ok_fc:
        return False, detail_fc
    with _set_env({"COMPASS_T3_EXEC_ENABLED": "1"}):
        caps = t3_service.list_capabilities()
        started = t3_service.start_execution(
            tmp,
            plan_id="i6-cross-provider-validation",
            objective="hermetic i6 probe",
            allow_fixture_plan=True,
        )
    if not isinstance(caps, dict):
        return False, "t3 capabilities unexpected"
    exec_doc = started.get("execution") if isinstance(started.get("execution"), dict) else {}
    if not exec_doc.get("execution_id"):
        return False, f"t3 start missing execution_id: {list(started.keys())}"
    return True, "fail-closed + fixture capabilities/start ok"


def _probe_apify(tmp: Path) -> tuple[bool, str]:
    from orchestrator.integrations.apify import service as apify_service
    from orchestrator.providers.technology_intelligence.apify_gates import (
        require_apify_enabled,
    )

    ok_fc, detail_fc = _check_fail_closed(
        require_apify_enabled, "COMPASS_APIFY_ENABLED"
    )
    if not ok_fc:
        return False, detail_fc
    # Copy schema for validation
    schema_src = CONTROL / "orchestrator/schemas/apify-research-packet.schema.json"
    schema_dst = tmp / "orchestrator" / "schemas"
    schema_dst.mkdir(parents=True, exist_ok=True)
    schema_dst.joinpath("apify-research-packet.schema.json").write_text(
        schema_src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    with _set_env({"COMPASS_APIFY_ENABLED": "1"}):
        result = apify_service.search(tmp, "web research")
    if not (result.get("packet") or {}).get("packet_id"):
        return False, "apify search missing packet"
    return True, "fail-closed + fixture search ok"


def _probe_explain(tmp: Path) -> tuple[bool, str]:
    from orchestrator.integrations.scrimba import service as explain_service
    from orchestrator.integrations.scrimba.gates import require_explain_enabled

    ok_fc, detail_fc = _check_fail_closed(
        require_explain_enabled, "COMPASS_EXPLAIN_ENABLED"
    )
    if not ok_fc:
        return False, detail_fc
    schema_src = CONTROL / "orchestrator/schemas/scrimba-explainer-packet.schema.json"
    schema_dst = tmp / "orchestrator" / "schemas"
    schema_dst.mkdir(parents=True, exist_ok=True)
    schema_dst.joinpath("scrimba-explainer-packet.schema.json").write_text(
        schema_src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    with _set_env({"COMPASS_EXPLAIN_ENABLED": "1"}):
        result = explain_service.create(tmp, "I6 hermetic explainer probe")
    if not (result.get("packet") or {}).get("packet_id"):
        return False, "explain create missing packet"
    return True, "fail-closed + fixture create ok"


def _probe_identity(tmp: Path) -> tuple[bool, str]:
    from orchestrator.integrations.workos import service as identity_service
    from orchestrator.integrations.workos.gates import require_identity_enabled

    ok_fc, detail_fc = _check_fail_closed(
        require_identity_enabled,
        "COMPASS_IDENTITY_ENABLED",
        "COMPASS_WORKOS_ENABLED",
    )
    if not ok_fc:
        return False, detail_fc
    schema_src = CONTROL / "orchestrator/schemas/workos-identity-packet.schema.json"
    schema_dst = tmp / "orchestrator" / "schemas"
    schema_dst.mkdir(parents=True, exist_ok=True)
    schema_dst.joinpath("workos-identity-packet.schema.json").write_text(
        schema_src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    with _set_env({"COMPASS_IDENTITY_ENABLED": "1"}):
        result = identity_service.sync(tmp)
    packet = result.get("packet") or {}
    if packet.get("grants_captain_approval") is not False:
        return False, "identity must lock grants_captain_approval false"
    if not packet.get("packet_id"):
        return False, "identity sync missing packet"
    return True, "fail-closed + fixture sync ok"


def _run_probes() -> list[dict[str, Any]]:
    probes = [
        ("I1", "sentry", _probe_sentry),
        ("I2", "t3", _probe_t3),
        ("I3", "apify", _probe_apify),
        ("I4", "scrimba-explain", _probe_explain),
        ("I5", "workos-identity", _probe_identity),
    ]
    rows: list[dict[str, Any]] = []
    for pid, name, fn in probes:
        with tempfile.TemporaryDirectory(prefix=f"i6-{pid.lower()}-") as tmp:
            try:
                fixture_ok, detail = fn(Path(tmp))
                # fail_closed is embedded in each probe; treat overall as both
                fail_closed = fixture_ok or "fail-closed" in detail.lower()
                # Re-derive: probes return False only on failure of either check
                status = "pass" if fixture_ok else "fail"
                rows.append(
                    {
                        "id": pid,
                        "name": name,
                        "fail_closed": fail_closed if fixture_ok else False,
                        "fixture_ok": fixture_ok,
                        "status": status,
                        "detail": detail,
                    }
                )
            except Exception as exc:  # noqa: BLE001 — harness must record failures
                rows.append(
                    {
                        "id": pid,
                        "name": name,
                        "fail_closed": False,
                        "fixture_ok": False,
                        "status": "fail",
                        "detail": f"{type(exc).__name__}: {exc}"[:300],
                    }
                )
    # Fix fail_closed flag: when pass, both checks succeeded
    for row in rows:
        if row["status"] == "pass":
            row["fail_closed"] = True
            row["fixture_ok"] = True
    return rows


def run(
    repo_root: Path,
    *,
    write_evidence: bool = True,
) -> dict[str, Any]:
    """Run hermetic I1–I5 probes and optionally persist a scorecard."""
    require_i6_enabled()
    repo_root = Path(repo_root)
    providers = _run_probes()
    passed = sum(1 for p in providers if p["status"] == "pass")
    failed = sum(1 for p in providers if p["status"] == "fail")
    created = _utc_now()
    scorecard = {
        "schema_version": "1",
        "scorecard_id": _scorecard_id(f"{created}:{passed}:{failed}"),
        "provider": "i6",
        "mode": "hermetic",
        "created_at": created,
        "providers": providers,
        "passed": passed,
        "failed": failed,
        "approved_for_execution": False,
        "authority_mutation": False,
        "auto_promoted": False,
        "notes": (
            "Hermetic I1–I5 cross-provider validation — NOT AUTHORITY. "
            "Live provider probes deferred."
        ),
    }
    _validate_scorecard(repo_root, scorecard)
    path = None
    if write_evidence:
        out_dir = repo_root / ".agent" / "evidence" / "i6-cross-provider"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{scorecard['scorecard_id']}.json"
        path.write_text(
            json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return {
        "status": "ok" if failed == 0 else "failed",
        "path": str(path) if path else "",
        "scorecard": scorecard,
    }
