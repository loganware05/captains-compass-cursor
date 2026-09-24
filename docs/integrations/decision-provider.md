# Decision Provider (M41/M43) — optional Jev skill suggestion + ranking apply

Canonical package: `orchestrator/providers/decision/`  
Plans: `m41-jev-decision-service`, `m43-jev-ranking-enablement`  
Pinned live model: **`jev-1.13.0`** (aliases `jev-latest` / `jev-preview` refused)

## Authority

- DecisionProvider never sets `approved_for_execution`, never promotes Skills,
  never approves plans/merges, never unblocks tool calls.
- Matcher-eligible roster is the only allowed skill set for apply.
- On API failure, unsupported input, abstain, or gate miss → **fail closed** to
  matcher rankings.
- Default / CI: provider **stub**, APPLY unset → rankings bit-identical to matcher.

## Env contract

| Variable | Default | Meaning |
|---|---|---|
| `COMPASS_DECISION_PROVIDER` | `stub` | `stub` \| `file` \| `jev` (unknown → stub) |
| `COMPASS_DECISION_SHADOW` | unset/off | When `1`/`true`/`on`, write shadow comparison evidence |
| `COMPASS_DECISION_APPLY` | unset/off | When on, may mutate `recommended_skill_ids` if gates pass (M43) |
| `COMPASS_DECISION_NOUL_MIN` | `0.70` | Apply Noul floor |
| `COMPASS_DECISION_CONF_MIN` | `0.60` | Apply Choice confidence floor |
| `COMPASS_DECISION_FIXTURES_DIR` | package fixtures | Offline file-provider fixtures |
| `COMPASS_JEV_MODEL_ID` | *(required for `jev`)* | Must be exactly `jev-1.13.0` (aliases refused) |
| `COMPASS_JEV_API_KEY` or `TYPESAFE_API_KEY` | unset | Captain-local only; never commit |
| `COMPASS_JEV_BASE_URL` | `https://api.typesafe.ai/v1` | Must be exactly this allowlisted HTTPS origin |

**M43 trial:** `COMPASS_DECISION_APPLY=1` implies paired shadow evidence (even if
`COMPASS_DECISION_SHADOW` is unset).

CI defaults leave the provider on **stub** with APPLY unset → no network.

## Shadow mode (observe-only)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_SHADOW=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

Evidence:

```text
.agent/evidence/m41-jev-decision-service/shadow/<run-id>/decision-shadow.json
```

`recommended_skill_ids` are **unchanged** when only shadow runs.

## Ranking apply (M43, opt-in)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_APPLY=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

Gates (fail closed to matcher if any miss):

1. Provider ≠ stub, not abstaining, no error
2. `needs_skill` Noul ≥ `COMPASS_DECISION_NOUL_MIN` (default 0.70)
3. Choice confidence ≥ `COMPASS_DECISION_CONF_MIN` (default 0.60)
4. Suggested IDs ⊆ matcher-eligible roster
5. Final list = provider head + **matcher pad** to `top_n`
6. `applied: true` only when final ranking **differs** from matcher

Evidence (APPLY path):

```text
.agent/evidence/m43-jev-ranking-enablement/shadow/<run-id>/decision-shadow.json
```

`resolve.json` / plan render include **path + evidence ID only**.

## Two-pass protocol (Jev)

1. Rank eligible skills (`skill_suggest_v1`) with Choice + needs_skill Noul.
2. Recheck top-N with fuller descriptions (`skill_recheck_v1`) + fits Noul.
3. Explicit `none` / low Noul → abstain.

Question revision JSON lives under
`orchestrator/providers/decision/questions/`.

M41 generation gates (≈0.30) are separate from M43 **apply** floors (0.70 / 0.60).

## Next trials (Captain-ordered, separate plans)

1. ~~Ranking enablement~~ (M43)
2. Review triage
3. Agent routing

## Related

- Notion research draft: NorthStar × Jev — Decision Service Implementation Draft
- TypeSafe: https://docs.typesafe.ai/models (`jev-1.13.0`)
- ADR-058 (shadow), ADR-060 (apply)
- Holdout gate: `.agent/evidence/m43-jev-ranking-enablement/HOLDOUT_GATE.md`
