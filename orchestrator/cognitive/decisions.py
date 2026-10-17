"""Extract Decision/ADR links from DECISIONS.md for C2 context (read-only)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from orchestrator.knowledge.index import tokenize

_ADR_HEADING = re.compile(r"^##\s+(ADR-\d+:\s*.+)$", re.MULTILINE)


def load_decision_entries(repo_root: Path) -> list[dict[str, Any]]:
    """Parse ADR headings from DECISIONS.md without mutating the knowledge store."""
    path = Path(repo_root) / "DECISIONS.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    matches = list(_ADR_HEADING.finditer(text))
    entries: list[dict[str, Any]] = []
    for idx, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        summary = body.split("\n\n")[0].strip() if body else heading
        summary = summary[:2000] if summary else heading
        adr_id = heading.split(":")[0].strip().lower().replace(" ", "-")
        entries.append(
            {
                "adr_id": adr_id,
                "title": heading,
                "summary": summary,
                "source_path": "DECISIONS.md",
                "body": body,
            }
        )
    return entries


def rank_decision_links(
    repo_root: Path,
    query: str,
    *,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """Return query-relevant ADR links with documented claim_kind."""
    query_tokens = set(tokenize(query))
    ranked: list[tuple[float, dict[str, Any]]] = []
    for entry in load_decision_entries(repo_root):
        blob = " ".join(
            [
                entry["adr_id"],
                entry["title"],
                entry.get("summary") or "",
                entry.get("body") or "",
            ]
        )
        item_tokens = set(tokenize(blob))
        if not query_tokens or not item_tokens:
            score = 0.0
        else:
            overlap = len(query_tokens & item_tokens)
            score = overlap / len(query_tokens) if overlap else 0.0
        if score <= 0:
            # Keep ADR id / title exact-ish matches even with light overlap
            lower_q = query.lower()
            if entry["adr_id"] in lower_q or entry["title"].lower() in lower_q:
                score = 0.5
            else:
                continue
        ranked.append(
            (
                score,
                {
                    "adr_id": entry["adr_id"],
                    "title": entry["title"],
                    "source_path": entry["source_path"],
                    "score": round(score, 4),
                    "claim_kind": "documented",
                },
            )
        )
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["adr_id"]))
    return [item for _, item in ranked[:top_n]]
