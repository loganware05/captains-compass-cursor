# Multi-runtime agents (Cursor, Claude Code, Codex)

Captain's Compass is authored for **Cursor**, but production teams often compose
multiple coding agents. Keep **one policy source** and thin adapters elsewhere.

## Canonical policy

| Artifact | Role |
|---|---|
| `AGENTS.md` | Cross-tool operating contract (startup, approval gate, safety) |
| `.cursor/rules/*.mdc` | Always-on Cursor rules |
| `.cursor/skills/*/SKILL.md` | On-demand procedures |
| `.cursor/commands/*.md` | Cursor slash-command phase entry points |
| Memory docs | `PROJECT_CONTEXT.md`, `DECISIONS.md`, `PROGRESS.md`, `TESTING.md`, plan |

Do **not** fork policy into long duplicate `CLAUDE.md` / Codex files.

## Cursor

Use slash commands under `.cursor/commands/` (`/plan-feature`,
`/implement-approved-plan`, …). Skills and hooks enforce the harness.

## Claude Code

Compass may install a thin root `CLAUDE.md` **only when missing** (never
overwrites a Captain-customized file). It should only point at `AGENTS.md` and
the Compass startup sequence.

Suggested contents match `templates/docs/CLAUDE.md`.

## OpenAI Codex / other AGENTS.md readers

Codex and similar tools already read root `AGENTS.md`. For monorepos, optionally
add nested `AGENTS.md` files in packages that need tighter local commands—keep
them short and point upward to the root Compass contract for approval/safety.

## Second-opinion review

For high-risk changes, prefer a different model or tool for adversarial review
than the one that implemented the change (implementer ≠ rubber-stamp reviewer).
