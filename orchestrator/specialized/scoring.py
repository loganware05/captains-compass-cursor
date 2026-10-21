"""Hermetic Level 0 scorers — retrieval / prompt / stub-student (no live models)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_GOLD_REL = Path("tests") / "fixtures" / "specialized-model-gold" / "tasks.json"

# Minimal prompt-bundle slots Level 0 expects before any LoRA.
_PROMPT_REQUIRED_SLOTS = ("objective", "evidence", "constraints", "output_format")


def default_gold_path(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / DEFAULT_GOLD_REL


def load_gold_set(path: Path) -> dict[str, Any]:
    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(f"gold set not found: {target}")
    doc = json.loads(target.read_text(encoding="utf-8"))
    tasks = list(doc.get("tasks") or [])
    if not tasks:
        raise ValueError(f"gold set has no tasks: {target}")
    return doc


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9_]{2,}", (text or "").lower())}


def score_retrieval(task: dict[str, Any]) -> bool:
    """Keyword hit-rate against fixture evidence snippets (hermetic)."""
    expected = [str(x).lower() for x in (task.get("expected_keywords") or [])]
    if not expected:
        return False
    corpus = " ".join(str(s) for s in (task.get("evidence_snippets") or []))
    corpus_l = corpus.lower()
    corpus_tokens = _tokenize(corpus)
    hits = sum(1 for kw in expected if kw in corpus_tokens or kw in corpus_l)
    need = max(1, (len(expected) + 1) // 2)
    return hits >= need


def score_prompt(task: dict[str, Any]) -> bool:
    """Prompt baseline: fixture prompt_bundle must cover required slots."""
    bundle = task.get("prompt_bundle") or {}
    if not isinstance(bundle, dict):
        return False
    for slot in _PROMPT_REQUIRED_SLOTS:
        val = bundle.get(slot)
        if not isinstance(val, str) or not val.strip():
            return False
    return True


def score_stub_student(task: dict[str, Any]) -> bool:
    """Hermetic stub student: canned answer must contain expected keywords."""
    answer = str(task.get("stub_student_answer") or "").lower()
    expected = [str(x).lower() for x in (task.get("expected_keywords") or [])]
    if not answer or not expected:
        return False
    hits = sum(1 for kw in expected if kw in answer)
    need = max(1, (len(expected) + 1) // 2)
    return hits >= need


def score_gold_set(gold: dict[str, Any]) -> dict[str, Any]:
    tasks = list(gold.get("tasks") or [])
    retrieval_passed = 0
    prompt_passed = 0
    stub_passed = 0
    misses: list[str] = []
    for task in tasks:
        tid = str(task.get("id") or "?")
        r_ok = score_retrieval(task)
        p_ok = score_prompt(task)
        s_ok = score_stub_student(task)
        if r_ok:
            retrieval_passed += 1
        else:
            misses.append(f"{tid}:retrieval")
        if p_ok:
            prompt_passed += 1
        else:
            misses.append(f"{tid}:prompt")
        if s_ok:
            stub_passed += 1
        else:
            misses.append(f"{tid}:stub")
    total = len(tasks)
    return {
        "retrieval_passed": retrieval_passed,
        "prompt_passed": prompt_passed,
        "stub_student_passed": stub_passed,
        "task_total": total,
        "retrieval_rate": round(retrieval_passed / total, 4) if total else None,
        "prompt_rate": round(prompt_passed / total, 4) if total else None,
        "stub_student_rate": round(stub_passed / total, 4) if total else None,
        "misses": misses[:24],
    }
