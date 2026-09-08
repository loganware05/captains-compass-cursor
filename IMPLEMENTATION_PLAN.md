# Implementation Plan — #50 closeout + NorthStar M4 bridge

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING CAPTAIN APPROVAL** |
| Plan ID | `issue-50-northstar-m4-bridge` |
| Issue | [#50](https://github.com/loganware05/captains-compass-cursor/issues/50) |
| Product | **NorthStar** (formerly Captain's Compass) |
| Baseline | `v1.25.0` on `main` |
| Prepared | 2026-09-08 |
| Start gate | Explicit Captain approval |

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
- [ ] `PROGRESS.md` no longer lists “close #50” as open hygiene.

### B — NorthStar ↔ M4 bridge

- [ ] Fixture-safe routine option (e.g. `--propose-roles` / `--surface-routing`)
      can emit persistent-role proposals and list pending routing proposals
      without mutating live `.cursor/agents/` or weights.
- [ ] Weight apply remains behind existing `captain_approved` + budget gates;
      NorthStar GitHub plan approval does **not** silently apply weights.
- [ ] Wrong Cursor agent / missing GitHub still fail closed (M21 rules preserved).
- [ ] Linear children created for promotion/apply follow-ups when connected;
      GitHub fallback when Linear missing.
- [ ] Unit/fixture tests cover bridge paths; `doctor.sh` + `tests/run.sh` pass.
- [ ] Skills `northstar-connected-routine`, `persistent-role-promotion`,
      `bounded-autonomy`, and `notion-integration` cross-link the bridge.
- [ ] Docs: Notion + Linear + NorthStar authority boundaries updated; ADR added.

### C — Notion surface

- [ ] Documented procedure for allowlisted Notion ingest as **context only**.
- [ ] Optional fixture-mode “release summary” payload for Notion write (no live
      credential required in CI).
- [ ] If Notion MCP remains unauthenticated, bridge still works; Notion steps
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

## Open questions for Captain

1. Prefer **close #50 now** and track bridge under this new plan ID only, or keep
   #50 open until the bridge ships?
2. Should Notion MCP auth be completed in this environment before W4 live checks,
   or is fixture-only Notion acceptable for this milestone?
3. Target version: patch **v1.25.1** vs next minor **v1.26.0**?

## Recommended defaults (awaiting approval)

1. Close #50 when bridge PR merges (comment now that M4 shipped; final close on
   bridge land) **or** close immediately and reference this plan — Captain picks.
2. Fixture-only Notion in CI; live MCP optional if authenticated.
3. Target **v1.26.0** (behavioral routine extension).
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
| Pending | **AWAITING APPROVAL** | — |

**Implementation must not begin until the Captain explicitly approves this plan.**
