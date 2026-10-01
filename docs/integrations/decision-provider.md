# Decision Provider (M41–M49) — skills, ranking, review, routing, behavior eval/learn/instructions/prompt-eval

Canonical package: `orchestrator/providers/decision/`  
Plans: `m41-jev-decision-service`, `m43-jev-ranking-enablement`,
`m44-jev-review-triage`, `m45-jev-agent-routing`,
`m46-behavior-intelligence-foundation`, `m47-behavior-pattern-learning`,
`m48-instruction-registry`, `m49-prompt-evaluation-harness`  
Pinned live model: **`jev-1.13.0`** (aliases `jev-latest` / `jev-preview` refused)

## Authority

- DecisionProvider never sets `approved_for_execution`, never promotes Skills,
  never approves plans/merges, never unblocks tool calls, never suppresses
  required review or boundary/verify gates, never bypasses agent hard filters.
- Matcher-eligible roster is the only allowed skill set for ranking apply.
- Agent-routing suggestions only see post-hard-filter eligible agents.
- Behavior evaluation (M46) is **observe-only** — never mutates routing, Skills,
  instructions, reputation, or authority (`authority_mutation: false`).
- Behavior pattern learning (M47) is **proposal-only** — emits patterns /
  candidates; never activates Policies or mutates Skills/routing/instructions.
- Instruction registry (M48) is **proposal-only** — PICCO bundles + drafts;
  never activates Policies or writes live `.cursor/` guidance.
- Prompt evaluation (M49) is **eval/proposal-only** — baseline-vs-candidate
  reports; never promotes instructions or mutates `.cursor/` / Skills / routing.
- On API failure, unsupported input, abstain, or gate miss → **fail closed** to
  baseline (matcher / deterministic review / hard-filtered router).
- Default / CI: provider **stub**; APPLY, shadow flags,
  `COMPASS_BEHAVIOR_EVAL_ENABLED`, `COMPASS_BEHAVIOR_LEARN_ENABLED`,
  `COMPASS_INSTRUCTIONS_ENABLED`, and `COMPASS_PROMPT_EVAL_ENABLED` unset.

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
| `COMPASS_BEHAVIOR_EVAL_ENABLED` | unset/off | Required for `northstar evaluate` (M46); default off |
| `COMPASS_BEHAVIOR_EVAL_THRESHOLDS` | defaults | Optional JSON path for threshold overrides |
| `COMPASS_BEHAVIOR_LEARN_ENABLED` | unset/off | Required for `northstar learn` (M47); default off |
| `COMPASS_BEHAVIOR_LEARN_MIN_OCCURRENCE` | `3` | Minimum qualifying evaluations per pattern |
| `COMPASS_INSTRUCTIONS_ENABLED` | unset/off | Required for `northstar instructions` (M48); default off |
| `COMPASS_PROMPT_EVAL_ENABLED` | unset/off | Required for `northstar prompt-eval` (M49); default off |
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

## Behavior evaluation (M46, observe-only)

```bash
COMPASS_BEHAVIOR_EVAL_ENABLED=1 \
COMPASS_DECISION_PROVIDER=file \
./scripts/northstar evaluate run <execution-id> --repo .
```

Dual ledger (canonical): `.agent/evaluations/behavior/{evaluation_id}.json` and
`ledger.jsonl`. CSV export is non-canonical (`evaluate export --format csv`).

Package: `orchestrator/behavior/`. Distinct from M3 Compass Evaluator
(`evaluation.schema.json` / `.agent/evaluations/{id}.json`).

## Behavior pattern learning (M47, proposal-only)

```bash
COMPASS_BEHAVIOR_LEARN_ENABLED=1 \
./scripts/northstar learn scan --repo .
```

Reads the M46 behavior ledger and writes patterns + proposal-only candidates
under `.agent/evaluations/behavior/patterns/`. Distinct from Skills Learning
Loop (`northstar skills learn`). Grouping: signal + agent + skill + polarity.
Never sets `approved_for_execution`.

When a PICCO bundle can be composed for the packet's agent/skill context,
`northstar evaluate` records `evaluator.prompt_bundle_hash` (M48, record-only).

## Instruction registry (M48, proposal-only)

```bash
COMPASS_INSTRUCTIONS_ENABLED=1 \
./scripts/northstar instructions compose --agent implementation-agent --repo .
```

Registry + bundles under `.agent/evaluations/behavior/instructions/`.
`draft-from-candidates` consumes M47 `bcand-*`. Distinct from
`northstar skills learn`. Never writes `.cursor/` or activates Policies.

## Prompt evaluation harness (M49, eval/proposal-only)

```bash
COMPASS_PROMPT_EVAL_ENABLED=1 \
./scripts/northstar prompt-eval run --repo .
```

Compares baseline (`include_proposals=false`) vs candidate
(`include_proposals=true`) using hermetic fixtures. Reports under
`.agent/evaluations/behavior/prompt-eval/` (+ evidence summary). Never
promotes instructions or activates Policies. No live LLM/Jev required for CI.

## Protocols (Jev)

- Skills: two-pass `skill_suggest_v1` → `skill_recheck_v1`
- Review triage: single-pass `review_triage_v1`
- Agent routing: single-pass `agent_routing_v1`
- Behavior eval: single-pass `behavior_eval_v1` (noul per signal)

Question revision JSON: `orchestrator/providers/decision/questions/`.

## Decision Service sequence (Captain-ordered)

1. ~~Skill suggestion shadow (M41)~~
2. ~~Ranking enablement (M43)~~
3. ~~Review triage shadow (M44)~~
4. ~~Agent routing shadow (M45)~~
5. ~~Behavior Intelligence Foundation observe-only (M46)~~
6. ~~Behavior Pattern Learning proposal-only (M47)~~
7. ~~Instruction Registry + Prompt Composer proposal-only (M48)~~
8. ~~Prompt Evaluation Harness eval-only (M49)~~
9. (Later) M50 Policy promotion; mutating review/agent apply

## Related

- Notion research draft: NorthStar × Jev — Decision Service Implementation Draft
- Notion sprint: NorthStar Behavioral Intelligence Loop — Sprint Development Plan
- TypeSafe: https://docs.typesafe.ai/models (`jev-1.13.0`)
- ADR-058 / ADR-060 / ADR-061 / ADR-062 / ADR-063 / ADR-064 / ADR-065 / ADR-066
- Agent routing contract: `docs/integrations/agent-routing-contract.md`
