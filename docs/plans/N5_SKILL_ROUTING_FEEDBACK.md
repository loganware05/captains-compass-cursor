# N5 — Skill-Fit / Routing Feedback

- **Plan ID:** `n5-skill-routing-feedback`
- **Status:** APPROVED / implementing (see root [`IMPLEMENTATION_PLAN.md`](../../IMPLEMENTATION_PLAN.md))
- **Release:** **v1.76.0**
- **Issue:** [#245](https://github.com/loganware05/captains-compass-cursor/issues/245)
- **Branch:** `cursor/n5-skill-routing-feedback-010c`
- **Baseline:** v1.75.0 @ `2cd6aef` (#243)
- **Rollback:** `rollback/pre-n5-skill-routing-feedback` @ `2cd6aef`
- **Evidence:** `.agent/evidence/n5-skill-routing-feedback/`
- **ADR:** ADR-096

## One-line summary

Turn N4 baseline vs evidence deltas into **proposal-only** Skill-fit / routing
suggestions — never auto-apply weights or promote policies.

## Operator

```bash
./scripts/northstar feedback n5 --repo . --enable-gates
```
