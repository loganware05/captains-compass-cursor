# Claude Code adapter (Captain's Compass)

This repository uses **Captain's Compass**. Canonical agent policy is in
[`AGENTS.md`](AGENTS.md) — read and follow it.

## Required startup

1. Read `AGENTS.md`
2. Read `PROJECT_CONTEXT.md`, `DECISIONS.md`, `PROGRESS.md`, `TESTING.md`
3. Inspect Git status / branch
4. Check whether `IMPLEMENTATION_PLAN.md` is **APPROVED** before product file changes

## Do not

- Modify product implementation files until the plan is APPROVED
- Work directly on protected base branches
- Weaken tests to force green
- Duplicate Compass policy here — update `AGENTS.md` / `.cursor/` instead

For Cursor + Claude Code + Codex composition notes, see the Compass control
repo doc `docs/integrations/multi-runtime-agents.md` (or `docs/EVIDENCE_MATRIX.md`
in the control repo for validation artifacts).
