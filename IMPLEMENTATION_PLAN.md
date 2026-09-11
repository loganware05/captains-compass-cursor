# Implementation Plan — M24 Linear Skills Learning Loop flight recorder

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m24-linear-skills-ledger` |
| Supersedes | `m22-m23-northstar-ops-ti-flywheel` (CLOSED — shipped as v1.27.0 / v1.28.0) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.28.0` / `main` @ plan start |
| Prepared | 2026-09-11 |
| Product target | `loganware05/captain-compass-sandbox` **only** for execution Experiences |
| Control repo | `loganware05/captains-compass-cursor` |
| Linear team | `Ovaltechnologysolutions` |
| Linear MCP | Authenticated in this session (ready for M0 after approval) |
| Existing Linear project | **None** matching “NorthStar Skills Learning Loop” |
| Cursor execution agent | `bc-05d4594d-fac7-4378-b595-c20e3c006044` (M21 pin; unchanged) |
| Proposed release | **v1.29.0** (single milestone ship; phased workstreams below) |
| Rollback tag (post-approval) | `rollback/pre-m24-linear-skills-ledger` |
| Branch (plan only) | `cursor/m24-linear-skills-ledger-05fd` |
| Issue | *TBD after approval* |
| Approved by | Logan Ware |
| Approval date | 2026-09-11 |
| Approved revision | 7c9fd53 (plan); implementation on `cursor/m24-linear-skills-ledger-05fd` |
| Linear M0 | **Captain-completed** — project `c62f65bf-a376-4716-b958-0d874730a391`, milestones M0–M7, Ledger + Agent Routing contracts, Run 001 OVA-5 |

## Request (Captain-level)

Continue the GitHub Stars → Skills flywheel by making **Linear** NorthStar’s
**flight recorder** for Skill learning — without inventing a new authority layer.
Preserve the Captain model: Linear may record and coordinate; only GitHub +
Captain (plan digest / `--captain-approved`) authorize advancement past
`SANDBOX_TESTED`.

Also fix production runbook topology before automating Linear, introduce a
stable `northstar skills …` launcher so agents do not need control/sandbox path
knowledge, add two-way ledger linkage on learning runs, and housekeep README
version drift (`VERSION` = 1.28.0 vs README “1.7.0”).

## Captain decisions (proposed locks — confirm on approval)

1. **One durable Linear project:** `NorthStar Skills Learning Loop` (not one
   project per Star or per run).
2. **Object model:** Skill Learning Run = parent issue + 13 gated sub-issues;
   project milestones M0–M7 mirror the lifecycle.
3. **Authority:** GitHub remains engineering truth; repo evidence remains
   technical truth; Captain remains approval authority; Linear records state only.
4. **Agent identity:** Linear-facing agent = **NorthStar First Mate** (never
   “NorthStar Captain”). Human Captain remains assignee/owner on approval-bearing
   work; agent may be delegated without replacing ownership.
5. **Execution split:** Linear First Mate = ledger/orchestrator; Cursor Cloud
   Agent = coding worker (sandbox only; M21 agent pin).
6. **Topology:** Learning CLIs live in the **control** repo and target the
   **sandbox** via `--repo-root` (or the new launcher). Product Skills must not
   imply `./scripts/...` exists inside the sandbox checkout.
7. **Pre-Linear fix order:** topology/docs + launcher + ledger schema **before**
   live Skill Learning Run automation against Linear.
8. **Housekeeping:** README header version tracks `VERSION` (separate small
   doc fix inside this plan, not a blocking Linear dependency).

## Problem statement

1. Stars→Skills learning exists (M19–M23) but has **no durable, reconstructable
   operational ledger** answering *why* a capability was trusted months later.
2. Installed Skills and guides still tell agents to run `./scripts/...` from the
   **product** checkout; those executables live only in the control repo
   (`--repo-root` already works).
3. Learning-run JSON has no Linear linkage (`project_id`, parent issue, milestone,
   control/product SHAs, delegated agent).
4. Agents (Linear ↔ Cursor) need a **topology-free** launcher:
   `northstar skills refresh|learn|promote`.
5. README still advertises **1.7.0** while `VERSION` is **1.28.0**.
6. Linear MCP is connected, but the Skills Learning Loop project/docs/templates
   do not exist yet.

## Current-state summary

| Surface | Today |
|---|---|
| Authority | ADR-037/039/040: GitHub + digest / `--captain-approved`; Linear never approves |
| Linear adapter | `orchestrator/integrations/adapters/linear.py` — generic NorthStar run ledger; allowlist `NorthStar` / `northstar`; **not** Skills Learning Run–aware |
| Learning loop | `scripts/run-skill-learning-loop.sh` + `orchestrator/learning/`; writes `.agent/learning-runs/<run_id>.json` **without** `ledger` |
| Scripts | `refresh-ti-cache`, `run-skill-learning-loop`, `promote-candidate`, etc. support `--repo-root` |
| Skills / guide | `skill-learning-loop`, `technology-intelligence-live`, `docs/guides/starred-repos-to-skills.md` use bare `./scripts/...` |
| Launcher | No `northstar skills` abstraction |
| Linear workspace | Team `Ovaltechnologysolutions`; **0** templates; **0** matching Skills projects |
| Version docs | `VERSION` = `1.28.0`; README header = `1.7.0` |

## Desired outcomes

### Authority chain (recorded in Linear; never originated by Linear)

```
GitHub Star → TI Candidate → Evidence → Skill Draft → Captain Decision
  → Promotion PR → Installed Skill → Delegated Agent → Execution Experience
  → Skill confidence
```

State machine (visual ledger only):

```
STARRED → TI_REFRESHED → CANDIDATE_SELECTED → SECURITY_REVIEWED
  → SUPPLY_CHAIN_REVIEWED → SANDBOX_TESTED
  ────── HUMAN BOUNDARY ──────
  → CAPTAIN_APPROVED → AVAILABLE_SKILL → PR_REVIEWED → INSTALLED
  → AGENT_DELEGATED → EXPERIENCE_RECORDED → PROVEN / IMPROVE / RETIRE
```

`CAPTAIN_APPROVED` may be **displayed** in Linear; Linear Agent may **notice** it;
Linear must **never create** it. Canonical approval remains GitHub Captain
decision (+ matching plan digest / `--captain-approved` as today).

### Workstreams (phased)

| Phase | Name | Outcome |
|---|---|---|
| **H0** | Doc housekeep | README / Skill counts / version align to `VERSION` |
| **H1** | Topology runbook | Skills + Stars guide + Linear docs use control/`--repo-root` or launcher |
| **H2** | `northstar skills` launcher | Stable agent-facing CLI wrapping control scripts |
| **H3** | Ledger linkage | `ledger` block on learning-run JSON (+ optional `ledger.json`) |
| **M0** | Linear ledger bootstrap | Project, milestones M0–M7, Ledger Contract doc, run template guidance, labels, First Mate guidance |
| **M1–M3** | Sync pre-human gates | Create/update Learning Run parent + sub-issues 01–07 from loop transitions |
| **M4–M5** | Captain gate + promote | Record approval **references** only; promote/PR linkage; never invent approval |
| **M6–M7** | Execute + learn | Cursor work-packet dispatch metadata + Experience / retrospective recording |

Ship target for this plan: **H0–H3 + M0 + minimal sync (create Learning Run + link SHAs)** as **v1.29.0**. Full automated transition sync through M7 may land as follow-on if budget requires — Captain may expand approval to include full M1–M7 in one release.

## Acceptance criteria

### H0 — Version housekeep

- [ ] Control `README.md` “Current version” matches `VERSION` (and Skill/subagent counts are not wildly stale).
- [ ] No other docs treat README version as authoritative over `VERSION`.

### H1 — Topology runbook

- [ ] `skill-learning-loop` (control source) documents control vs execution roots; no implication that `./scripts/run-skill-learning-loop.sh` lives in the sandbox.
- [ ] `docs/guides/starred-repos-to-skills.md` uses launcher **or** explicit `CONTROL=…` / `--repo-root` form.
- [ ] Related TI Skills that teach `./scripts/refresh-ti-cache.sh` from product context are corrected the same way (at least `technology-intelligence-live`).
- [ ] Sandbox refresh after ship picks up Skill text (no divergent sandbox-only Skill edits as source of truth).

### H2 — Launcher

- [ ] Control ships `scripts/northstar` (or equivalent) supporting at least:
  - `northstar skills refresh [--repo PATH]`
  - `northstar skills learn --repo PATH --objective "…" [--category …] [--source …]`
  - `northstar skills promote …` (thin wrap of `promote-candidate.sh`)
- [ ] Launcher resolves control root from its own location; `--repo` defaults documented; never clones external Stars.
- [ ] Doctor checks launcher exists and is executable.
- [ ] Unit/smoke tests cover help + dry wiring (no live Stars required).

### H3 — Ledger artifact

- [ ] Learning-run report includes (or writes sibling):

```json
{
  "ledger": {
    "provider": "linear",
    "project_id": null,
    "parent_issue_id": null,
    "milestone": null,
    "last_synced_at": null,
    "control_revision": "<sha>",
    "product_revision": "<sha>",
    "delegated_agent": null
  }
}
```

- [ ] Control + product SHAs always recorded when known; Linear IDs nullable until sync.
- [ ] Fixture learning-loop tests still green; new assertions for `ledger` keys.

### M0 — Linear bootstrap (after approval; MCP or documented Captain steps)

- [ ] Project **NorthStar Skills Learning Loop** exists on team `Ovaltechnologysolutions`.
- [ ] Milestones in order: M0–M7 with meanings from Captain brief.
- [ ] Project document **NorthStar Skills — Ledger Contract** with the 12 invariants.
- [ ] Reusable Learning Run structure documented (issue template if Linear API/UI allows; else First Mate playbook + saved parent description template in control docs).
- [ ] Sub-issue checklist 01–13 and gating rules documented in project + control docs.
- [ ] Project allowlist in Linear adapter updated to include this project name/id.
- [ ] Agent guidance: First Mate READ/WRITE/TRIGGER/NEVER matrix from Captain brief.
- [ ] Linear templates list was empty at plan time — if MCP cannot create issue/project templates, document Captain UI steps and keep machine-readable template under `docs/integrations/linear-skills-learning-loop.md`.

### Sync slice (v1.29.0 minimum)

- [ ] Optional/explicit CLI or loop flag can create/update a Linear parent Learning Run + child stubs (or link existing) and write IDs into `ledger`.
- [ ] Sync **never** sets Captain approval, `approved_for_execution`, merge, or install.
- [ ] Fixture mode remains CI default; live Linear requires credentials / MCP (never committed secrets).
- [ ] Disagreement rule documented: GitHub/repo evidence wins over Linear.

### Hard non-regressions

- [ ] No auto-install into `.cursor/skills/`.
- [ ] No clone/exec of Starred repos.
- [ ] No Linear-originated `CAPTAIN_APPROVED`.
- [ ] M21 agent identity pin unchanged unless separate ADR.
- [ ] `./scripts/doctor.sh` + `./tests/run.sh` green; evidence under `.agent/evidence/`.

## Non-goals

- Replacing GitHub approval with Linear approval
- Installing a Linear agent identity named “NorthStar Captain”
- One Linear project per Star or per learning run
- Cloning or executing external Starred repositories
- Auto-merge of promotion PRs
- Expanding product dispatch allowlist beyond sandbox
- Slack changes (unless needed for notify copy only)
- Full Linear Project Template export automation (document as follow-on once M0 stable)

## Assumptions

1. Captain remains Logan Ware; Linear assignee for approval-bearing issues stays human.
2. Control and sandbox checkouts are available side-by-side for real runs.
3. Linear MCP (this session) or `NORTHSTAR_LINEAR_API_KEY` will be available for M0/live sync.
4. Issue templates may require Captain UI if MCP lacks create-template APIs (confirmed: `list_templates` returned `[]`; no create-template tool in MCP catalog).
5. Sandbox Skill refresh continues via control `update.sh` after control merge.

## Open questions (Captain)

1. **Ship scope:** Approve **H0–H3 + M0 + minimal sync** as v1.29.0, or require **full M1–M7 automated transition sync** in the same release?
2. **Linear issue template:** Accept control-repo markdown template + First Mate procedure if Linear UI template creation is manual?
3. **Housekeeping issue:** Prefer a separate GitHub issue for README drift, or fold entirely into this plan (recommended: fold into H0)?
4. **Project lead / labels:** Any preferred Linear labels beyond Skills / Learning-Run / Gate / Experience?

## Proposed architecture

```
Control repo                         Sandbox (execution)
────────────                         ───────────────────
scripts/northstar  ──skills learn──► --repo sandbox
orchestrator/learning/               .agent/learning-runs/<id>.json
  + ledger block                     .agent/evidence/...
orchestrator/integrations/           (no control scripts copied)
  linear skills-ledger sync
         │
         ▼
Linear project: NorthStar Skills Learning Loop
  milestones M0–M7
  parent: NS-SKILL-RUN: <objective>
  children 01–13 (gates)
  doc: Ledger Contract
```

**First Mate (Linear)** may: inspect, create/update children, record evidence
paths, update non-authoritative status, prepare commands/work packets, link
PRs, dispatch Cursor **only after** verified GitHub Captain approval.

**First Mate may never:** approve, fabricate evidence, merge, auto-install,
execute Stars, set `approved_for_execution=true`, close a run solely because an
agent claimed success.

## Required Capabilities

See `.agent/plans/m24-linear-skills-ledger/` (capability-plan artifacts).

Relevant Skills: `implementation-planning`, `linear-integration`,
`skill-learning-loop`, `candidate-promotion`, `skill-lifecycle`,
`northstar-connected-routine`, `github-integration`, `security-review`,
`dependency-supply-chain`, `testing-validation`.

## Technology Intelligence Candidates

> External candidates are **NOT APPROVED FOR EXECUTION**.

None required for this milestone (Linear MCP + existing control code).

## Task Graph

| Task ID | Objective | Dependencies |
|---|---|---|
| `task-discovery` | Confirm topology, Linear workspace, learning-run shape | — |
| `task-architecture` | Ledger contract, launcher surface, sync boundaries | discovery |
| `task-implementation` | H0–H3 + M0 docs/bootstrap helpers + minimal sync | architecture |
| `task-validation` | Doctor, unit/integration, fixture Linear doubles | implementation |
| `task-documentation` | ADR, guide, Linear integration doc, PROGRESS, CHANGELOG | validation |

## Workstreams (file boundaries)

| Stream | Owner files | Notes |
|---|---|---|
| A — Docs/Skills topology | `.cursor/skills/skill-learning-loop/`, `technology-intelligence-live/`, `docs/guides/starred-repos-to-skills.md`, `README.md`, `docs/integrations/linear*.md` | No orchestrator behavior change |
| B — Launcher | `scripts/northstar`, doctor hooks, tests | Thin wrap only |
| C — Ledger schema | `orchestrator/learning/loop.py`, tests | Additive JSON fields |
| D — Linear sync | `orchestrator/integrations/` (+ skills ledger module), fixtures | Fail-closed; never approve |
| E — Linear M0 bootstrap | MCP + `docs/integrations/linear-skills-learning-loop.md` | After approval |

## Files expected to change (control)

- `IMPLEMENTATION_PLAN.md`, `PROGRESS.md`, `DECISIONS.md` (new ADR), `CHANGELOG.md`, `VERSION` (on ship)
- `README.md` (H0)
- `.cursor/skills/skill-learning-loop/SKILL.md` (+ related Skills)
- `docs/guides/starred-repos-to-skills.md`
- `docs/integrations/linear.md` + new `linear-skills-learning-loop.md`
- `scripts/northstar` (+ optional `scripts/northstar-skills.sh`)
- `scripts/doctor.sh`
- `orchestrator/learning/loop.py` (+ maybe small ledger helper)
- `orchestrator/integrations/adapters/linear.py` (allowlist + skills-run helpers)
- `tests/orchestrator/test_m19_skill_learning_loop.py` (+ new ledger/launcher tests)
- `.agent/plans/m24-linear-skills-ledger/` (already seeded)
- `.agent/budgets/m24-linear-skills-ledger.md` (after approval)
- `.agent/evidence/` (validation)

Sandbox: refresh PR after control ship (Skill text + VERSION), no independent Skill authorship.

## Testing strategy

- Doctor + `./tests/run.sh` (+ evals if hooks touched)
- Unit: learning-run `ledger` keys; launcher help/dispatch; Linear sync with recording transport / fixtures
- No live Stars or live Linear credentials in CI
- Manual M0 evidence: Linear project URL, milestone list screenshot or API dump under `.agent/evidence/m24-linear-skills-ledger/`
- Security review Skill: confirm Linear cannot approve / no secret leakage in issue bodies

## Security review

- Preserve ADR-037/039/040 gates
- Redact tokens from Linear descriptions/comments
- Link evidence paths; do not paste secret-bearing logs
- Explicit tests that sync refuses to mark issue 08 approved without GitHub reference

## Accessibility review

Not applicable (no UI product change). Sandbox UI untouched except optional later Experience run.

## Migration plan

- Additive ledger fields; old learning-run JSON remains readable
- Launcher is new; old script paths remain for humans who know topology
- Linear project created once; no migration of historical runs required for v1.29.0

## Rollback plan

1. Tag `rollback/pre-m24-linear-skills-ledger` before implementation commits.
2. Revert control merge / restore tag.
3. Archive or leave Linear project (ledger-only; safe to retain).
4. Sandbox: re-install prior Compass VERSION if Skill text must roll back.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Linear treated as approval authority | Docs + code asserts; issue 08 cannot be agent-approved |
| MCP cannot create issue templates | Control-repo template doc + Captain UI checklist |
| Agents still run `./scripts` in sandbox | H1+H2 before live Learning Runs |
| Scope creep to full M1–M7 automation | Open question #1; default ship slice H0–H3+M0+minimal sync |
| Adapter allowlist too broad | Allowlist exact project name/id |

## Autonomy budget (post-approval)

| Limit | Value |
|---|---|
| Max iterations | 8 |
| Max additional deps | 0 (stdlib + existing Linear transport) |
| Max files touched | ~40 |
| Stop | Budget Stop Report under `.agent/evidence/` |

## Evaluation strategy

Reconstructability test: given one fixture learning run + synced Linear parent,
an agent can answer: control SHA, sandbox SHA, evidence paths, whether Captain
approval exists (and from where), and next gate — without trusting Linear over
repo state.

## Learning plan

Retain under `.agent/plans/m24-linear-skills-ledger/` and release evidence.
First real Learning Run after M0 uses Linear as ledger only; feed Experience
back per M7 when an installed Skill is exercised.

## Approval Boundary

**No product implementation, Linear project creation, or launcher commits beyond
this plan branch until the Captain explicitly approves this plan** (status →
`APPROVED` with name/date/revision).

Discovery completed this session:

- Linear MCP authenticated
- Team `Ovaltechnologysolutions` identified
- Confirmed no existing Skills Learning Loop project
- Confirmed control scripts already support `--repo-root`
- Confirmed README version drift (1.7.0 vs 1.28.0)
- Confirmed learning-run JSON lacks `ledger`

---

## Captain approval block

```text
Status: APPROVED
Approved by: Logan Ware
Approval date: 2026-09-11
Approved revision: 7c9fd53 (plan); implementation continues on cursor/m24-linear-skills-ledger-05fd
Ship scope: H0–H3 + M0 + minimal sync as v1.29.0
Notes: Linear project already bootstrapped by Captain (NorthStar Skills Learning Loop). Issue templates: use control-repo markdown unless MCP gains create-template. Labels: defaults only. Run 001 OVA-5 live; implement OVA-6..OVA-12 next; stop before OVA-13 Captain Gate.
```

### Linear bootstrap status (Captain-completed M0)

- Project: NorthStar Skills Learning Loop (`c62f65bf-a376-4716-b958-0d874730a391`)
- Run 001 parent: OVA-5 NS-SKILL-001
- Lifecycle children: OVA-6 … OVA-18
- Governance docs attached in Linear (Ledger Contract + Agent Routing Contract)

