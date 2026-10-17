"""Compose C2 memory/retrieval context from project-state + knowledge + ADRs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.cognitive.decisions import rank_decision_links
from orchestrator.cognitive.enabled import require_brain_enabled
from orchestrator.cognitive.git_facts import git_sha
from orchestrator.cognitive.store import BrainStoreError, load_latest
from orchestrator.knowledge.query import query_knowledge
from orchestrator.schemas.validate import validate_document


def _freshness_for(repo_root: Path, snapshot: dict[str, Any] | None) -> str:
    if snapshot is None:
        return "no_snapshot"
    current = git_sha(repo_root)
    recorded = str(snapshot.get("repository_sha") or "")
    if current and recorded and current == recorded:
        return "fresh"
    return "stale"


def _normalize_mode(mode: str) -> str:
    normalized = (mode or "hybrid").strip().lower()
    if normalized not in {"hybrid", "keyword", "vector"}:
        raise ValueError("--mode must be hybrid, keyword, or vector")
    return normalized


def _item_source_path(item: dict[str, Any]) -> str:
    artifact = item.get("source_artifact") or {}
    if isinstance(artifact, dict) and artifact.get("path"):
        return str(artifact["path"])
    return str(item.get("source_path") or "")


def _slim_hit(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": str(item.get("item_id") or ""),
        "kind": str(item.get("kind") or ""),
        "title": str(item.get("title") or ""),
        "summary": str(item.get("summary") or "")[:2000],
        "source_path": _item_source_path(item),
        "query_score": float(item.get("query_score") or 0.0),
        "search_mode": str(item.get("search_mode") or ""),
        "keyword_score": item.get("keyword_score"),
        "vector_score": item.get("vector_score"),
        "vector_backend": item.get("vector_backend"),
        "search_fallback": item.get("search_fallback"),
    }


def build_context(
    repo_root: Path,
    query: str,
    *,
    mode: str = "hybrid",
    top_n: int = 10,
) -> dict[str, Any]:
    """Return schema-validated brain context for a query (read-oriented)."""
    require_brain_enabled()
    repo_root = Path(repo_root)
    q = (query or "").strip()
    if not q:
        raise ValueError("--query is required for brain context")
    if top_n < 1:
        top_n = 1
    if top_n > 50:
        top_n = 50

    normalized_mode = _normalize_mode(mode)
    try:
        snapshot = load_latest(repo_root)
    except BrainStoreError as exc:
        raise ValueError(str(exc)) from exc

    freshness = _freshness_for(repo_root, snapshot)
    head_sha = git_sha(repo_root)
    snapshot_sha = str((snapshot or {}).get("repository_sha") or "")
    snapshot_id = str((snapshot or {}).get("snapshot_id") or "") or None
    version = str((snapshot or {}).get("northstar_version") or "")

    # Read-only: do not rebuild/write knowledge indexes during context.
    raw_hits = query_knowledge(
        repo_root,
        q,
        top_n=top_n,
        mode=normalized_mode,
        rebuild_index=False,
    )
    hits = [_slim_hit(item) for item in raw_hits]

    # Prefer knowledge decision hits; always enrich with live DECISIONS.md ranks.
    decision_links = rank_decision_links(repo_root, q, top_n=min(5, top_n))
    seen_adr = {d["adr_id"] for d in decision_links}
    for hit in hits:
        if hit.get("kind") != "decision":
            continue
        title = hit.get("title") or ""
        adr_guess = title.split(":")[0].strip().lower().replace(" ", "-")
        if not adr_guess.startswith("adr-"):
            # Fall back to source_path / item_id heuristics from ingest
            item_id = str(hit.get("item_id") or "")
            if item_id.startswith("know-adr-"):
                adr_guess = item_id.removeprefix("know-")
            else:
                continue
        if adr_guess in seen_adr:
            continue
        decision_links.append(
            {
                "adr_id": adr_guess,
                "title": title or adr_guess,
                "source_path": hit.get("source_path") or "DECISIONS.md",
                "score": float(hit.get("query_score") or 0.0),
                "claim_kind": "documented",
            }
        )
        seen_adr.add(adr_guess)

    citations: list[dict[str, str]] = []
    if head_sha:
        citations.append(
            {"kind": "git", "ref": f"HEAD={head_sha}", "claim_kind": "observed"}
        )
    if snapshot_id:
        citations.append(
            {
                "kind": "snapshot",
                "ref": snapshot_id,
                "claim_kind": "observed",
            }
        )
    if version:
        citations.append(
            {
                "kind": "version",
                "ref": f"VERSION={version}",
                "claim_kind": "observed",
            }
        )
    for hit in hits:
        if hit.get("item_id"):
            citations.append(
                {
                    "kind": "knowledge",
                    "ref": str(hit["item_id"]),
                    "claim_kind": "documented",
                }
            )
        if hit.get("source_path"):
            citations.append(
                {
                    "kind": "file",
                    "ref": str(hit["source_path"]),
                    "claim_kind": "documented",
                }
            )
    for link in decision_links:
        citations.append(
            {
                "kind": "decision",
                "ref": link["adr_id"],
                "claim_kind": "documented",
            }
        )
        citations.append(
            {
                "kind": "file",
                "ref": link["source_path"],
                "claim_kind": "documented",
            }
        )

    # Deduplicate citations by (kind, ref)
    deduped: list[dict[str, str]] = []
    seen_cite: set[tuple[str, str]] = set()
    for cite in citations:
        key = (cite["kind"], cite["ref"])
        if key in seen_cite:
            continue
        seen_cite.add(key)
        deduped.append(cite)

    # Query-grounded only: snapshot/git metadata alone is not evidence-linked.
    evidence_linked = bool(hits or decision_links)

    payload: dict[str, Any] = {
        "schema_version": "1",
        "query": q,
        "mode": normalized_mode,
        "freshness": freshness,
        "repository_sha": snapshot_sha,
        "repository_sha_head": head_sha,
        "snapshot_id": snapshot_id,
        "northstar_version": version,
        "citations": deduped,
        "hits": hits,
        "decision_links": decision_links,
        "evidence_linked": evidence_linked,
        "notes": (
            "Cognitive Core C2 memory/retrieval context. "
            "Includes project-state freshness/SHA metadata plus query-ranked "
            "knowledge hits and ADR decision links. "
            "Does not approve plans or mutate authority. "
            "evidence_linked requires hits or decision_links for this query."
        ),
        "approved_for_execution": False,
        "authority_mutation": False,
    }
    # Drop None optional score fields from hits for cleaner JSON / schema
    for hit in payload["hits"]:
        for key in ("keyword_score", "vector_score", "vector_backend", "search_fallback"):
            if hit.get(key) is None:
                hit.pop(key, None)

    validate_document(payload, "brain-context-response.schema.json")
    return payload
