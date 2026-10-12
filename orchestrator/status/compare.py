"""Compare Project Overseer understanding across git SHAs (M51)."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from orchestrator.status.snapshot import build_snapshot


class StatusCompareError(ValueError):
    """Raised when compare fails closed."""


def _export_tree(repo_root: Path, sha: str, dest: Path) -> None:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "archive", sha],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise StatusCompareError(
            f"unable to archive sha {sha!r}: {(proc.stderr or b'').decode('utf-8', 'replace')}"
        )
    dest.mkdir(parents=True, exist_ok=True)
    untar = subprocess.run(
        ["tar", "-xf", "-", "-C", str(dest)],
        input=proc.stdout,
        capture_output=True,
        check=False,
    )
    if untar.returncode != 0:
        raise StatusCompareError(
            f"unable to extract archive for {sha!r}: "
            f"{(untar.stderr or b'').decode('utf-8', 'replace')}"
        )


def compare_since(repo_root: Path, since_sha: str) -> dict[str, Any]:
    if not since_sha.strip():
        raise StatusCompareError("--since SHA is required")
    current = build_snapshot(Path(repo_root), include_explanation=False)
    with tempfile.TemporaryDirectory(prefix="m51-compare-") as tmp:
        prior_root = Path(tmp) / "prior"
        _export_tree(Path(repo_root), since_sha.strip(), prior_root)
        prior = build_snapshot(prior_root, include_explanation=False)
        # Force prior sha label for clarity
        prior["repository_sha"] = since_sha.strip()

    cur_kinds = {f.get("kind") for f in (current.get("findings") or [])}
    prior_kinds = {f.get("kind") for f in (prior.get("findings") or [])}
    added = sorted(cur_kinds - prior_kinds)
    resolved = sorted(prior_kinds - cur_kinds)
    return {
        "status": "compared",
        "since": since_sha.strip(),
        "current": {
            "snapshot_id": current.get("snapshot_id"),
            "northstar_version": current.get("northstar_version"),
            "repository_sha": current.get("repository_sha"),
            "finding_count": len(current.get("findings") or []),
            "skill_count_fs": current.get("skill_count_fs"),
            "provenance_ref_count": len(current.get("provenance_refs") or []),
        },
        "prior": {
            "northstar_version": prior.get("northstar_version"),
            "repository_sha": prior.get("repository_sha"),
            "finding_count": len(prior.get("findings") or []),
            "skill_count_fs": prior.get("skill_count_fs"),
            "provenance_ref_count": len(prior.get("provenance_refs") or []),
        },
        "added_finding_kinds": added,
        "resolved_finding_kinds": resolved,
        "provenance_refs": list(current.get("provenance_refs") or []),
        "approved_for_execution": False,
        "authority_mutation": False,
    }
