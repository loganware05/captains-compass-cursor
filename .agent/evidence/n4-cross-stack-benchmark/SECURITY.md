# Security review — n4-cross-stack-benchmark

- Gate fail-closed without `COMPASS_N4_BENCHMARK_ENABLED`.
- Live mode requires explicit `COMPASS_N4_STACK_ROOTS` (no silent clone).
- `COMPASS_N4_LIVE_IMPLEMENT=1` refused in v1.75.0.
- Schema const-false: `policy_promoted`, `auto_applied`, `authority_mutation`,
  `approved_for_execution`, `security_regression`.
- Evidence uses proxy cost units only; no secrets.
