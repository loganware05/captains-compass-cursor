# Implementation Plan — #50 closeout + NorthStar M4 bridge

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED — IMPLEMENTATION IN PROGRESS** |
| Plan ID | `issue-50-northstar-m4-bridge` |
| Issue | [#50](https://github.com/loganware05/captains-compass-cursor/issues/50) |
| Product | **NorthStar** (formerly Captain's Compass) |
| Baseline | `v1.25.0` on `main` |
| Prepared | 2026-09-08 |
| Start gate | Open — Captain approved 2026-09-08 |
| Branch | `cursor/issue-50-northstar-m4-bridge-6044` |
| Rollback | `rollback/pre-issue-50-m4-bridge` |
| Target release | **v1.26.0** |

## Request

Tackle open issue #50. Original M4 acceptance already shipped in **v1.8.0**; the
Captain wants the remaining hygiene **and** alignment with Notion plus the M21
NorthStar connected routine.

## Problem statement

1. Issue #50 remains **OPEN** even though persistent-role promotion and bounded
   Level 3 autonomy shipped (ADR-020, PRs historically under #50 / v1.8.0).
2. M21’s NorthStar routine (`orchestrator/integrations/`) does **not** invoke
   M4 promotion or weight-apply paths.
3. Notion is research/summary only today; it is **not** a NorthStar provider and
   must not gain approval authority. Notion MCP currently needs authentication
   in this environment.

## Current-state analysis (evidence)

| Surface | Status |
|---|---|
| `propose-persistent-role.sh` / `persistent-role-promotion` Skill | Shipped (M4) |
| `apply-routing-proposal.sh` / `bounded-autonomy` Skill | Shipped (M4; extended M17) |
| `tests/orchestrator/test_m4_persistent_roles_autonomy.py` | Present |
| ADR-020 | Accepted |
| NorthStar routine providers | `slack`, `linear`, `github`, `cursor` only |
| Notion | `notion-integration` Skill + `ingest-notion-live.sh`; no M21 adapter |
| Linear | M21 work ledger (already) |

## Desired outcome

1. **Close #50** as completed for original M4 acceptance, with a clear comment
   linking v1.8.0 / ADR-020.
2. **Bridge M4 into NorthStar** as a Captain-gated routine extension:
   - After review-ready / closeout phases (never before canonical GitHub
     approval), optionally propose persistent roles from proficiency evidence.
   - Surface pending routing proposals for Captain-flagged apply; never
     auto-apply weights.
   - Create Linear child workstreams for promotion / apply follow-ups when
     Linear is connected.
3. **Notion (optional, non-authoritative):**
   - Ingest allowlisted research pages that inform role/autonomy rationale
     (`ingest-notion-live.sh`).
   - Optionally write a release/summary mirror after successful bridge runs.
   - Never store approvals only in Notion; never add Notion to approval
     providers.

## Acceptance criteria

### A — Issue #50 hygiene

- [ ] GitHub issue #50 closed with completion comment citing v1.8.0 / ADR-020
      and this follow-on plan ID.
- [x] `PROGRESS.md` no longer lists “close #50” as open hygiene.

### B — NorthStar ↔ M4 bridge

- [x] Fixture-safe routine option (e.g. `--propose-roles` / `--surface-routing`)
      can emit persistent-role proposals and list pending routing proposals
      without mutating live `.cursor/agents/` or weights.
- [x] Weight apply remains behind existing `captain_approved` + budget gates;
      NorthStar GitHub plan approval does **not** silently apply weights.
- [x] Wrong Cursor agent / missing GitHub still fail closed (M21 rules preserved).
- [x] Linear children created for promotion/apply follow-ups when connected;
      GitHub fallback when Linear missing.
- [x] Unit/fixture tests cover bridge paths; `doctor.sh` + `tests/run.sh` pass.
- [x] Skills `northstar-connected-routine`, `persistent-role-promotion`,
      `bounded-autonomy`, and `notion-integration` cross-link the bridge.
- [x] Docs: Notion + Linear + NorthStar authority boundaries updated; ADR added.

### C — Notion surface

- [x] Documented procedure for allowlisted Notion ingest as **context only**.
- [x] Optional fixture-mode “release summary” payload for Notion write (no live
      credential required in CI).
- [x] If Notion MCP remains unauthenticated, bridge still works; Notion steps
      are skipped with an explicit non-fatal note.

## Non-goals

- Re-implementing M4 from scratch
- Adding Notion as a NorthStar approval or dispatch authority
- Auto-merging persistent-role PRs or auto-applying routing weights
- Renaming the repository
- Live Skill install
- Closing unrelated issues

## Proposed architecture

```
NorthStar routine (existing)
  └─ after REVIEW_READY / closeout hooks (Captain flags)
       ├─ persistent-role: propose-only → staging + Linear child
       ├─ bounded autonomy: list pending proposals; apply only if
       │    captain_approved on proposal JSON + budget
       └─ Notion (optional): ingest research / emit summary mirror
```

### Implementation surface (proposed)

- `orchestrator/integrations/m4_bridge.py` — propose roles + surface/apply routing
  under explicit flags
- Extend `orchestrator/integrations/routine.py` +
  `scripts/run-northstar-routine.sh`
- Fixture tests in `tests/orchestrator/test_m21_northstar.py` or
  `test_issue50_m4_bridge.py`
- Docs: `docs/integrations/{notion,linear,slack}.md`, Skill updates, ADR-038
- Issue #50 close comment + PROGRESS update

## Workstreams

| ID | Scope | Depends |
|---|---|---|
| W1 | Close #50 comment + PROGRESS hygiene | — |
| W2 | `m4_bridge` module + routine/CLI flags + tests | — |
| W3 | Linear children + Slack transition notes for bridge events | W2 |
| W4 | Notion optional ingest/summary fixtures + Skill/doc updates | W2 |
| W5 | ADR + doctor/tests green + PR | W1–W4 |

## Safety and authority

- GitHub + plan digest remain canonical approval (ADR-037).
- Slack notify only; Linear ledger only; Notion research/summary only.
- Persistent roles: staging + PR only (ADR-020).
- Weight apply: Captain flag per apply + autonomy budget (ADR-020 / M17).
- Secrets never enter Notion mirrors, Slack, or fixtures.

## Autonomy budget (proposed; activates on approval)

| Limit | Value |
|---|---|
| Maximum iterations | 6 |
| Maximum failed validation cycles | 3 |
| Maximum weight-apply operations | 0 in CI fixtures (Captain-gated only in live) |
| Stop on scope change / destructive / unresolved security high | true |

## Captain decisions (2026-09-08)

1. Close #50 **when the bridge ships** (not before).
2. Authenticate Notion MCP for live checking (desktop IDE required; cloud cannot
   complete interactive MCP auth — live path implemented; skip with explicit note
   until desktop auth is done).
3. Target release **v1.26.0**.
4. Do **not** auto-apply routing weights from NorthStar approval alone.

## Capability planning appendix (proposals only)

Top Skills: `implementation-planning`, `github-integration`,
`persistent-role-promotion`, `bounded-autonomy`, `notion-integration`,
`northstar-connected-routine`, `linear-integration`, `testing-validation`,
`autonomy-budget`.

No capability gaps detected for inferred plan-domain requirements.

## Approval record

| Captain | Decision | Date |
|---|---|---|
| Captain | **APPROVED** — implement `issue-50-northstar-m4-bridge` (close #50 on ship; Notion live auth; v1.26.0) | 2026-09-08 |
