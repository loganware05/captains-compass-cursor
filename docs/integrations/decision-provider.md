# Decision Provider (M41–M45) — skills, ranking apply, review triage, agent routing

Canonical package: `orchestrator/providers/decision/`  
Plans: `m41-jev-decision-service`, `m43-jev-ranking-enablement`,
`m44-jev-review-triage`, `m45-jev-agent-routing`  
Pinned live model: **`jev-1.13.0`** (aliases `jev-latest` / `jev-preview` refused)

## Authority

- DecisionProvider never sets `approved_for_execution`, never promotes Skills,
  never approves plans/merges, never unblocks tool calls, never suppresses
  required review or boundary/verify gates, never bypasses agent hard filters.
- Matcher-eligible roster is the only allowed skill set for ranking apply.
- Agent-routing suggestions only see post-hard-filter eligible agents.
- On API failure, unsupported input, abstain, or gate miss → **fail closed** to
  baseline (matcher / deterministic review / hard-filtered router).
- Default / CI: provider **stub**; APPLY and all shadow flags unset.

## Env contract

| Variable | Default | Meaning |
|---|---|---|
| `COMPASS_DECISION_PROVIDER` | `stub` | `stub` \| `file` \| `jev` (unknown → stub) |
| `COMPASS_DECISION_SHADOW` | unset/off | Skill shadow comparison evidence (M41) |
| `COMPASS_DECISION_APPLY` | unset/off | May mutate `recommended_skill_ids` if gates pass (M43) |
| `COMPASS_DECISION_NOUL_MIN` | `0.70` | Apply Noul floor |
| `COMPASS_DECISION_CONF_MIN` | `0.60` | Apply Choice confidence floor |
| `COMPASS_DECISION_REVIEW_SHADOW` | unset/off | Review triage shadow (M44); never mutates findings |
| `COMPASS_DECISION_AGENT_ROUTING_SHADOW` | unset/off | Agent routing shadow (M45); never mutates selection |
| `COMPASS_DECISION_FIXTURES_DIR` | package fixtures | Offline file-provider fixtures |
| `COMPASS_JEV_MODEL_ID` | *(required for `jev`)* | Must be exactly `jev-1.13.0` (aliases refused) |
| `COMPASS_JEV_API_KEY` or `TYPESAFE_API_KEY` | unset | Captain-local only; never commit |
| `COMPASS_JEV_BASE_URL` | `https://api.typesafe.ai/v1` | Must be exactly this allowlisted HTTPS origin |

**M43 trial:** `COMPASS_DECISION_APPLY=1` implies paired skill shadow evidence.

CI defaults leave the provider on **stub** with APPLY / shadows unset → no network.

## Shadow mode (skill observe-only)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_SHADOW=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

Evidence: `.agent/evidence/m41-jev-decision-service/shadow/<run-id>/`

## Ranking apply (M43, opt-in)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_APPLY=1 \
./scripts/capability-resolve.sh "Build accessible forms with React"
```

See M43 / ADR-060. Evidence: `.agent/evidence/m43-jev-ranking-enablement/`.

## Review triage shadow (M44, opt-in)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_REVIEW_SHADOW=1 \
./scripts/run-code-review.sh --repo-root . --base HEAD~1
```

Evidence: `.agent/evidence/m44-jev-review-triage/shadow/<run-id>/`

## Agent routing shadow (M45, opt-in)

```bash
COMPASS_DECISION_PROVIDER=file \
COMPASS_DECISION_AGENT_ROUTING_SHADOW=1 \
./scripts/score-agent-routing.sh \
  --registry path/to/agents.json \
  --objective path/to/objective.json
```

After hard filters, records a semantic task-fit suggestion over **eligible**
agents only. **Does not** change `selected_agent_id` or `dispatch_ready`.
Evidence:

```text
.agent/evidence/m45-jev-agent-routing/shadow/<run-id>/decision-agent-routing.json
```

CLI payload may include path/ID refs only (`applied: false`).

## Protocols (Jev)

- Skills: two-pass `skill_suggest_v1` → `skill_recheck_v1`
- Review triage: single-pass `review_triage_v1`
- Agent routing: single-pass `agent_routing_v1`

Question revision JSON: `orchestrator/providers/decision/questions/`.

## Decision Service sequence (Captain-ordered)

1. ~~Skill suggestion shadow (M41)~~
2. ~~Ranking enablement (M43)~~
3. ~~Review triage shadow (M44)~~
4. ~~Agent routing shadow (M45)~~
5. (Later, separate plans) Mutating review/agent apply; tool-call security triage (Notion §B)

## Related

- Notion research draft: NorthStar × Jev — Decision Service Implementation Draft
- TypeSafe: https://docs.typesafe.ai/models (`jev-1.13.0`)
- ADR-058 / ADR-060 / ADR-061 / ADR-062
- Agent routing contract: `docs/integrations/agent-routing-contract.md`
