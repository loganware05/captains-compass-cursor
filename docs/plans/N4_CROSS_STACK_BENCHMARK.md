# N4 — Cross-Stack Benchmark

- **Plan ID:** `n4-cross-stack-benchmark`
- **Status:** AWAITING APPROVAL (see root [`IMPLEMENTATION_PLAN.md`](../../IMPLEMENTATION_PLAN.md))
- **Proposed release:** v1.75.0
- **Branch:** `cursor/n4-cross-stack-benchmark-010c`
- **Baseline:** v1.74.1 @ `db17050`
- **Source:** Repository State assessment 2026-10-24 (priority 2)

## One-line summary

Randomized baseline vs evidence-informed NorthStar benchmark across three
independent stacks (TrapHouseKitchen, Verdant.sys / sandbox substitute,
bitcoin-data-collector), with held-out tasks and cost/latency/accuracy/security
logging — proposal-only; no Skill/policy auto-promotion; Level 3 stays deferred.

## Candidate stacks (verified 2026-10-26)

| Stack | Role | NorthStar present? |
|---|---|---|
| `TrapHouseKitchen` | Order-status tasks | Yes (`.cursor/`) |
| `Verdant.sys` | Plant/data validation | **No** at root — install or substitute sandbox |
| `bitcoin-data-collector` | Idempotent recovery | Yes; pin ref (default branch is feature branch) |
| `captain-compass-sandbox` | Fallback | Yes (N2 evidence) |
