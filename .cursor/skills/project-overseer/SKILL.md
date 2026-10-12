---
name: project-overseer
description: Read-oriented Project Overseer — snapshot, explain, compare, and propose memory reconcile without mutating authority
---

# Project Overseer

## Use this Skill when

The Captain or First Mate needs a current, evidence-backed understanding of
repository reality vs project memory — drift detection, system-map refresh, or
reconcile proposals — without granting execution authority.

## Inputs

- Repository root (`--repo` / `--repo-root`)
- Optional enable gate: `COMPASS_STATUS_ENABLED=1`
- Optional provider: `COMPASS_STATUS_PROVIDER=stub|http` (default stub)
- Optional live model: `COMPASS_STATUS_MODEL` + `OPENROUTER_API_KEY` /
  `COMPASS_STATUS_API_KEY` when provider is `http`

## Procedure

1. **Enable the gate** (required):

   ```bash
   export COMPASS_STATUS_ENABLED=1
   ```

2. **Snapshot** repository understanding:

   ```bash
   ./scripts/northstar status snapshot --repo .
   ```

3. **Explain** (stub by default; opt-in live):

   ```bash
   ./scripts/northstar status explain --repo .
   # Optional live path (never required for CI):
   COMPASS_STATUS_PROVIDER=http COMPASS_STATUS_MODEL=<model> \
     ./scripts/northstar status explain --repo .
   ```

4. **Compare** since a SHA:

   ```bash
   ./scripts/northstar status compare --since <sha> --repo .
   ```

5. **Reconcile** (proposal-only drafts under `.agent/status/reconcile-proposals/`):

   ```bash
   ./scripts/northstar status reconcile --repo .
   ```

6. Label every material claim as **observed**, **documented**, **external**, or
   **proposed**. Prefer citations to files, SHAs, VERSION, and evidence paths.

7. Treat `.agent/status/system-map.md` and `scope-ledger.json` as Overseer
   artifacts — **not** replacements for `PROJECT_CONTEXT.md` / ADRs.

## Constraints

- Never approve `IMPLEMENTATION_PLAN.md` or set plan Status to APPROVED.
- Never promote Skills or Policies; never mutate routing or reputation.
- Never merge, deploy, release, or rewrite canonical project memory silently.
- Never require live HTTP/Kimi for CI; stub must remain sufficient.
- Fail closed when the live provider is selected without keys or on network error.
- Always keep `approved_for_execution: false` and `authority_mutation: false`.

## Return

- Snapshot / explanation summary with claim labels
- Paths to system-map, scope-ledger, and any reconcile proposals
- Explicit statement that canonical memory was not auto-rewritten
