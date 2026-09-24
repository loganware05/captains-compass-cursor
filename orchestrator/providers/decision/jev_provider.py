"""Optional live Jev (TypeSafe System One) DecisionProvider — Captain-local only."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from orchestrator.providers.decision.state import assert_state_safe
from orchestrator.providers.decision.types import (
    FORBIDDEN_MODEL_ALIASES,
    PINNED_JEV_MODEL_ID,
    RankedSuggestion,
    SkillSuggestionRequest,
    SkillSuggestionResult,
)

DEFAULT_BASE_URL = "https://api.typesafe.ai/v1"
QUESTIONS_DIR = Path(__file__).resolve().parent / "questions"
HttpPost = Callable[[str, dict[str, str], bytes, float], bytes]


def _default_http_post(url: str, headers: dict[str, str], body: bytes, timeout: float) -> bytes:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _load_question_template(revision: str) -> dict[str, Any]:
    path = QUESTIONS_DIR / f"{revision}.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing question revision file: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"question revision must be object: {path}")
    return payload


def resolve_pinned_model_id(raw: str | None = None) -> str:
    """Require an explicit version-pinned model id; refuse aliases and empty."""
    model = (raw if raw is not None else os.environ.get("COMPASS_JEV_MODEL_ID", "")).strip()
    if not model:
        raise ValueError(
            "COMPASS_JEV_MODEL_ID is required for jev provider "
            f"(expected pinned id such as {PINNED_JEV_MODEL_ID!r})"
        )
    lowered = model.lower().replace("_", "-")
    if (
        lowered in FORBIDDEN_MODEL_ALIASES
        or lowered in {"latest", "preview", "jev"}
        or lowered.endswith("-latest")
        or lowered.endswith("-preview")
        or "_latest" in model.lower()
        or "_preview" in model.lower()
    ):
        raise ValueError(
            f"COMPASS_JEV_MODEL_ID must be a version-pinned id (got {model!r}); "
            f"refusing aliases {sorted(FORBIDDEN_MODEL_ALIASES)}"
        )
    # M41 allowlist: Captain-pinned release only.
    if model != PINNED_JEV_MODEL_ID:
        raise ValueError(
            f"COMPASS_JEV_MODEL_ID must be exactly {PINNED_JEV_MODEL_ID!r} for M41 "
            f"(got {model!r})"
        )
    return model


def _eligible_id_set(request: SkillSuggestionRequest) -> set[str]:
    return {s.skill_id for s in request.eligible_skills if s.skill_id}


def _filter_ranked(
    ranked: list[RankedSuggestion], allowed: set[str]
) -> list[RankedSuggestion]:
    return [item for item in ranked if item.skill_id in allowed]


class JevDecisionProvider:
    """Two-pass skill suggestion via POST /v1/systemone (injected HTTP for tests).

    Env:
    - COMPASS_JEV_API_KEY or TYPESAFE_API_KEY (required for live)
    - COMPASS_JEV_BASE_URL (default https://api.typesafe.ai/v1)
    - COMPASS_JEV_MODEL_ID (required; must be exactly jev-1.13.0 in M41)
    """

    name = "jev"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model_id: str | None = None,
        timeout: float = 60.0,
        http_post: HttpPost | None = None,
        gate_threshold: float = 0.30,
        fits_threshold: float = 0.30,
    ) -> None:
        key = api_key
        if key is None:
            key = os.environ.get("COMPASS_JEV_API_KEY") or os.environ.get("TYPESAFE_API_KEY") or ""
        self.api_key = key.strip()
        base = (
            base_url
            if base_url is not None
            else os.environ.get("COMPASS_JEV_BASE_URL", DEFAULT_BASE_URL)
        )
        self.base_url = str(base).strip().rstrip("/")
        try:
            self.model_id = resolve_pinned_model_id(model_id)
            self._model_error: str | None = None
        except ValueError as exc:
            self.model_id = PINNED_JEV_MODEL_ID
            self._model_error = str(exc)
        self.timeout = timeout
        self._http_post = http_post or _default_http_post
        self.gate_threshold = gate_threshold
        self.fits_threshold = fits_threshold

    def _post_systemone(self, state: Any, questions: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("COMPASS_JEV_API_KEY or TYPESAFE_API_KEY is required for jev provider")
        url = f"{self.base_url}/systemone"
        payload = {"state": state, "model": self.model_id, "questions": questions}
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        raw = self._http_post(url, headers, body, self.timeout)
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("jev response must be a JSON object")
        return data

    def _choice_criteria(self, skill_ids: list[str], summaries: dict[str, str]) -> dict[str, str | None]:
        criteria: dict[str, str | None] = {"none": "No eligible skill fits the objective"}
        for skill_id in skill_ids:
            criteria[skill_id] = summaries.get(skill_id) or skill_id
        return criteria

    def _build_rank_questions(
        self, request: SkillSuggestionRequest, summaries: dict[str, str]
    ) -> dict[str, Any]:
        template = _load_question_template(request.question_revision_rank)
        questions = dict(template.get("questions") or {})
        which = dict(questions.get("which_skill") or {})
        skill_ids = [s.skill_id for s in request.eligible_skills]
        which["criteria"] = self._choice_criteria(skill_ids, summaries)
        which.pop("criteria_from", None)
        questions["which_skill"] = which
        return questions

    def _build_recheck_questions(
        self,
        request: SkillSuggestionRequest,
        shortlist: list[str],
        fuller: dict[str, str],
    ) -> dict[str, Any]:
        template = _load_question_template(request.question_revision_recheck)
        questions = dict(template.get("questions") or {})
        which = dict(questions.get("which_of_shortlist") or {})
        which["criteria"] = self._choice_criteria(shortlist, fuller)
        which.pop("criteria_from", None)
        questions["which_of_shortlist"] = which
        return questions

    def suggest_skills(self, request: SkillSuggestionRequest) -> SkillSuggestionResult:
        started = time.perf_counter()
        if self._model_error:
            return SkillSuggestionResult(
                provider=self.name,
                model_id=None,
                abstain=True,
                abstain_reason="jev provider refused — model id not pinned",
                error=self._model_error,
                latency_ms=(time.perf_counter() - started) * 1000.0,
            )
        allowed = _eligible_id_set(request)
        try:
            summaries = {
                s.skill_id: f"{s.name}: {s.description}" for s in request.eligible_skills
            }
            state = {
                "objective": request.objective,
                "eligible_skills": [s.to_dict() for s in request.eligible_skills],
                "roster_hash": request.roster_hash,
            }
            assert_state_safe(state)

            rank_questions = self._build_rank_questions(request, summaries)
            rank_resp = self._post_systemone(state, rank_questions)
            answers = dict(rank_resp.get("answers") or {})
            usage = dict(rank_resp.get("usage") or {})
            input_tokens = int(usage.get("input_tokens") or 0)
            output_tokens = int(usage.get("output_tokens") or 0)
            model_reported = str(rank_resp.get("model") or self.model_id)

            needs = answers.get("needs_skill") or {}
            needs_noul = float(needs.get("noul") or 0.0) if isinstance(needs, dict) else 0.0
            which = answers.get("which_skill") or {}
            probs = dict(which.get("probabilities") or {}) if isinstance(which, dict) else {}
            choice = str(which.get("choice") or "") if isinstance(which, dict) else ""
            confidence = (
                float(which["confidence"])
                if isinstance(which, dict) and which.get("confidence") is not None
                else None
            )

            if needs_noul < self.gate_threshold or choice in {"", "none"}:
                return SkillSuggestionResult(
                    provider=self.name,
                    model_id=model_reported,
                    abstain=True,
                    abstain_reason="rank pass abstain (needs_skill gate or none)",
                    question_revision_rank=request.question_revision_rank,
                    question_revision_recheck=request.question_revision_recheck,
                    latency_ms=(time.perf_counter() - started) * 1000.0,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    raw_answers={"rank": answers},
                )

            if choice not in allowed:
                return SkillSuggestionResult(
                    provider=self.name,
                    model_id=model_reported,
                    abstain=True,
                    abstain_reason="out_of_roster",
                    question_revision_rank=request.question_revision_rank,
                    question_revision_recheck=request.question_revision_recheck,
                    latency_ms=(time.perf_counter() - started) * 1000.0,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    raw_answers={"rank": answers},
                )

            ranked = _filter_ranked(
                [
                    RankedSuggestion(
                        skill_id=skill_id,
                        score=float(score),
                        confidence=confidence if skill_id == choice else None,
                        rationale="jev-rank",
                    )
                    for skill_id, score in sorted(
                        probs.items(), key=lambda kv: (-float(kv[1]), kv[0])
                    )
                    if skill_id != "none"
                ],
                allowed,
            )
            shortlist = [item.skill_id for item in ranked[: max(1, request.shortlist_n)]]
            if not shortlist:
                return SkillSuggestionResult(
                    provider=self.name,
                    model_id=model_reported,
                    abstain=True,
                    abstain_reason="empty shortlist after rank",
                    latency_ms=(time.perf_counter() - started) * 1000.0,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    raw_answers={"rank": answers},
                )

            fuller = {
                s.skill_id: (
                    f"{s.name}: {s.description} "
                    f"[lifecycle={s.lifecycle_stage}; categories={','.join(s.categories)}]"
                )
                for s in request.eligible_skills
                if s.skill_id in shortlist
            }
            recheck_state = {
                "objective": request.objective,
                "shortlist": fuller,
                "roster_hash": request.roster_hash,
            }
            assert_state_safe(recheck_state)
            recheck_questions = self._build_recheck_questions(request, shortlist, fuller)
            recheck_resp = self._post_systemone(recheck_state, recheck_questions)
            recheck_answers = dict(recheck_resp.get("answers") or {})
            recheck_usage = dict(recheck_resp.get("usage") or {})
            input_tokens += int(recheck_usage.get("input_tokens") or 0)
            output_tokens += int(recheck_usage.get("output_tokens") or 0)
            model_reported = str(recheck_resp.get("model") or model_reported)

            which2 = recheck_answers.get("which_of_shortlist") or {}
            choice2 = str(which2.get("choice") or "") if isinstance(which2, dict) else ""
            conf2 = (
                float(which2["confidence"])
                if isinstance(which2, dict) and which2.get("confidence") is not None
                else None
            )
            fits = recheck_answers.get("top_fits") or {}
            fits_noul = float(fits.get("noul") or 0.0) if isinstance(fits, dict) else 0.0
            probs2 = dict(which2.get("probabilities") or {}) if isinstance(which2, dict) else {}

            if (
                choice2 in {"", "none"}
                or fits_noul < self.fits_threshold
                or choice2 not in allowed
                or choice2 not in shortlist
            ):
                return SkillSuggestionResult(
                    provider=self.name,
                    model_id=model_reported,
                    ranked=ranked,
                    abstain=True,
                    abstain_reason=(
                        "out_of_roster"
                        if choice2 not in {"", "none"} and choice2 not in allowed
                        else "recheck pass abstain (none, fits threshold, or out_of_roster)"
                    ),
                    question_revision_rank=request.question_revision_rank,
                    question_revision_recheck=request.question_revision_recheck,
                    latency_ms=(time.perf_counter() - started) * 1000.0,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    raw_answers={"rank": answers, "recheck": recheck_answers},
                )

            recheck_ranked = _filter_ranked(
                [
                    RankedSuggestion(
                        skill_id=skill_id,
                        score=float(score),
                        confidence=conf2 if skill_id == choice2 else None,
                        rationale="jev-recheck",
                    )
                    for skill_id, score in sorted(
                        probs2.items(), key=lambda kv: (-float(kv[1]), kv[0])
                    )
                    if skill_id != "none"
                ],
                set(shortlist),
            ) or ranked

            return SkillSuggestionResult(
                provider=self.name,
                model_id=model_reported,
                ranked=recheck_ranked,
                suggested_skill_id=choice2,
                abstain=False,
                question_revision_rank=request.question_revision_rank,
                question_revision_recheck=request.question_revision_recheck,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                raw_answers={"rank": answers, "recheck": recheck_answers},
            )
        except (ValueError, OSError, urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
            return SkillSuggestionResult(
                provider=self.name,
                model_id=self.model_id,
                abstain=True,
                abstain_reason="jev provider error — withhold suggestion",
                error=str(exc),
                latency_ms=(time.perf_counter() - started) * 1000.0,
            )
