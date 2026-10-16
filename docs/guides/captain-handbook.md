# Captain Handbook — Using NorthStar

One-page operating guide for the human Captain. Use this after **v1.59.0**.
Deep dives live in linked docs; this handbook is the map.

## What NorthStar is

NorthStar (control repo: `captains-compass-cursor`) is an **approval-gated Cursor
workflow**. It owns rules, Skills, hooks, docs templates, and operator CLIs.
Product application code lives in other repos; those repos receive Skills via
`install.sh` / `update.sh`.

You are the **Captain**. Agents are the **First Mate** and specialists. Nothing
that mutates Skills, Policies, or authority proceeds without your explicit gate.

## Topology (required)

```text
CONTROL  = /path/to/captains-compass-cursor     # scripts/northstar, doctor, learning CLIs
SANDBOX  = /path/to/captain-compass-sandbox     # disposable product for learn/promote
PRODUCT  = /path/to/<your-app>                  # real work after install/update
```

| Lives in | What |
|---|---|
| **Control** | `scripts/northstar`, orchestrator, doctor, Learning Loop, review/repair CLIs |
| **Sandbox / product** | `.cursor/` Skills/rules/agents, memory docs, `.agent/` — **not** control `scripts/` |

Always run learning and TI from **control**, pointing `--repo` at sandbox/product:

```bash
CONTROL=/path/to/captains-compass-cursor
SANDBOX=/path/to/captain-compass-sandbox

"$CONTROL/scripts/doctor.sh"
"$CONTROL/scripts/northstar" help
"$CONTROL/scripts/northstar" skills learn --repo "$SANDBOX" --objective "…"
```

## Day-to-day surfaces

Launcher: `"$CONTROL/scripts/northstar" <surface> …`

| Surface | When to use | Gate |
|---|---|---|
| `skills` | Star → TI → draft Skill → promote proposal | Captain PR to `.cursor/skills/`; `--captain-approved` for late stages |
| `review` | Detect→investigate→verify→report on a product PR/checkout | Evidence-only by default |
| `evaluate` / `learn` / `instructions` / `prompt-eval` / `policy` | Behavior Loop (observe → pattern → compose → eval → promote policy) | Each needs `COMPASS_*_ENABLED=1`; never auto-promotes Skills |
| `status` | Project Overseer snapshot / explain / reconcile | `COMPASS_STATUS_ENABLED=1`; proposal-only reconcile |
| `brain` | Cognitive Core project-state sync / freshness | `COMPASS_BRAIN_ENABLED=1`; `.agent/project-state/` only |
| `provenance` / `examples` | Explain run-to-run prompt/policy lineage; curate exemplars | `COMPASS_PROVENANCE_ENABLED=1`; `auto_promoted: false` |
| `context` | Filesystem-gated context inodes | Build/walk only |
| `intent` / `outcomes` / `repair` / `precision` | Review intent packs, triage, repair packets, precision ledger | Never Captain approval substitutes |

Full operator map: [`docs/INDEX.md`](../INDEX.md).

## Core loop: issue → plan → approve → implement → evidence → PR

1. Inspect repo + memory (`PROJECT_CONTEXT.md`, `PROGRESS.md`, `DECISIONS.md`).
2. Write/update `IMPLEMENTATION_PLAN.md` → **AWAITING APPROVAL**.
3. You set Status → **APPROVED** (explicit).
4. Branch + rollback tag (never implement on `main`).
5. Implement within plan boundaries; run doctor/tests; store evidence under `.agent/evidence/`.
6. First Mate **commits and opens the PR** (standing order — no separate ask).
7. You merge only after your review.

**Standing order (2026-10-13):** Plan approval authorizes implement → validate →
commit → open PR. It does **not** authorize merge, deploy, or authority mutation.

Agents must stop at the approval gate. Saying “just implement” does not override it.

## Goal: GitHub repos → portable Skills

### What works today

1. **Star** trusted repos on GitHub (required provenance).
2. From control: refresh TI cache → categorize → `skills learn` → read scorecards.
3. Promote with `--captain-approved` to an **AVAILABLE** proposal.
4. You open a **PR** that copies the draft into control `.cursor/skills/<slug>/`.
5. Run `"$CONTROL/scripts/update.sh" "$PRODUCT"` (or install) so other projects get the Skill.

Step-by-step: [`guides/starred-repos-to-skills.md`](starred-repos-to-skills.md).  
Library-fill ops (A1): [`guides/skills-library-fill-a1.md`](skills-library-fill-a1.md).  
Which Stars first: [`guides/starred-library-ranking.md`](starred-library-ranking.md)
(Wave 1 promoted: `agent-skills-packaging`, `goose-agent-orchestration`,
`security-audit-procedures`).

### Hard non-goals (do not expect these)

| Non-goal | Why |
|---|---|
| Clone / install / execute starred repos | Skills capture *procedure*, not vendor runtimes |
| Auto-install into `.cursor/skills/` | Captain PR only |
| Feed non-starred URLs into TI | Starred-only gate (M23 / ADR-040) |
| Linear / Overseer / Behavior Loop as approval | Human Captain + GitHub evidence remain authority |
| Run reverse-engineering MCP toolchains (e.g. REA) inside NorthStar | Captain-local tools only; Learning Loop is metadata |

**Starred REA (`morluto/rea`)** may enter TI as a **metadata/procedure** candidate after scorecards. It does **not** wire Hopper/Ghidra/IDA or `npx rea-agents` into the sandbox.

## Carry Skills across projects

```bash
CONTROL=/path/to/captains-compass-cursor
PRODUCT=/path/to/product-repo

# First time
"$CONTROL/scripts/install.sh" "$PRODUCT"

# Later (after new Skills land on a control release you choose)
"$CONTROL/scripts/update.sh" "$PRODUCT"
```

See [`PRODUCT_ONBOARDING.md`](../PRODUCT_ONBOARDING.md) and [`UPGRADING.md`](../UPGRADING.md).  
Product memory docs (`PROJECT_CONTEXT.md`, etc.) are preserved by default.

## Behavior Loop (optional operate)

Hermetic operate (gates default **off**):

```bash
export COMPASS_BEHAVIOR_EVAL_ENABLED=1
export COMPASS_BEHAVIOR_LEARN_ENABLED=1
export COMPASS_INSTRUCTIONS_ENABLED=1
export COMPASS_PROMPT_EVAL_ENABLED=1
export COMPASS_PROVENANCE_ENABLED=1
export COMPASS_STATUS_ENABLED=1
export COMPASS_DECISION_PROVIDER=file

"$CONTROL/scripts/northstar" evaluate run <execution-id> --repo "$CONTROL"
"$CONTROL/scripts/northstar" learn scan --repo "$CONTROL"
"$CONTROL/scripts/northstar" instructions compose --agent implementation-agent --repo "$CONTROL"
"$CONTROL/scripts/northstar" prompt-eval run --repo "$CONTROL"
"$CONTROL/scripts/northstar" status snapshot --repo "$CONTROL"
```

Details: `TESTING.md` (Behavior / Overseer sections).

## Weekly Captain cadence (suggested)

1. `doctor.sh` on control; skim `PROGRESS.md`.
2. Star or unstar repos intentionally; refresh TI when learning.
3. One Learning Run toward A1 (scorecard → at most one promote/PR).
4. `update.sh` any active product repos after Skill merges.
5. Optional: Overseer `status snapshot` (stub) — never auto-rewrites memory.

## Failure modes

| Symptom | Check |
|---|---|
| `skills learn` / `status` exits non-zero | Enable flag missing; or scripts run from product instead of control |
| Draft refused | Missing security or supply-chain scorecard artifact |
| Star not appearing | Repo not starred under the authenticated `gh` account; refresh cache |
| Skill missing in product | Control release not updated into product; re-run `update.sh` |

## Related

- [`guides/starred-repos-to-skills.md`](starred-repos-to-skills.md)
- [`guides/skills-library-fill-a1.md`](skills-library-fill-a1.md)
- [`INDEX.md`](../INDEX.md)
- [`AGENT_INSTALL_PROMPT.md`](../AGENT_INSTALL_PROMPT.md)
- Skill: `.cursor/skills/skill-learning-loop/SKILL.md`
- Skill: `.cursor/skills/project-overseer/SKILL.md`
