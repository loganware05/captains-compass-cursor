"""Parse Obsidian AI Exporter / ChatGPT markdown conversation exports."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TURN_SPLIT = re.compile(
    r"^##\s+.+$",
    re.MULTILINE,
)
_USER_BLOCK = re.compile(
    r">\s*\[!QUESTION\]\s*User\s*\n(?P<body>(?:>.*\n?)+)",
    re.IGNORECASE,
)
_ASSIST_BLOCK = re.compile(
    r">\s*\[!NOTE\]\s*ChatGPT\s*\n(?P<body>(?:>.*\n?)+)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedTurn:
    turn_index: int
    section_title: str
    user_prompt: str
    assistant_suggestion: str


@dataclass(frozen=True)
class ParsedConversation:
    conversation_id: str
    title: str
    source_url: str | None
    exported_at: str
    frontmatter: dict[str, str]
    turns: list[ParsedTurn]


class ConversationParseError(ValueError):
    """Raised when an export cannot be parsed into trajectories."""


def _strip_blockquote(body: str) -> str:
    lines: list[str] = []
    for raw in body.splitlines():
        line = raw
        if line.startswith(">"):
            line = line[1:]
            if line.startswith(" "):
                line = line[1:]
        lines.append(line)
    return "\n".join(lines).strip()


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            meta[key] = value
    return meta, text[match.end() :]


def parse_obsidian_chatgpt_export(text: str) -> ParsedConversation:
    """Parse Obsidian AI Exporter ChatGPT markdown into Q/A turns."""
    if not text or not text.strip():
        raise ConversationParseError("empty conversation export")
    meta, body = _parse_frontmatter(text)
    conversation_id = (
        meta.get("id")
        or meta.get("conversation_id")
        or "conversation-unknown"
    )
    title = meta.get("title") or "Untitled conversation"
    source_url = meta.get("url") or None
    exported_at = meta.get("modified") or meta.get("created") or "unknown"

    # Split on ## section headings while keeping headings.
    parts = _TURN_SPLIT.split(body)
    headings = _TURN_SPLIT.findall(body)
    turns: list[ParsedTurn] = []
    # Content before first heading may still contain turns.
    chunks: list[tuple[str, str]] = []
    if parts and parts[0].strip():
        chunks.append(("(preamble)", parts[0]))
    for idx, heading in enumerate(headings):
        section = parts[idx + 1] if idx + 1 < len(parts) else ""
        chunks.append((heading.lstrip("# ").strip(), section))

    for section_title, section in chunks:
        user_match = _USER_BLOCK.search(section)
        assist_match = _ASSIST_BLOCK.search(section)
        if not user_match or not assist_match:
            continue
        user_prompt = _strip_blockquote(user_match.group("body"))
        assistant = _strip_blockquote(assist_match.group("body"))
        if not user_prompt or not assistant:
            continue
        turns.append(
            ParsedTurn(
                turn_index=len(turns),
                section_title=section_title,
                user_prompt=user_prompt,
                assistant_suggestion=assistant,
            )
        )

    if not turns:
        raise ConversationParseError(
            "no User/ChatGPT callout turns found "
            "(expected [!QUESTION] User and [!NOTE] ChatGPT)"
        )

    return ParsedConversation(
        conversation_id=conversation_id,
        title=title,
        source_url=source_url,
        exported_at=exported_at,
        frontmatter=meta,
        turns=turns,
    )


def normalize_source(source: str) -> str:
    allowed = {"chatgpt", "obsidian-ai-exporter", "t3-attachment"}
    value = (source or "").strip().lower()
    if value not in allowed:
        raise ConversationParseError(
            f"unsupported source {source!r}; expected one of {sorted(allowed)}"
        )
    return value


def default_model_or_source(source: str, override: str | None) -> str:
    if override and override.strip():
        return override.strip()
    if source in {"chatgpt", "obsidian-ai-exporter"}:
        return "chatgpt"
    return source


def conversation_to_meta(parsed: ParsedConversation) -> dict[str, Any]:
    return {
        "conversation_id": parsed.conversation_id,
        "title": parsed.title,
        "source_url": parsed.source_url,
        "exported_at": parsed.exported_at,
        "turn_count": len(parsed.turns),
        "frontmatter": dict(parsed.frontmatter),
    }
