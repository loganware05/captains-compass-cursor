# Implementation Plan

## Metadata

- Status: APPROVED
- Plan ID: compass-v0.1
- Issue: N/A (control repo bootstrap)
- Branch: main
- Created: 2026-07-10
- Last updated: 2026-07-10
- Approved by: Captain
- Approval date: 2026-07-10
- Approved revision: plan Compass V0.1 Bootstrap

## Request

Implement Version 0.1 of the Captain's Compass reusable Cursor workflow template repository.

## Problem Statement

There is no installable, approval-gated agentic engineering workflow package yet—only design documents.

## Desired Outcome

A working control repository with rules, Skills, agents, templates, install/doctor scripts, tests, and README that can be installed into a disposable product sandbox.

## Acceptance Criteria

- VERSION is 0.1.0
- Five always-applied rules, seven Skills, eight agents
- Seven installable doc templates
- install.sh and doctor.sh work; automated tests pass
- README documents usage and V0.1 boundaries
- No product application code in this repo

## Non-Goals

Hooks, MCP integrations, tech-specific Skills, update.sh auto-overwrite, production product installs.

## Assumptions

- Cursor loads `.cursor/rules/`, Skills, and agents as documented
- Bash is available on macOS/Linux for scripts

## Open Questions

None for V0.1.

## Current-State Analysis

Repository contained only three design markdown files; no git history, no workflow package.

## Proposed Architecture

Control repo owns reusable workflow; product repos receive a copy via install.sh.

## Workstreams

1. Bootstrap and root docs
2. AGENTS.md + rules + Skills + agents
3. Templates + scripts + tests + README
4. Sandbox install validation

## Parallelization Plan

Sequential within the control repo; no parallel product workstreams.

## Files Expected to Change

All V0.1 scaffold files under `.cursor/`, `templates/`, `scripts/`, `tests/`, `examples/`, and root docs.

## Testing Strategy

Automated installer/doctor tests; manual sandbox approval-gate exercise.

## Security Review

Installer must not overwrite without `--force`; secrets stay in ignore files.

## Accessibility Review

N/A for control repo UI (none). Skill/agent included for product installs.

## Migration Plan

N/A (greenfield).

## Deployment Plan

Local only; optional private GitHub remote later.

## Rollback Plan

Revert commits or delete uncommitted scaffold.

## Risks and Mitigations

- Cursor config paths may differ by version — keep Skills/agents conventional and document assumptions
- Accidental install into important repos — README warns; sandbox first

## Autonomy Budget

- Maximum iterations: 20
- Maximum failed validation cycles: 3
- Maximum estimated cost: N/A
- Maximum elapsed time: session

## Definition of Done

All acceptance criteria met; doctor and tests pass; sandbox install verified.

## Approval Record

- Approved by Captain via plan confirmation in Cursor (Compass V0.1 Bootstrap)
- Date: 2026-07-10
