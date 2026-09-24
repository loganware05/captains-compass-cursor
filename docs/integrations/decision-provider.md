# Decision Provider (M41) — optional Jev skill suggestion

Canonical package: `orchestrator/providers/decision/`  
Plan: `m41-jev-decision-service`  
Pinned live model: **`jev-1.13.0`** (aliases `jev-latest` / `jev-preview` refused)

## Authority

- DecisionProvider output is **suggestion-only**.
- Deterministic matcher rankings remain authoritative in M41.
- Never sets `approved_for_execution`, never promotes Skills, never approves
  plans/merges, never unblocks tool calls.
- On API failure, unsupported input, or uncertainty → **abstain** and keep the
  baseline route.

## Env contract

| Variable | Default | Meaning |
|---|---|---|
| `COMPASS_DECISION_PROVIDER` | `stub` | `stub` \| `file` \| `jev` (unknown → stub) |
| `COMPASS_DECISION_SHADOW` | unset/off | When `1`/`true`/`on`, write shadow comparison evidence |
| `COMPASS_DECISION_FIXTURES_DIR` | package fixtures | Offline file-provider fixtures |
| `COMPASS_JEV_MODEL_ID` | *(required for `jev`)* | Must be exactly `jev-1.13.0` in M41 (aliases refused) |
| `COMPASS_JEV_API_KEY` or `TYPESAFE_API_KEY` | unset | Captain-local only; never commit |
| `COMPASS_JEV_BASE_URL` | `https://api.typesafe.ai/v1` | System One API base |

CI defaults leave the provider on **stub** with shadow off → no network.

## Shadow mode

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_SHADOW=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

Full artifact:

```text
.agent/evidence/m41-jev-decision-service/shadow/<run-id>/decision-shadow.json
```

`resolve.json` / plan render include **path + evidence ID only** (no duplicated
ranking payload under `.agent/plans/`).

`recommended_skill_ids` are **unchanged** when shadow runs.

## Two-pass protocol (Jev)

1. Rank eligible skills (`skill_suggest_v1`) with Choice + needs_skill Noul.
2. Recheck top-N with fuller descriptions (`skill_recheck_v1`) + fits Noul.
3. Explicit `none` / low Noul → abstain.

Question revision JSON lives under
`orchestrator/providers/decision/questions/`.

## Next trials (Captain-ordered, separate plans)

1. Ranking enablement (allow suggestions to influence rankings under a new gate)
2. Review triage
3. Agent routing

## Related

- Notion research draft: NorthStar × Jev — Decision Service Implementation Draft
- TypeSafe: https://docs.typesafe.ai/models (`jev-1.13.0`)
- ADR-058
