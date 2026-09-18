# Implementation Plan — Agentic security review in NorthStar Code Reviewer

> Archive mirror of root `IMPLEMENTATION_PLAN.md` (plan id `agentic-security-review-integration`).

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED — IMPLEMENTING** (Phase A / v1.39.0) |
| Plan ID | `agentic-security-review-integration` |
| Supersedes | — (builds on M28 specialists + M36 hook hardening) |
| Product | **NorthStar** |
| Baseline | **v1.38.1** tagged @ `d9a059c` (M36 merged) |
| Prepared | 2026-09-16 |
| Approved | 2026-09-18 — Captain: “I approve the M37 Agentic_Security_Review_Integration plan” |
| Design source | Cursor Security Agents docs + PR #7 Agentic Security Review findings |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.39.0** |
| Rollback tag | `rollback/pre-m37-agentic-security-review` |
| Branch | `cursor/m37-agentic-security-review-5182` |
| Control PR | [#168](https://github.com/loganware05/captains-compass-cursor/pull/168) |
| Linear | [OVA-52](https://linear.app/ovaltechnologysolutions/issue/OVA-52/m37-agentic-equivalent-fail-closed-hook-detectors-v1390) |
| Captain | Logan Ware |

## Analysis — Cursor Agentic Security Review (level)

Cursor Security Agents (docs: https://cursor.com/docs/security-review) provide:

| Capability | Cursor today | NorthStar Code Reviewer today (M28–M35) |
|---|---|---|
| Trigger | PR Automations + `/review-security` on branch diff | Hermetic `northstar review` (diff/fixtures); optional GitHub draft (M30) |
| Depth | LLM agent with built-in security checks + custom instructions + MCP tools | Deterministic specialist emitters (`security-review` regex/heuristic candidates) → verify → report |
| Severity | Critical / High / Medium with Fix-in-Cursor links | Finding severity on candidates; no Fix-in-Cursor automation |
| Bypass classes | Catches fail-closed control gaps (hooks, authz, refspecs) as in PR #7 | Weak on control-plane / hook logic unless patterns are encoded |
| At-rest scan | Vulnerability Scanner (cron) | Not present |
| Billing / runtime | Team Cloud Agents | Local/hermetic default (no model on CI path) |

**Gap:** NorthStar’s security specialist is pattern-based and misses semantic fail-closed bypasses (self-serve approval gates, git refspec mutation). Cursor’s agentic reviewer reasoned about *control effectiveness*, not only secret regexes.

## Proposed NorthStar integration (phased)

### Phase A — Encode PR #7 classes into hermetic security specialist (this plan’s MVP)

1. Extend `orchestrator/review/specialists.py` `emit_security_candidates` with **control-plane / fail-closed** detectors for diffs touching `.cursor/hooks/**` and `hooks.json`:
   - Plan-gate self-serve: exempt Write path for `IMPLEMENTATION_PLAN.md` without Captain env / committed-status check
   - Protected-branch gaps: substring short-circuits, missing `git -C`, missing push refspec parsing
2. Add fixture diffs under `tests/fixtures/code-review/` that replay the two PR #7 findings (expect medium+ candidates).
3. Document in `docs/integrations/code-reviewer.md` + security-review Skill: “agentic-equivalent control checks (hermetic)”.
4. Optional: `northstar review --intent security-hooks` pack hint.

### Phase B — Optional live Agentic Security pass (Captain-gated, later plan)

1. Opt-in wrapper invoking Cursor `/review-security` or Security Reviewer Automation results ingestion into `.agent/evidence/review/` (never auto-merge).
2. Map Cursor severities → NorthStar finding outcomes (M31).
3. Keep hermetic default; live agent path requires allowlist (same posture as M30 GitHub drafts).

### Phase C — Shell forge residual from M36

1. `beforeShellExecution` gate for redirects/`tee` into `IMPLEMENTATION_PLAN.md` without `COMPASS_CAPTAIN_APPROVE=1`.

## Non-goals (this plan)

- Replacing hermetic CI with paid Cloud Agent reviews as default
- Auto-opening Fix-in-Cursor agents
- Changing Skill slug `code-reviewer`

## Acceptance criteria (Phase A MVP)

1. Plan-gated ✅ (Captain approved 2026-09-18)
2. Specialist emits candidates for the two PR #7 hook bypass classes on fixture diffs ✅
3. Hermetic tests green; doctor unchanged locks ✅
4. Docs updated; ADR-054 ✅
5. No requirement on Cursor Cloud for default `northstar review` ✅

## Residual (later plans)

- Phase B — live Cursor Security Agent / `/review-security` ingestion
- Phase C — shell redirect forge gate for `IMPLEMENTATION_PLAN.md`

## Approval gate

**APPROVED** 2026-09-18 — Captain: “I approve the M37 Agentic_Security_Review_Integration plan”.
