# M49 Prompt Evaluation Harness — Validation

| Field | Value |
|---|---|
| Plan ID | `m49-prompt-evaluation-harness` |
| Linear | OVA-61 |
| Release | v1.49.0 |
| Branch | `cursor/m49-prompt-evaluation-harness-plan-3192` |
| Rollback | `rollback/pre-m49-prompt-evaluation-harness` @ `2d388cf` |
| Date | 2026-10-01 |

## Validation

| Check | Result |
|---|---|
| M49 unit/CLI tests | **15/15 passed** |
| Orchestrator suite | **573+ tests OK** (includes M46–M49) |
| `./scripts/doctor.sh` | **passed** (0 errors); prompt-eval fail-closed smoke exit 2 |
| Enable gate | Unset `COMPASS_PROMPT_EVAL_ENABLED` → CLI exit 2 |
| Live M48 isolation | Compose seeds only per-case temp registries; operator `instructions/` untouched |
| Schema locks | `approved_for_execution: false`, `authority_mutation: false`, `additionalProperties: false` |
| Hermetic | No live LLM/Jev; fixture scoring only |

## Adversarial findings addressed

1. **Critical** — Live M48 registry mutation → fixed via per-case `tempfile` registries
2. **High** — Cross-case registry pollution → fixed by isolation
3. **High** — Absolute-path `lstrip("./")` bug → fixed; `/tests/...` fails closed
4. **Medium** — Nested eval JSON gitignore → `.agent/evaluations/behavior/**/*.json` ignored
5. **Medium** — Ungated `run_prompt_eval` → calls `require_prompt_eval_enabled()`
6. **Low** — Doctor smoke now asserts exit 2 + env name in stderr

## Operator smoke

```bash
COMPASS_PROMPT_EVAL_ENABLED=1 \
./scripts/northstar prompt-eval run --repo .
```

## Ready for merge

Yes — after Captain review of PR #187.
