# Implementation Plan

## Metadata

- Status: APPROVED
- Plan ID: compass-micky-inspired-skills
- Issue: #19
- Branch: feature/19-micky-inspired-skills
- Created: 2026-07-28
- Last updated: 2026-07-28
- Approved by: Captain
- Approval date: 2026-07-28
- Approved revision: compass-micky-inspired-skills (VERSION 1.1.0; opensrc preferred-optional; cleanup always separate plan; GitHub issue #19)
- Rollback checkpoint: `rollback/pre-micky-inspired-skills` (`2dd5429`)

## Request

Add three Compass Skills inspired by [micky-podcast-agentic-engineering](https://github.com/pawel-cell/micky-podcast-agentic-engineering):

1. `source-code-context`
2. `code-structure-cleanup`
3. `review-fix-loop`

Also evaluate [vercel-labs/opensrc](https://github.com/vercel-labs/opensrc) as tooling for the source-code-context Skill and decide whether (and how) to incorporate it.

## Problem Statement

Compass already provides a strong control plane (approval gate, memory docs, hooks, validation evidence, specialist agents). It is weaker on three tactical patterns that reduce agent hallucination and improve post-feature quality:

1. Searching real dependency/library source instead of guessing APIs from incomplete docs
2. A deliberate cleanup pass after a feature works (service-layer extraction without behavior change)
3. An iterative review-fix loop that consumes PR/review feedback until merge-ready or a human decision is required

Without these Skills, agents underuse evidence from package source, leave duplicated mechanics in place, and treat review as a one-shot step rather than a loop.

## Desired Outcome

After this change, product repos that install/update Compass gain three new Skills (loaded only when relevant). Agents:

- Prefer real package/repo source when integrating or debugging libraries
- Run a cleanup pass only under a **separate approved** `IMPLEMENTATION_PLAN.md`
- Iterate on review feedback with clear stop conditions

`opensrc` is documented as the **preferred optional tool** for fetching/caching dependency source (not vendored into Compass; not required for install).

Ship as **VERSION 1.1.0**. Doctor, installer tests, README/PROJECT_CONTEXT skill counts, CHANGELOG, and integration docs are updated.

## opensrc decision (approved)

**Preferred-optional.** Skill prefers `opensrc` when installed; falls back to Captain-approved `reference/repos/…`; `docs/integrations/opensrc.md` documents setup. Doctor does **not** require the `opensrc` binary.

## Acceptance Criteria

- [x] Skill `.cursor/skills/source-code-context/SKILL.md` exists with frontmatter `name:` and Compass-style procedure (opensrc preferred, reference-path fallback, cite sources, no silent dependency swaps)
- [x] Skill `.cursor/skills/code-structure-cleanup/SKILL.md` exists: post-feature only; service-layer extraction; no behavior change; **always requires its own approved IMPLEMENTATION_PLAN.md** (never mixed into the feature plan)
- [x] Skill `.cursor/skills/review-fix-loop/SKILL.md` exists: small-PR preflight; read diff + feedback; fix only relevant items; re-validate; stop on human decisions; no auto-merge
- [x] `docs/integrations/opensrc.md` documents optional install and Skill usage
- [x] Cross-links from README, CHANGELOG 1.1.0, PROJECT_CONTEXT skill count (17 → 20)
- [x] `scripts/doctor.sh` SKILLS array includes the three new Skills
- [x] `tests/run.sh` asserts the three Skill files install correctly
- [x] Light touch see-also links on related Skills where useful
- [x] `./scripts/doctor.sh` and `./tests/run.sh` pass on the control repo
- [x] ADR for opensrc-as-optional-tool and cleanup-separate-plan
- [x] VERSION = 1.1.0; PROGRESS.md updated; PR targeting `main` ([#20](https://github.com/loganware05/captains-compass-cursor/pull/20))

## Non-Goals

- Vendoring or forking `vercel-labs/opensrc`
- Requiring `opensrc` for Compass install/doctor success
- Replacing the approval gate, hooks, or evidence DoD
- Always-on “launch earlier” rule
- Young-package (&lt;14 day) security harden (follow-up)
- New hooks
- Sandbox failure-test campaign for these Skills

## Open Questions (resolved)

1. VERSION → **1.1.0 now** (Captain)
2. opensrc → **preferred-optional** (Captain)
3. Cleanup approval → **always a separate plan** (Captain)
4. Issue → **#19** (created after approval)

## Affected Systems

- `.cursor/skills/` (three new Skills; optional see-also edits)
- `scripts/doctor.sh`, `tests/run.sh`
- `docs/integrations/opensrc.md` (new)
- `VERSION`, `README.md`, `PROJECT_CONTEXT.md`, `CHANGELOG.md`, `PROGRESS.md`, `DECISIONS.md`
- Installer copies Skills via existing `cp -R .cursor/skills`

## Independent Workstreams

Single branch `feature/19-micky-inspired-skills`, sequential A→B→C→D.

| Stream | Boundary |
|---|---|
| A — `source-code-context` + `docs/integrations/opensrc.md` | Skill + integration doc |
| B — `code-structure-cleanup` | Skill (separate-plan rule) |
| C — `review-fix-loop` | Skill + see-also on PR skill |
| D — doctor/tests/docs/VERSION/ADR | packaging |

## Test Plan

1. `./scripts/doctor.sh` on control repo
2. `./tests/run.sh`
3. Manual Skill frontmatter/structure review
4. Doc link check

## Migration / Rollback

- Product repos: `./scripts/update.sh /path/to/product-repo`
- Rollback tag: `rollback/pre-micky-inspired-skills`
- `opensrc` cache at `~/.opensrc/` unrelated to Compass uninstall

## Autonomy Budget

- Max iterations: 3
- Max failed validation cycles: 2
- Max elapsed minutes: 90
