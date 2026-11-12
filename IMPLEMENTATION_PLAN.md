# Implementation Plan — Superpowers Process Harvest + C2 Session Memory

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `superpowers-c2-session-memory` |
| Issue | [#272](https://github.com/loganware05/captains-compass-cursor/issues/272) |
| Baseline | **v1.85.0** @ `151ce6a` |
| Branch | `feature/272-superpowers-c2-session-memory` |
| Rollback | `rollback/pre-superpowers-c2-session-memory` @ `151ce6a` |
| Proposed release | **v1.86.0** |
| Created | 2026-11-12 |
| Last updated | 2026-11-12 |
| Approved by | Logan Ware (Captain) — chat “Approve” |
| Approval date | 2026-11-12 |
| Approved revision | defaults: include subagent Skill; non-trivial design gate; citation enum + optional context include |
| Worktree | `/Users/loganware/Documents/Personal/Code/captains-compass-cursor-superpowers-c2` |

Durable copy: `docs/plans/SUPERPOWERS_C2_SESSION_MEMORY.md`

## Request

Harvest Superpowers process patterns (Wave A), then C2 local session memory
(Wave B). No ECC/TradingAgents install. Authority locks false.

## Acceptance Criteria

### Wave A

- [x] Skills: design-before-plan, verification-before-completion,
      finishing-a-development-branch, subagent-driven-development
- [x] `/design-feature` + rule 01/03 cross-links
- [x] doctor + tests/run.sh green
- [x] Handbook + ADR-107
- [x] Evidence under `.agent/evidence/superpowers-process-harvest/`

### Wave B

- [x] Schema + dual-gated memory CLI + progressive search/show
- [x] `--include-session-memory` citation kind
- [x] doctor + unit tests green
- [x] ADR-108 + TESTING/handbook notes
- [x] Evidence under `.agent/evidence/c2-session-memory/`

## Non-Goals

ECC/TradingAgents install; hosted observer; auto capture hooks; memory doc rewrite;
live trading authority.

## Rollback

Tag `rollback/pre-superpowers-c2-session-memory` @ `151ce6a`; revert PR.

## Autonomy Budget

`.agent/budgets/superpowers-c2-session-memory.md` — ACTIVE
