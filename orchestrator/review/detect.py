"""Detect review domains and load intent artifacts from a change set."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

DOMAIN_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("typescript", re.compile(r"\.(tsx?|cts|mts)$", re.I)),
    ("javascript", re.compile(r"\.(jsx?|cjs|mjs)$", re.I)),
    ("python", re.compile(r"\.(py|pyi)$", re.I)),
    ("react", re.compile(r"\.(tsx|jsx)$", re.I)),
    ("css", re.compile(r"\.(css|scss|sass)$", re.I)),
    ("sql", re.compile(r"\.(sql)$", re.I)),
    ("prisma", re.compile(r"schema\.prisma$", re.I)),
    ("github-actions", re.compile(r"\.github/workflows/", re.I)),
    ("docker", re.compile(r"(Dockerfile|docker-compose)", re.I)),
    ("security", re.compile(r"(auth|session|password|token|secret|permission)", re.I)),
    ("tests", re.compile(r"(^|/)(tests?|__tests__|spec)/|\.(test|spec)\.", re.I)),
    ("docs", re.compile(r"\.(md|mdx|rst)$", re.I)),
]


def parse_changed_paths_from_diff(diff_text: str) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:].strip()
            if path and path != "/dev/null" and path not in seen:
                seen.add(path)
                paths.append(path)
        elif line.startswith("diff --git "):
            # Fallback: "diff --git a/foo b/foo"
            parts = line.split()
            if len(parts) >= 4 and parts[3].startswith("b/"):
                path = parts[3][2:]
                if path and path not in seen:
                    seen.add(path)
                    paths.append(path)
    return paths


def detect_domains(paths: list[str]) -> list[str]:
    domains: set[str] = set()
    for path in paths:
        for name, pattern in DOMAIN_RULES:
            if pattern.search(path):
                domains.add(name)
    if not domains and paths:
        domains.add("general")
    return sorted(domains)


_AC_LINE = re.compile(
    r"^\s*(?:[-*]|\d+[.)])\s+(?:\[.\]\s*)?(.+)$",
)
_HEADING = re.compile(r"^#{1,6}\s+(.*)$")


def _extract_section_bullets(text: str, headings: tuple[str, ...]) -> list[str]:
    lines = text.splitlines()
    collecting = False
    items: list[str] = []
    for line in lines:
        heading = _HEADING.match(line)
        if heading:
            title = heading.group(1).strip().casefold()
            collecting = any(h in title for h in headings)
            continue
        if not collecting:
            continue
        if not line.strip():
            if items:
                # allow blank lines inside section
                continue
            continue
        m = _AC_LINE.match(line)
        if m:
            items.append(m.group(1).strip())
        elif line.startswith("#"):
            collecting = False
    return items


def load_intent(plan_path: Path | None) -> dict[str, Any]:
    if plan_path is None or not plan_path.is_file():
        return {
            "plan_path": None,
            "acceptance_criteria": [],
            "non_goals": [],
            "excerpt": "",
        }
    text = plan_path.read_text(encoding="utf-8", errors="replace")
    ac = _extract_section_bullets(
        text,
        ("acceptance criteria", "acceptance", "definition of done", "desired outcomes"),
    )
    non_goals = _extract_section_bullets(
        text,
        ("non-goals", "non goals", "deferred", "out of scope"),
    )
    excerpt = "\n".join(text.splitlines()[:80])
    return {
        "plan_path": str(plan_path),
        "acceptance_criteria": ac,
        "non_goals": non_goals,
        "excerpt": excerpt,
    }


def detect(
    *,
    repo_root: Path,
    changed_paths: list[str] | None = None,
    diff_text: str = "",
    plan_path: Path | None = None,
) -> dict[str, Any]:
    paths = list(changed_paths or [])
    if not paths and diff_text:
        paths = parse_changed_paths_from_diff(diff_text)
    domains = detect_domains(paths)
    intent = load_intent(plan_path)
    return {
        "repository": str(repo_root.resolve()),
        "changed_paths": paths,
        "domains": domains,
        "intent": intent,
        "skills_suggested": _skills_for_domains(domains),
    }


def _skills_for_domains(domains: list[str]) -> list[str]:
    skills = ["code-reviewer"]
    mapping = {
        "security": "security-review",
        "react": "accessibility-review",
        "css": "accessibility-review",
        "tests": "testing-validation",
        "python": "testing-validation",
        "typescript": "testing-validation",
        "javascript": "testing-validation",
    }
    for domain in domains:
        skill = mapping.get(domain)
        if skill and skill not in skills:
            skills.append(skill)
    if "security-review" not in skills and "security" not in domains:
        # Always keep security on the radar for API/auth-ish paths already handled;
        # adversarial review remains a default companion.
        pass
    if "review-fix-loop" not in skills:
        skills.append("review-fix-loop")
    return skills
