---
name: harness-gc
description: Detects drift across rules, Skills, commands, and docs; proposes evidence-backed harness cleanup
---

# Harness GC

## Use this Skill when

Rules, Skills, commands, README, or AGENTS.md appear inconsistent; after a major
Compass upgrade; or when the Captain asks for harness garbage collection.

## Procedure

1. Inventory always-on rules (`.cursor/rules/`), Skills (`.cursor/skills/*/SKILL.md`),
   commands (`.cursor/commands/*.md`), and key docs (`AGENTS.md`, README, TESTING).
2. Look for contradictions (e.g. README Skill count vs doctor list, commands that
   reference missing Skills, failClosed docs vs `hooks.json`).
3. Write a report under `.agent/evidence/harness-gc-<date>/REPORT.md` with:
   - Findings (severity, location, evidence)
   - Recommended fixes
   - Predicted impact / regression risk
4. **Docs-only / control-repo workflow fixes** may proceed only with an approved
   plan when they change shipped Compass behavior.
5. **Product application file changes** always require a **separate** approved
   `IMPLEMENTATION_PLAN.md` (same gate as `code-structure-cleanup`).
6. Do not auto-mutate rules/Skills without Captain approval.

## Output

Harness GC report path and a clear ask: approve a plan, waive findings, or defer.

## Prohibited actions

- Silently editing always-on rules to “fix” drift
- Expanding into unrelated product refactors
- Deleting Skills or commands without an approved plan
