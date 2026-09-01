"""Live Hugging Face Hub Technology Intelligence (Captain local, M16)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

from orchestrator.providers.technology_intelligence import CandidateCapability
from orchestrator.providers.technology_intelligence.mapper import (
    candidate_from_huggingface_shaped,
)
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates

_TOKEN = re.compile(r"[a-z0-9]{3,}", re.I)
_DEFAULT_TOP_N = 8
_DEFAULT_TIMEOUT = 20.0
_HUB_MODELS_API = "https://huggingface.co/api/models"


def _tokenize(text: str) -> set[str]:
    return {match.group(0).lower() for match in _TOKEN.finditer(text)}


def _default_http_get(url: str, timeout: float) -> bytes:
    headers = {"Accept": "application/json"}
    token = os.environ.get("COMPASS_HF_HUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, method="GET", headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _score_candidate(objective: str, candidate: CandidateCapability) -> float:
    tokens = _tokenize(objective)
    if not tokens:
        return 0.0
    blob = " ".join(
        [
            candidate.id,
            candidate.discovery_signal,
            candidate.notes,
            " ".join(candidate.capabilities_provided),
            candidate.source_path,
        ]
    )
    hits = len(tokens & _tokenize(blob))
    return hits / max(len(tokens), 1)


def _query_terms(objective: str, limit: int = 3) -> list[str]:
    tokens = [t for t in _tokenize(objective) if len(t) >= 3]
    tokens.sort(key=lambda t: (-len(t), t))
    return tokens[:limit] or ["transformers"]


def _infer_caps(model_id: str, pipeline_tag: str, tags: list[str]) -> list[str]:
    text = f"{model_id} {pipeline_tag} {' '.join(tags)}".lower()
    seen: set[str] = set()
    caps: list[str] = []
    for token in sorted(_tokenize(text)):
        if token in seen:
            continue
        seen.add(token)
        caps.append(token)
        if len(caps) >= 5:
            break
    if pipeline_tag and pipeline_tag not in caps:
        caps.insert(0, pipeline_tag.replace("-", "_"))
    return caps[:5] or ["hf-model-pattern"]


class HuggingFaceHubLiveTechnologyIntelligenceProvider:
    """Live Hugging Face Hub model search → CandidateCapability (Captain local; never CI default)."""

    def __init__(
        self,
        *,
        top_n: int = _DEFAULT_TOP_N,
        timeout: float = _DEFAULT_TIMEOUT,
        http_get: Callable[[str, float], bytes] | None = None,
    ) -> None:
        self.top_n = top_n
        self.timeout = timeout
        self._http_get = http_get or _default_http_get

    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        del context
        records: list[dict] = []
        for term in _query_terms(objective):
            records.extend(self._search_hub(term))
        by_id: dict[str, dict] = {}
        for raw in records:
            cand_id = str(raw.get("id") or "")
            if cand_id and cand_id not in by_id:
                by_id[cand_id] = raw
        candidates = [candidate_from_huggingface_shaped(raw) for raw in by_id.values()]
        if not candidates:
            return []
        validate_ti_candidates([c.to_dict() for c in candidates])
        ranked = sorted(candidates, key=lambda c: _score_candidate(objective, c), reverse=True)
        return ranked[: self.top_n]

    def _search_hub(self, term: str) -> list[dict]:
        url = _HUB_MODELS_API + "?" + urllib.parse.urlencode(
            {"search": term, "limit": 5, "sort": "downloads", "direction": -1}
        )
        try:
            raw = self._http_get(url, self.timeout)
            payload = json.loads(raw.decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError):
            return []
        if not isinstance(payload, list):
            return []
        out: list[dict] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            model_id = str(item.get("id") or item.get("modelId") or "").strip()
            if not model_id:
                continue
            pipeline_tag = str(item.get("pipeline_tag") or item.get("task") or "").strip()
            tags = [str(t) for t in (item.get("tags") or []) if t]
            out.append(
                {
                    "id": f"hf-{model_id.replace('/', '-')}",
                    "model_id": model_id,
                    "version": "0.1.0",
                    "pipeline_tag": pipeline_tag,
                    "description": f"Hub model {model_id} ({pipeline_tag or 'general'})",
                    "capabilities_provided": _infer_caps(model_id, pipeline_tag, tags),
                    "discovery_signal": f"huggingface-hub-live:{model_id}",
                    "source": {
                        "type": "external-candidate",
                        "path": model_id,
                        "provenance_url": f"https://huggingface.co/{model_id}",
                    },
                    "notes": "Live Hugging Face Hub result — NOT APPROVED FOR EXECUTION",
                }
            )
        return out
