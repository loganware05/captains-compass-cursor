# NS-SKILL-NNN — <short objective title>

Paste this as the **parent** Learning Run issue body in project
**NorthStar Skills Learning Loop** (`c62f65bf-a376-4716-b958-0d874730a391`).

Create children 01–13 from the checklist below (or clone from Run 001).

## Run metadata

```yaml
northstar_run_type: skill_learning
run_id: NS-SKILL-NNN
mode: live
objective: <natural language objective>
category: design-system
source: ti-cache
control_repo: loganware05/captains-compass-cursor
control_revision: <control HEAD sha>
execution_repo: loganware05/captain-compass-sandbox
execution_revision: <sandbox HEAD sha>
northstar_version: 1.29.0
captain: Logan Ware
captain_gate: human-only
candidate_install_authority: captain-only
approved_for_execution: false
external_repo_clone_allowed: false
external_repo_execution_allowed: false
auto_install_allowed: false
promotion_policy: sandbox-first
```

## Run goal

Trace one Skill-learning lifecycle from trusted Stars through sandbox install,
agent execution, and Experience — without Linear originating Captain approval.

## Governance

Linear records state and routes work. It does not originate approval.
GitHub/repository evidence is authoritative if this ledger diverges.

## Sub-issues (create as children)

1. **01 — Reconstruct control + sandbox provenance** (M1)
2. **02 — Confirm trusted Star provenance** (M1)
3. **03 — Re-run TI categorization** (M2)
4. **04 — Complete security review** (M2)
5. **05 — Complete dependency / supply-chain review** (M2)
6. **06 — Materialize or reconcile Skill candidate** (M3)
7. **07 — Complete sandbox test evidence** (M3)
8. **08 — Human Captain decision** (M4 — HUMAN-ONLY GATE)
9. **09 — Promote candidate to sandbox-available** (M5)
10. **10 — Install Skill through sandbox PR** (M5)
11. **11 — Route next real objective to best eligible Cursor agent** (M6)
12. **12 — Record formal Skill Experience** (M7)
13. **13 — Decide retain / improve / prove / retire / upstream** (M7)

## Commands (control repo)

```bash
CONTROL=/path/to/captains-compass-cursor
SANDBOX=/path/to/captain-compass-sandbox

"$CONTROL/scripts/northstar" skills refresh --repo "$SANDBOX"
"$CONTROL/scripts/northstar" skills learn \
  --repo "$SANDBOX" \
  --source ti-cache \
  --objective "<objective>" \
  --category <category>

"$CONTROL/scripts/northstar" skills sync-ledger \
  --run .agent/learning-runs/<run_id>.json \
  --mode link \
  --parent-issue-id <LINEAR_PARENT_ID>
```

Product/sandbox checkouts do **not** contain these scripts.
