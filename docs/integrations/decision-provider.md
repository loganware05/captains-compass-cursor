# Decision Provider (M41/M43/M44) — skill suggestion, ranking apply, review triage

Canonical package: `orchestrator/providers/decision/`  
Plans: `m41-jev-decision-service`, `m43-jev-ranking-enablement`, `m44-jev-review-triage`  
Pinned live model: **`jev-1.13.0`** (aliases `jev-latest` / `jev-preview` refused)

## Authority

- DecisionProvider never sets `approved_for_execution`, never promotes Skills,
  never approves plans/merges, never unblocks tool calls, never suppresses
  required review or boundary/verify gates.
- Matcher-eligible roster is the only allowed skill set for ranking apply.
- On API failure, unsupported input, abstain, or gate miss → **fail closed** to
  baseline (matcher rankings / deterministic review).
- Default / CI: provider **stub**, APPLY and review shadow unset.

## Env contract

| Variable | Default | Meaning |
|---|---|---|
| `COMPASS_DECISION_PROVIDER` | `stub` | `stub` \| `file` \| `jev` (unknown → stub) |
| `COMPASS_DECISION_SHADOW` | unset/off | Skill shadow comparison evidence (M41) |
| `COMPASS_DECISION_APPLY` | unset/off | May mutate `recommended_skill_ids` if gates pass (M43) |
| `COMPASS_DECISION_NOUL_MIN` | `0.70` | Apply Noul floor |
| `COMPASS_DECISION_CONF_MIN` | `0.60` | Apply Choice confidence floor |
| `COMPASS_DECISION_REVIEW_SHADOW` | unset/off | Review triage shadow evidence (M44); never mutates findings |
| `COMPASS_DECISION_FIXTURES_DIR` | package fixtures | Offline file-provider fixtures |
| `COMPASS_JEV_MODEL_ID` | *(required for `jev`)* | Must be exactly `jev-1.13.0` (aliases refused) |
| `COMPASS_JEV_API_KEY` or `TYPESAFE_API_KEY` | unset | Captain-local only; never commit |
| `COMPASS_JEV_BASE_URL` | `https://api.typesafe.ai/v1` | Must be exactly this allowlisted HTTPS origin |

**M43 trial:** `COMPASS_DECISION_APPLY=1` implies paired skill shadow evidence.

CI defaults leave the provider on **stub** with APPLY / review shadow unset → no network.

## Shadow mode (skill observe-only)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_SHADOW=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

Evidence: `.agent/evidence/m41-jev-decision-service/shadow/<run-id>/`

`recommended_skill_ids` are **unchanged** when only skill shadow runs.

## Ranking apply (M43, opt-in)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_APPLY=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

Gates and pad-from-matcher behavior: see M43 / ADR-060. Evidence under
`.agent/evidence/m43-jev-ranking-enablement/`.

## Review triage shadow (M44, opt-in)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_REVIEW_SHADOW=1 \
./scripts/run-code-review.sh --repo-root . --base HEAD~1
```

After specialist composition, records investigation priority /
specialist-security-warranted signals from compact change metadata (paths,
domains, path flags). **Does not** change findings, candidates, boundary, or
verify. Evidence:

```text
.agent/evidence/m44-jev-review-triage/shadow/<run-id>/decision-review-triage.json
```

Reports may include path/ID refs only (`applied: false`).

## Two-pass protocol (Jev skill suggestion)

1. Rank eligible skills (`skill_suggest_v1`) with Choice + needs_skill Noul.
2. Recheck top-N with fuller descriptions (`skill_recheck_v1`) + fits Noul.
3. Explicit `none` / low Noul → abstain.

Review triage uses single-pass `review_triage_v1` (Noul + Choice).

Question revision JSON lives under
`orchestrator/providers/decision/questions/`.

## Next trials (Captain-ordered)

1. ~~Skill suggestion shadow (M41)~~
2. ~~Ranking enablement (M43)~~
3. ~~Review triage shadow (M44)~~
4. Agent routing
5. (Later) Mutating review triage apply; tool-call security triage (Notion §B)

## Related

- Notion research draft: NorthStar × Jev — Decision Service Implementation Draft
- TypeSafe: https://docs.typesafe.ai/models (`jev-1.13.0`)
- ADR-058 (skill shadow), ADR-060 (ranking apply), ADR-061 (review triage shadow)
- Holdout gate (ranking): `.agent/evidence/m43-jev-ranking-enablement/HOLDOUT_GATE.md`
