"""Map Stars-shaped records to CandidateCapability (shared by file + live TI)."""

from __future__ import annotations

from orchestrator.providers.technology_intelligence import CandidateCapability


def candidate_from_stars_shaped(raw: dict) -> CandidateCapability:
    """Map redacted or live Stars-export shaped records to CandidateCapability."""
    source = raw.get("source") if isinstance(raw.get("source"), dict) else {}
    full_name = str(raw.get("full_name") or source.get("path") or raw.get("nameWithOwner") or raw["id"])
    return CandidateCapability(
        id=str(raw.get("id") or full_name.replace("/", "-")),
        version=str(raw.get("version") or "0.1.0"),
        capabilities_provided=list(raw.get("capabilities_provided") or []),
        discovery_signal=str(
            raw.get("discovery_signal")
            or raw.get("star_signal")
            or f"github-stars:{full_name}"
        ),
        source_path=str(source.get("path") or full_name),
        provenance_url=str(source.get("provenance_url") or raw.get("html_url") or raw.get("url") or ""),
        notes=str(raw.get("notes") or raw.get("description") or ""),
    )


def candidate_from_huggingface_shaped(raw: dict) -> CandidateCapability:
    """Map Hugging Face model-card-shaped records to CandidateCapability."""
    source = raw.get("source") if isinstance(raw.get("source"), dict) else {}
    model_id = str(
        raw.get("model_id") or raw.get("id") or source.get("path") or "unknown-model"
    )
    caps = list(raw.get("capabilities_provided") or [])
    if not caps:
        pipeline = str(raw.get("pipeline_tag") or raw.get("task") or "").strip()
        caps = [pipeline.replace("-", "_") or "hf-model-pattern"]
    return CandidateCapability(
        id=str(raw.get("id") or f"hf-{model_id.replace('/', '-')}"),
        version=str(raw.get("version") or "0.1.0"),
        capabilities_provided=caps,
        discovery_signal=str(
            raw.get("discovery_signal") or f"huggingface-file:{model_id}"
        ),
        source_path=str(source.get("path") or model_id),
        provenance_url=str(
            source.get("provenance_url")
            or raw.get("url")
            or f"https://huggingface.co/{model_id}"
        ),
        notes=str(raw.get("notes") or raw.get("description") or ""),
    )


def candidate_from_package_registry_shaped(raw: dict) -> CandidateCapability:
    """Map npm/PyPI-shaped package records to CandidateCapability."""
    source = raw.get("source") if isinstance(raw.get("source"), dict) else {}
    ecosystem = str(raw.get("ecosystem") or raw.get("registry") or "package").lower()
    package_name = str(
        raw.get("package_name") or raw.get("name") or source.get("path") or "unknown-package"
    )
    caps = list(raw.get("capabilities_provided") or [])
    if not caps:
        caps = [f"{ecosystem}-package-pattern"]
    provenance = str(
        source.get("provenance_url")
        or raw.get("url")
        or (
            f"https://www.npmjs.com/package/{package_name}"
            if ecosystem == "npm"
            else f"https://pypi.org/project/{package_name}/"
            if ecosystem == "pypi"
            else ""
        )
    )
    return CandidateCapability(
        id=str(raw.get("id") or f"{ecosystem}-{package_name.replace('/', '-')}"),
        version=str(raw.get("version") or "0.1.0"),
        capabilities_provided=caps,
        discovery_signal=str(
            raw.get("discovery_signal") or f"package-registry-file:{ecosystem}:{package_name}"
        ),
        source_path=str(source.get("path") or f"{ecosystem}:{package_name}"),
        provenance_url=provenance,
        notes=str(raw.get("notes") or raw.get("description") or ""),
    )


def repo_record_from_github_api(item: dict) -> dict:
    """Normalize `gh api user/starred` repo payload to Stars-shaped record."""
    full_name = str(item.get("full_name") or "")
    topics = item.get("topics") or []
    if isinstance(topics, list) and topics and isinstance(topics[0], dict):
        topics = [t.get("name", "") for t in topics if isinstance(t, dict)]
    slug = full_name.replace("/", "-") if full_name else "unknown-repo"
    return {
        "id": f"github-stars-{slug}",
        "version": "0.1.0",
        "full_name": full_name,
        "html_url": str(item.get("html_url") or ""),
        "description": str(item.get("description") or ""),
        "star_signal": f"github-stars:live:{full_name}",
        "topics_redacted": list(topics)[:10],
        "capabilities_provided": _infer_capabilities(full_name, item.get("description") or "", topics),
        "source": {
            "type": "external-candidate",
            "path": full_name or slug,
            "provenance_url": str(item.get("html_url") or ""),
        },
        "notes": "Live GitHub starred repo — NOT APPROVED FOR EXECUTION",
    }


def _infer_capabilities(full_name: str, description: str, topics: list) -> list[str]:
    text = f"{full_name} {description} {' '.join(str(t) for t in topics)}".lower()
    tokens: list[str] = []
    for word in text.replace("/", " ").replace("-", " ").split():
        cleaned = "".join(ch for ch in word if ch.isalnum())
        if len(cleaned) >= 3:
            tokens.append(cleaned)
    # Dedupe preserve order; use top tokens as capability hints
    seen: set[str] = set()
    caps: list[str] = []
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        caps.append(token)
        if len(caps) >= 5:
            break
    return caps or ["external-repository-pattern"]
