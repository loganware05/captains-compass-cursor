# N4 — Cross-Stack Benchmark

> **COMPLETE** (2026-10-26) — Plan ID `n4-cross-stack-benchmark`.
> Baseline: **v1.74.1** @ `db17050`.
> Release: **v1.75.0** / PR [#243](https://github.com/loganware05/captains-compass-cursor/pull/243) @ `2cd6aef`.
> Evidence: `.agent/evidence/n4-cross-stack-benchmark/`.
> Rollback: `rollback/pre-n4-cross-stack-benchmark` @ `db17050`.

## Operator note

```bash
./scripts/northstar benchmark n4 --mode hermetic --seed 20261026 --enable-gates
# or:
COMPASS_N4_BENCHMARK_ENABLED=1 ./scripts/run-n4-benchmark.sh --mode hermetic --seed 20261026
```

## Primary outcome

`accepted_tasks / (inference_cost_units + engineering_cost_units)` with
`security_regression=false` and no authorization bypass.

## Non-goals honored

No Skill/policy auto-promotion; no Level 3 GPU; evaluate-only; no silent clones.
