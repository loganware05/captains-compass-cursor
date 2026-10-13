"""Read-only local Git fact collectors for Cognitive Core C1."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(repo_root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def git_sha(repo_root: Path) -> str:
    return _run_git(repo_root, "rev-parse", "HEAD")


def git_branch(repo_root: Path) -> str:
    return _run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")


def working_tree_dirty(repo_root: Path) -> bool:
    """True when there are unstaged, staged, or untracked changes."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    if proc.returncode != 0:
        return False
    return bool((proc.stdout or "").strip())
