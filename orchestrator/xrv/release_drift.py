"""Release / document consistency checks (VERSION ↔ README)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

README_VERSION_RE = re.compile(
    r"(?im)^\s*(?:#{1,3}\s*)?(?:current\s+version|version)\s*:\s*v?([0-9]+(?:\.[0-9]+){1,3})\s*$"
)


def read_version_file(repo_root: Path) -> str:
    path = Path(repo_root) / "VERSION"
    if not path.is_file():
        raise FileNotFoundError(f"VERSION missing at {path}")
    return path.read_text(encoding="utf-8").strip()


def extract_readme_version(readme_text: str) -> str | None:
    match = README_VERSION_RE.search(readme_text)
    if not match:
        return None
    return match.group(1)


def check_release_document_drift(repo_root: Path) -> dict[str, Any]:
    """
    Compare VERSION file to README current-version line.

    Returns a structured report. ``ok`` is True when versions match.
    Does not grant authority and never auto-closes issues.
    """
    root = Path(repo_root)
    version = read_version_file(root)
    readme_path = root / "README.md"
    if not readme_path.is_file():
        return {
            "ok": False,
            "version": version,
            "readme_version": None,
            "findings": ["README.md missing"],
            "approved_for_execution": False,
            "authority_mutation": False,
            "issues_auto_closed": False,
        }
    readme_version = extract_readme_version(readme_path.read_text(encoding="utf-8"))
    findings: list[str] = []
    if readme_version is None:
        findings.append(
            "README.md has no 'Current version:' / 'Version:' line to compare"
        )
    elif readme_version != version:
        findings.append(
            f"VERSION={version} does not match README version={readme_version}"
        )
    return {
        "ok": len(findings) == 0,
        "version": version,
        "readme_version": readme_version,
        "findings": findings,
        "approved_for_execution": False,
        "authority_mutation": False,
        "issues_auto_closed": False,
    }
