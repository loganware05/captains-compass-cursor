# Linear Skills Learning Loop (M24)

NorthStar uses Linear as a **flight recorder** for Skill learning — not as an
approval authority.

## Project

| Field | Value |
|---|---|
| Name | **NorthStar Skills Learning Loop** |
| ID | `c62f65bf-a376-4716-b958-0d874730a391` |
| Team | `Ovaltechnologysolutions` (`OVA`) |
| URL | https://linear.app/ovaltechnologysolutions/project/northstar-skills-learning-loop-476ac0164351 |

## Contracts (Linear documents)

| Document | URL |
|---|---|
| NorthStar Skills — Ledger Contract | https://linear.app/ovaltechnologysolutions/document/northstar-skills-ledger-contract-0c920bd49896 |
| NorthStar Agent Routing Contract | https://linear.app/ovaltechnologysolutions/document/northstar-agent-routing-contract-1f0ce2a177c9 |

## Authority

- Linear may create/update Learning Run issues, record evidence links, record
  non-authoritative status, and select among eligible Cursor agents.
- **Linear never originates Captain approval.**
- Canonical approval remains human Captain approval evidenced in GitHub /
  repository artifacts (plan digest / `--captain-approved`).
- If Linear and GitHub/repo evidence disagree, **GitHub/repository truth wins**.

## Milestones (M0–M7)

| Milestone | Meaning |
|---|---|
| **M0 — Ledger Bootstrap** | Permanent project, contracts, templates, traceability |
| **M1 — Trusted Intake** | Starred-only TI refresh + provenance for a run |
| **M2 — Analyze & Gate** | Categorize; security + supply-chain reviews before draft |
| **M3 — Draft & Test** | Skill draft / improvement proposal + sandbox validation |
| **M4 — Captain Gate** | Human-only Captain review (Linear records/links only) |
| **M5 — Promote** | Sandbox-first install via reviewed GitHub changes |
| **M6 — Execute** | Route installed Skills to eligible Cursor agents |
| **M7 — Learn** | Experience, confidence, retain / improve / prove / retire / upstream |

## Run template (machine-readable header)

Parent Learning Run issues begin with a YAML block. Full template:

`docs/templates/linear/northstar-skill-learning-run.md`

Required header fields:

```yaml
northstar_run_type: skill_learning
run_id: NS-SKILL-NNN
mode: live | retrospective-validation | fixtures
objective: <text>
category: frontend-ui | design-system | backend-library | devtool | ml-data | other
source: fixtures | ti-cache | live
control_repo: loganware05/captains-compass-cursor
control_revision: <sha>
execution_repo: loganware05/captain-compass-sandbox
execution_revision: <sha>
northstar_version: <VERSION>
captain: <human name>
captain_gate: human-only
candidate_install_authority: captain-only
approved_for_execution: false
external_repo_clone_allowed: false
external_repo_execution_allowed: false
auto_install_allowed: false
promotion_policy: sandbox-first
```

## Issue templates location

Linear MCP `list_templates` returned `[]` at plan time, and there is no
create-template tool in the MCP catalog. Reusable parent-issue text therefore
lives in the control repo:

- `docs/templates/linear/northstar-skill-learning-run.md`

Captain may paste this into Linear UI templates later if desired.

## Sub-issues (01–13)

Every Learning Run parent has thirteen gated children:

| # | Title | Typical milestone |
|---|---|---|
| 01 | Reconstruct control + sandbox provenance | M1 |
| 02 | Confirm trusted Star provenance | M1 |
| 03 | Re-run TI categorization | M2 |
| 04 | Complete security review | M2 |
| 05 | Complete dependency / supply-chain review | M2 |
| 06 | Materialize or reconcile Skill candidate | M3 |
| 07 | Reconcile / complete sandbox test evidence | M3 |
| 08 | Human Captain decision | **M4 (human-only)** |
| 09 | Promote candidate to sandbox-available | M5 |
| 10 | Install Skill through sandbox PR | M5 |
| 11 | Route next real objective to best eligible Cursor agent | M6 |
| 12 | Record formal Skill Experience | M7 |
| 13 | Decide retain / improve / prove / retire / upstream | M7 |

Working Run 001 (`OVA-5` / `NS-SKILL-001`): children `OVA-6`…`OVA-18`. Implement
through **OVA-12** (07); **stop before OVA-13** (08 Captain Gate).

## Minimal ledger sync

Attach Linear identifiers + SHAs to a learning-run JSON without inventing
approval:

```bash
CONTROL=/path/to/captains-compass-cursor

# Fixture / CI (placeholder parent id + sibling .ledger.json)
"$CONTROL/scripts/northstar" skills sync-ledger \
  --run .agent/learning-runs/<run_id>.json \
  --mode fixtures

# Link an existing Linear parent (allowlisted project only)
"$CONTROL/scripts/northstar" skills sync-ledger \
  --run .agent/learning-runs/<run_id>.json \
  --mode link \
  --parent-issue-id OVA-5 \
  --project-id c62f65bf-a376-4716-b958-0d874730a391
```

Sync **never** sets `approved_for_execution: true`, merges PRs, or installs
Skills. Refuses sync when the learning-run already has
`approved_for_execution: true`.

## Agent routing

After verified Captain approval and sandbox install, NorthStar scores **eligible**
agents (Agent Routing Contract v1). It does not hardcode a single dispatcher.

Initial known candidate only (not a mandate):

`bc-05d4594d-fac7-4378-b595-c20e3c006044`

## Topology reminder

```bash
CONTROL=/path/to/captains-compass-cursor
SANDBOX=/path/to/captain-compass-sandbox
"$CONTROL/scripts/northstar" skills learn --repo "$SANDBOX" --objective "…"
```

Product/sandbox checkouts do not contain these control scripts.

## Related

- Guide: `docs/guides/starred-repos-to-skills.md`
- Skill: `.cursor/skills/skill-learning-loop/SKILL.md`
- Module: `orchestrator/integrations/skills_ledger.py`
- ADR-041 in `DECISIONS.md`
