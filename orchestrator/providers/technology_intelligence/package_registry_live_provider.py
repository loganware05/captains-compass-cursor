"""Live npm/PyPI package-registry Technology Intelligence (Captain local, M12)."""

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
    candidate_from_package_registry_shaped,
)
from orchestrator.providers.technology_intelligence.validate import validate_ti_candidates

_TOKEN = re.compile(r"[a-z0-9]{3,}", re.I)
_DEFAULT_TOP_N = 8
_DEFAULT_TIMEOUT = 20.0


def _tokenize(text: str) -> set[str]:
    return {match.group(0).lower() for match in _TOKEN.finditer(text)}


def _default_http_get(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
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
    # Prefer longer tokens first for search quality
    tokens.sort(key=len, reverse=True)
    return tokens[:limit] or ["library"]


class PackageRegistryLiveTechnologyIntelligenceProvider:
    """Live npm + PyPI search → CandidateCapability (Captain local; never CI default)."""

    def __init__(
        self,
        *,
        ecosystems: tuple[str, ...] | None = None,
        top_n: int = _DEFAULT_TOP_N,
        timeout: float = _DEFAULT_TIMEOUT,
        http_get: Callable[[str, float], bytes] | None = None,
    ) -> None:
        env_eco = os.environ.get("COMPASS_PACKAGE_TI_ECOSYSTEMS", "npm,pypi").strip().lower()
        if ecosystems is not None:
            self.ecosystems = ecosystems
        else:
            parsed = tuple(e.strip() for e in env_eco.split(",") if e.strip())
            self.ecosystems = parsed or ("npm", "pypi")
        self.top_n = top_n
        self.timeout = timeout
        self._http_get = http_get or _default_http_get

    def discover_candidates(self, objective: str, context: dict) -> list[CandidateCapability]:
        del context
        records: list[dict] = []
        for term in _query_terms(objective):
            if "npm" in self.ecosystems:
                records.extend(self._search_npm(term))
            if "pypi" in self.ecosystems:
                records.extend(self._search_pypi(term))
        # Dedupe by id
        by_id: dict[str, dict] = {}
        for raw in records:
            cand_id = str(raw.get("id") or "")
            if cand_id and cand_id not in by_id:
                by_id[cand_id] = raw
        candidates = [candidate_from_package_registry_shaped(raw) for raw in by_id.values()]
        if not candidates:
            return []
        validate_ti_candidates([c.to_dict() for c in candidates])
        ranked = sorted(candidates, key=lambda c: _score_candidate(objective, c), reverse=True)
        return ranked[: self.top_n]

    def _search_npm(self, term: str) -> list[dict]:
        url = "https://registry.npmjs.org/-/v1/search?" + urllib.parse.urlencode(
            {"text": term, "size": 5}
        )
        try:
            raw = self._http_get(url, self.timeout)
            payload = json.loads(raw.decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError):
            return []
        objects = payload.get("objects") if isinstance(payload, dict) else None
        if not isinstance(objects, list):
            return []
        out: list[dict] = []
        for obj in objects:
            pkg = obj.get("package") if isinstance(obj, dict) else None
            if not isinstance(pkg, dict):
                continue
            name = str(pkg.get("name") or "").strip()
            if not name:
                continue
            desc = str(pkg.get("description") or "")
            version = str(pkg.get("version") or "0.0.0")
            out.append(
                {
                    "id": f"npm-{name.replace('/', '-')}",
                    "package_name": name,
                    "ecosystem": "npm",
                    "version": version,
                    "description": desc,
                    "capabilities_provided": _infer_caps(name, desc),
                    "discovery_signal": f"package-registry-live:npm:{name}",
                    "source": {
                        "type": "external-candidate",
                        "path": f"npm:{name}",
                        "provenance_url": f"https://www.npmjs.com/package/{name}",
                    },
                    "notes": "Live npm registry result — NOT APPROVED FOR EXECUTION",
                }
            )
        return out

    def _search_pypi(self, term: str) -> list[dict]:
        # PyPI JSON search via warehouse XML-RPC is awkward; use pypi.org search JSON alternative
        # Simple API: https://pypi.org/search/?q=... is HTML. Use warehouse simple name probe via
        # https://pypi.org/pypi/<name>/json when term looks like a package, else skip HTML scrape.
        # For live discovery without scraping HTML, query the JSON endpoint for the term as name
        # and also try pluralized common libraries via search.pypi.org unofficial JSON if available.
        # Prefer official: GET https://pypi.org/search/?q= returns HTML — avoid.
        # Use: https://pypi.org/pypi/{term}/json for exact; plus https://pypi.org/simple/ is listing.
        # Practical approach: try exact package JSON; also try first token as package name.
        url = f"https://pypi.org/pypi/{urllib.parse.quote(term)}/json"
        try:
            raw = self._http_get(url, self.timeout)
            payload = json.loads(raw.decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError):
            return []
        info = payload.get("info") if isinstance(payload, dict) else None
        if not isinstance(info, dict):
            return []
        name = str(info.get("name") or term).strip()
        if not name:
            return []
        desc = str(info.get("summary") or info.get("description") or "")[:500]
        version = str(info.get("version") or "0.0.0")
        return [
            {
                "id": f"pypi-{name.replace('/', '-')}",
                "package_name": name,
                "ecosystem": "pypi",
                "version": version,
                "description": desc,
                "capabilities_provided": _infer_caps(name, desc),
                "discovery_signal": f"package-registry-live:pypi:{name}",
                "source": {
                    "type": "external-candidate",
                    "path": f"pypi:{name}",
                    "provenance_url": f"https://pypi.org/project/{name}/",
                },
                "notes": "Live PyPI registry result — NOT APPROVED FOR EXECUTION",
            }
        ]


def _infer_caps(name: str, description: str) -> list[str]:
    text = f"{name} {description}".lower()
    tokens = [t for t in _tokenize(text)]
    seen: set[str] = set()
    caps: list[str] = []
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        caps.append(token)
        if len(caps) >= 5:
            break
    return caps or ["package-registry-pattern"]
