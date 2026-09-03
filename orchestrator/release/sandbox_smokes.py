"""Sandbox release smoke catalog, runner, and closeout validation (M18)."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SMOKE_REPORT_KIND = "sandbox-release-smoke-report"
INTERACTIVE_REPORT_KIND = "sandbox-interactive-smoke-report"


class SandboxSmokeError(ValueError):
    """Raised when sandbox release smoke validation fails."""


@dataclass(frozen=True)
class SmokeStep:
    smoke_id: str
    label: str
    mode: str  # automated | interactive
    checklist_item: int | None = None


RELEASE_SMOKE_CATALOG: tuple[SmokeStep, ...] = (
    SmokeStep("doctor-sandbox", "Doctor on sandbox path", "automated"),
    SmokeStep("compass-version", "Sandbox COMPASS_VERSION matches control", "automated"),
    SmokeStep("behavioral-checklist-present", "Behavioral checklist document present", "automated"),
    SmokeStep("knowledge-ingest-fixtures", "Knowledge ingest fixtures CLI", "automated"),
    SmokeStep("pgvector-mock-query", "Mock pgvector knowledge query", "automated"),
    SmokeStep("stars-categorize-fixtures", "Stars categorization fixtures CLI", "automated"),
    SmokeStep("skill-learning-loop-fixtures", "Skill learning loop fixtures CLI", "automated"),
    SmokeStep("notion-live-fixtures", "Notion live ingest fixtures CLI", "automated"),
    SmokeStep("hf-file-ti", "Hugging Face file TI query", "automated"),
    SmokeStep("context-selection-propose", "Context selection proposal CLI", "automated"),
    SmokeStep("approval-gate", "Approval gate stops before product edits", "interactive", 1),
    SmokeStep("no-implement-draft", "No implement on DRAFT plan", "interactive", 2),
    SmokeStep("no-weaken-tests", "Refuse to weaken failing tests", "interactive", 3),
    SmokeStep("evidence-capture", "Validation evidence under .agent/evidence/", "interactive", 4),
    SmokeStep("budget-stop", "Budget stop report when limit hit", "interactive", 5),
    SmokeStep("phase-commands", "/plan-feature and /implement-approved-plan", "interactive", 6),
    SmokeStep("capability-plan", "Capability-aware /plan-feature sections", "interactive", 7),
    SmokeStep("post-foundation-smokes", "Post-foundation fixture smokes (M13–M17)", "interactive", 8),
    SmokeStep("skill-learning-loop", "Skill learning loop drafts + improvement proposals", "interactive", 9),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_version(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _run_script(control_root: Path, script: str, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    merged["PYTHONPATH"] = str(control_root) + (
        f":{merged['PYTHONPATH']}" if merged.get("PYTHONPATH") else ""
    )
    cmd = [str(control_root / "scripts" / script), *args]
    return subprocess.run(
        cmd,
        cwd=str(control_root),
        env=merged,
        capture_output=True,
        text=True,
        check=False,
    )


def _step_doctor_sandbox(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    proc = _run_script(control_root, "doctor.sh", str(sandbox_root))
    return {
        "smoke_id": "doctor-sandbox",
        "passed": proc.returncode == 0,
        "detail": proc.stdout[-500:] if proc.stdout else proc.stderr[-500:],
    }


def _step_compass_version(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    control_v = _read_version(control_root / "VERSION")
    sandbox_path = sandbox_root / ".agent" / "COMPASS_VERSION"
    if not sandbox_path.is_file():
        return {"smoke_id": "compass-version", "passed": False, "detail": "missing COMPASS_VERSION"}
    sandbox_v = _read_version(sandbox_path)
    return {
        "smoke_id": "compass-version",
        "passed": control_v == sandbox_v,
        "detail": f"control={control_v} sandbox={sandbox_v}",
    }


def _step_behavioral_checklist(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    del sandbox_root
    path = control_root / "docs" / "evals" / "SANDBOX_BEHAVIORAL_CHECKLIST.md"
    return {
        "smoke_id": "behavioral-checklist-present",
        "passed": path.is_file() and "Post-foundation" in path.read_text(encoding="utf-8"),
        "detail": str(path),
    }


def _step_knowledge_ingest(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    del sandbox_root
    proc = _run_script(
        control_root,
        "ingest-knowledge.sh",
        "--from-store",
        "procedures",
        "--repo-root",
        str(control_root),
    )
    return {
        "smoke_id": "knowledge-ingest-fixtures",
        "passed": proc.returncode == 0,
        "detail": proc.stdout[:300] or proc.stderr[:300],
    }


def _step_pgvector_mock(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    del sandbox_root
    env = {"COMPASS_VECTOR_PROVIDER": "mock", "COMPASS_VECTOR_NAMESPACE": "release-smoke"}
    proc = _run_script(
        control_root,
        "query-knowledge.sh",
        "--query",
        "matcher routing",
        "--mode",
        "vector",
        env=env,
    )
    return {
        "smoke_id": "pgvector-mock-query",
        "passed": proc.returncode == 0,
        "detail": proc.stdout[:300] or proc.stderr[:300],
    }


def _step_stars_categorize(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    del sandbox_root
    proc = _run_script(
        control_root,
        "categorize-github-stars.sh",
        "--source",
        "fixtures",
        "--repo-root",
        str(control_root),
    )
    return {
        "smoke_id": "stars-categorize-fixtures",
        "passed": proc.returncode == 0,
        "detail": proc.stdout[:300] or proc.stderr[:300],
    }


def _step_skill_learning_loop(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    del sandbox_root
    proc = _run_script(
        control_root,
        "run-skill-learning-loop.sh",
        "--source",
        "fixtures",
        "--objective",
        "accessible react forms",
        "--top",
        "1",
        "--repo-root",
        str(control_root),
    )
    passed = proc.returncode == 0 and "skill-learning-run" in proc.stdout
    return {
        "smoke_id": "skill-learning-loop-fixtures",
        "passed": passed,
        "detail": proc.stdout[:300] or proc.stderr[:300],
    }


def _step_notion_live(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    del sandbox_root
    try:
        from orchestrator.knowledge.notion_live import NotionLiveError, ingest_notion_live_pages

        allowlist = control_root / "tests" / "fixtures" / "knowledge" / "notion-allowlist.txt"
        result = ingest_notion_live_pages(
            control_root,
            source="fixtures",
            allowlist_path=allowlist,
        )
        passed = bool(result.get("items"))
        detail = json.dumps({"count": len(result.get("items") or [])})
    except NotionLiveError as exc:
        passed = False
        detail = str(exc)
    except Exception as exc:  # pragma: no cover - defensive for subprocess parity
        passed = False
        detail = str(exc)
    return {
        "smoke_id": "notion-live-fixtures",
        "passed": passed,
        "detail": detail,
    }


def _step_hf_file_ti(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    del sandbox_root
    proc = _run_script(
        control_root,
        "query-technology-intelligence.sh",
        "--query",
        "sentence embeddings",
        "--provider",
        "huggingface-file",
    )
    return {
        "smoke_id": "hf-file-ti",
        "passed": proc.returncode == 0 and '"candidates"' in proc.stdout,
        "detail": proc.stdout[:300] or proc.stderr[:300],
    }


def _step_context_selection(control_root: Path, sandbox_root: Path) -> dict[str, Any]:
    del sandbox_root
    fixture = control_root / "tests" / "fixtures" / "experience" / "contact-counter.json"
    proc = _run_script(
        control_root,
        "propose-context-selection.sh",
        "--experiences",
        str(fixture),
        "--repo-root",
        str(control_root),
    )
    return {
        "smoke_id": "context-selection-propose",
        "passed": proc.returncode == 0 and "proposal" in proc.stdout,
        "detail": proc.stdout[:300] or proc.stderr[:300],
    }


AUTOMATED_STEPS: dict[str, Callable[[Path, Path], dict[str, Any]]] = {
    "doctor-sandbox": _step_doctor_sandbox,
    "compass-version": _step_compass_version,
    "behavioral-checklist-present": _step_behavioral_checklist,
    "knowledge-ingest-fixtures": _step_knowledge_ingest,
    "pgvector-mock-query": _step_pgvector_mock,
    "stars-categorize-fixtures": _step_stars_categorize,
    "skill-learning-loop-fixtures": _step_skill_learning_loop,
    "notion-live-fixtures": _step_notion_live,
    "hf-file-ti": _step_hf_file_ti,
    "context-selection-propose": _step_context_selection,
}


def run_automated_sandbox_smokes(
    control_root: Path,
    sandbox_root: Path,
    *,
    steps: dict[str, Callable[[Path, Path], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Run deterministic release smokes (no LLM)."""
    control_root = Path(control_root).resolve()
    sandbox_root = Path(sandbox_root).resolve()
    runners = steps or AUTOMATED_STEPS
    results: list[dict[str, Any]] = []
    for step in RELEASE_SMOKE_CATALOG:
        if step.mode != "automated":
            continue
        runner = runners.get(step.smoke_id)
        if runner is None:
            results.append({"smoke_id": step.smoke_id, "passed": False, "detail": "no runner"})
            continue
        results.append(runner(control_root, sandbox_root))
    passed = all(r.get("passed") for r in results)
    return {
        "kind": SMOKE_REPORT_KIND,
        "ran_at": _utc_now(),
        "control_root": str(control_root),
        "sandbox_root": str(sandbox_root),
        "passed": passed,
        "results": results,
    }


def write_smoke_report(report: dict[str, Any], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def interactive_smoke_catalog() -> list[dict[str, Any]]:
    return [
        {
            "smoke_id": step.smoke_id,
            "label": step.label,
            "checklist_item": step.checklist_item,
        }
        for step in RELEASE_SMOKE_CATALOG
        if step.mode == "interactive"
    ]


def validate_release_smoke_evidence(
    control_root: Path,
    version: str,
    *,
    require_interactive: bool = True,
) -> dict[str, Any]:
    """Validate automated + interactive smoke evidence for release closeout."""
    control_root = Path(control_root)
    version = version.lstrip("v")
    evidence_dir = control_root / ".agent" / "evidence" / f"release-v{version}"
    automated_path = evidence_dir / "sandbox-smokes-automated.json"
    interactive_path = evidence_dir / "sandbox-smokes-interactive.json"

    if not automated_path.is_file():
        raise SandboxSmokeError(f"missing automated smoke evidence: {automated_path}")

    with automated_path.open(encoding="utf-8") as handle:
        automated = json.load(handle)
    if not isinstance(automated, dict) or not automated.get("passed"):
        raise SandboxSmokeError("automated sandbox smokes did not pass")
    
    if automated.get("kind") != SMOKE_REPORT_KIND:
        raise SandboxSmokeError(f"automated report has wrong kind: expected {SMOKE_REPORT_KIND}")
    
    results = automated.get("results")
    if not isinstance(results, list) or not results:
        raise SandboxSmokeError("automated report missing results")
    
    expected_automated = {step.smoke_id for step in RELEASE_SMOKE_CATALOG if step.mode == "automated"}
    actual_automated = {r.get("smoke_id") for r in results if isinstance(r, dict)}
    missing_automated = expected_automated - actual_automated
    if missing_automated:
        raise SandboxSmokeError(f"automated report missing smokes: {sorted(missing_automated)}")
    
    failed_automated = [r.get("smoke_id") for r in results if isinstance(r, dict) and not r.get("passed")]
    if failed_automated:
        raise SandboxSmokeError(f"automated smokes failed: {failed_automated}")

    interactive: dict[str, Any] | None = None
    if require_interactive:
        if not interactive_path.is_file():
            raise SandboxSmokeError(f"missing interactive smoke evidence: {interactive_path}")
        with interactive_path.open(encoding="utf-8") as handle:
            interactive = json.load(handle)
        if not isinstance(interactive, dict) or not interactive.get("passed"):
            raise SandboxSmokeError("interactive sandbox smokes not marked passed")
        
        if interactive.get("kind") != INTERACTIVE_REPORT_KIND:
            raise SandboxSmokeError(f"interactive report has wrong kind: expected {INTERACTIVE_REPORT_KIND}")
        
        items = interactive.get("checklist_results")
        if not isinstance(items, list) or not items:
            raise SandboxSmokeError("interactive report missing checklist_results")
        
        expected_items = {step.checklist_item for step in RELEASE_SMOKE_CATALOG if step.mode == "interactive" and step.checklist_item is not None}
        actual_items = {item.get("item") for item in items if isinstance(item, dict)}
        missing_items = expected_items - actual_items
        if missing_items:
            raise SandboxSmokeError(f"interactive report missing checklist items: {sorted(missing_items)}")
        
        failed_items = [item.get("item") for item in items if isinstance(item, dict) and not item.get("passed")]
        if failed_items:
            raise SandboxSmokeError(f"interactive checklist items failed: {sorted(failed_items)}")

    return {
        "version": version,
        "automated_path": str(automated_path),
        "interactive_path": str(interactive_path) if interactive_path.is_file() else None,
        "passed": True,
    }


def default_sandbox_path() -> Path:
    return Path(
        os.environ.get(
            "COMPASS_SANDBOX_PATH",
            "/Users/loganware/Documents/Personal/Code/captain-compass-sandbox",
        )
    ).expanduser()
