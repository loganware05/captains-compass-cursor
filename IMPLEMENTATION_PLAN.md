# Implementation Plan — M42 / Specialist Added-Line Scope (M37 FP)

## Metadata

| Field | Value |
|---|---|
| Status | **COMPLETE** |
| Plan ID | `m42-specialist-added-line-scope` |
| Approved | 2026-09-24 — Captain: "I've merged PR #179, continue with M37, then the rest of the plan" |
| Supersedes | Closes M40/M41 follow-up: M37 specialist FP on removed / docs-described short-circuits |
| Product | **NorthStar** |
| Baseline | **v1.42.0** @ `ed20499` (M41 merged #179) |
| Prepared | 2026-09-24 |
| Proposed release | **v1.42.1** (patch) |
| Rollback | `rollback/pre-m42-specialist-added-line-scope` @ `ed20499` |
| Branch | `cursor/m42-specialist-added-line-scope-753c` |
| Captain | Logan Ware |

## Request

Fix M37 fail-closed hook detectors so `sec-hook-checkout-shortcircuit` (and siblings) only inspect **added lines in executable hook scripts / hooks.json**, not removed lines and not docs/README that mention legacy patterns.

## Problem

M40 sandbox clean review emitted a verified FP for `sec-hook-checkout-shortcircuit` while refreshing hooks: the short-circuit was **removed** from `protected-branch.sh`, but docs/README **added** prose describing `checkout -b feature/`. Detectors searched whole-diff added text, so documentation + `allow()` helpers in scripts triggered the finding.

## Solution

1. Parse added lines **per file**; ignore removed (`-`) lines.
2. Restrict fail-closed pattern matching to `_HOOK_SCAN_PATH` (`.cursor/hooks/*.sh` + `hooks.json`), excluding README/docs under hooks.
3. Regression tests: removal-only, docs+removal, replay M40 sandbox context pack.

## Out of scope

- Ranking enablement / review triage / agent routing (next plans after this patch)
- Changing detector severity or new detector classes

## Acceptance criteria

1. Existing M37 positive fixtures still emit their findings.
2. Removal-only short-circuit diffs emit no checkout finding.
3. Docs mentioning the pattern + hook removal emit no checkout finding.
4. M40 sandbox clean context pack replay emits no `sec-hook-checkout-shortcircuit`.
5. doctor + `./tests/run.sh` + evals green.

## Autonomy budget

| Limit | Max |
|---|---|
| Iterations | 4 |
| Failed validation cycles | 2 |
