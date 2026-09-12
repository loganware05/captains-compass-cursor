"""Verify and rank candidate review findings."""

from __future__ import annotations

from typing import Any

DEFAULT_MIN_CONFIDENCE = 0.55
_SEVERITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}


def _normalize_finding(raw: dict[str, Any], index: int) -> dict[str, Any]:
    evidence = raw.get("evidence_paths") or raw.get("evidence") or []
    if isinstance(evidence, str):
        evidence = [evidence]
    evidence_paths = [str(p) for p in evidence if str(p).strip()]
    confidence = raw.get("confidence", 0.0)
    try:
        confidence_f = float(confidence)
    except (TypeError, ValueError):
        confidence_f = 0.0
    severity = str(raw.get("severity") or "info").lower()
    if severity not in _SEVERITY_RANK:
        severity = "info"
    return {
        "id": str(raw.get("id") or f"finding-{index:03d}"),
        "title": str(raw.get("title") or "Untitled finding").strip() or "Untitled finding",
        "detail": str(raw.get("detail") or raw.get("description") or ""),
        "severity": severity,
        "confidence": max(0.0, min(1.0, confidence_f)),
        "skill": str(raw.get("skill") or raw.get("source_skill") or "code-reviewer"),
        "category": str(raw.get("category") or "general"),
        "evidence_paths": evidence_paths,
        "suggested_fix": str(raw.get("suggested_fix") or ""),
        "status": "unverified",
    }


def verify_findings(
    candidates: list[dict[str, Any]],
    *,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    require_evidence: bool = True,
) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    for index, raw in enumerate(candidates):
        if not isinstance(raw, dict):
            continue
        finding = _normalize_finding(raw, index)
        if require_evidence and not finding["evidence_paths"]:
            finding["status"] = "discarded"
            finding["discard_reason"] = "missing_evidence_paths"
        elif finding["confidence"] < min_confidence:
            finding["status"] = "discarded"
            finding["discard_reason"] = (
                f"confidence_below_threshold:{min_confidence}"
            )
        elif finding["confidence"] < 0.75:
            finding["status"] = "unverified"
            finding["discard_reason"] = ""
        else:
            finding["status"] = "verified"
            finding["discard_reason"] = ""
        verified.append(finding)

    verified.sort(
        key=lambda f: (
            0 if f["status"] == "verified" else 1 if f["status"] == "unverified" else 2,
            _SEVERITY_RANK.get(f["severity"], 9),
            -float(f["confidence"]),
            f["id"],
        )
    )
    return verified
