# Implementation Plan

## Metadata

- Status: APPROVED
- Plan ID: compass-post-1.0-onboarding
- Issue: #14
- Branch: feature/14-post-1.0-onboarding
- Created: 2026-07-11
- Last updated: 2026-07-11
- Approved by: Captain
- Approval date: 2026-07-11
- Approved revision: compass-post-1.0-onboarding (no VERSION bump; defer sandbox failure tests)
- Rollback checkpoint: `rollback/pre-post-1.0-onboarding` (`1f9a242`)

## Request

After releasing **v1.0.0**, complete the design Part 14 onboarding documentation and refresh project memory so the stable workflow is clear for new and existing product repos.

## Problem Statement

v1.0.0 is tagged and the sandbox is on 1.0.0, but PROGRESS/SANDBOX memory still describe pre-release state, and the two onboarding paths from the design docs (new project vs existing project) are only partially reflected in README quick commands.

## Desired Outcome

Operators can follow a single onboarding guide for installing Compass into a new or existing product repo, and project memory accurately reflects the stable 1.0.0 baseline.

## Acceptance Criteria

- [x] `docs/PRODUCT_ONBOARDING.md` documents new-project and existing-project install paths (branch → install → PR), plus update/uninstall pointers
- [x] README links to the onboarding guide
- [x] `PROGRESS.md`, `SANDBOX_VALIDATION.md`, and `PROJECT_CONTEXT.md` reflect v1.0.0 stable (sandbox at 1.0.0; template repo + topics already live)
- [x] `CHANGELOG.md` notes the docs-only post-1.0 patch in Unreleased (no VERSION bump)
- [x] `./tests/run.sh` still passes (49/49)
- [x] Evidence note under `.agent/evidence/post-1.0-onboarding/`

## Non-Goals

- Deeper cloud automation
- Expanding `examples/react-node-prisma` into a runnable app
- Sandbox failure-test exercises (deferred)
- Changing hooks, Skills, or installer behavior
- Version bump to 1.0.1

## Assumptions

- GitHub template + topics already configured (verified: `isTemplate: true`)
- Release https://github.com/loganware05/captains-compass-cursor/releases/tag/v1.0.0 exists
- Sandbox at `/Users/loganware/Documents/Personal/Code/captain-compass-sandbox` reports `.agent/COMPASS_VERSION=1.0.0`

## Open Questions

1. Ship as docs-only on `1.0.0` (CHANGELOG Unreleased) or bump to `1.0.1`? → **No bump** (Captain)
2. Include optional sandbox failure-test runs in this PR, or defer? → **Defer**

## Affected Systems

- Documentation (`docs/`, README, memory docs)
- Evidence folder only

## Independent Workstreams

1. **Docs** — PRODUCT_ONBOARDING + README link + memory refresh
2. **Validation** — run `./tests/run.sh`; record evidence

## Test Plan

- `./tests/run.sh`
- Manual: doctor on sandbox still passes (no sandbox update required for docs-only)

## Migration / Rollback

- Rollback: `git reset --hard rollback/pre-post-1.0-onboarding` (or revert the PR)
- No product-repo migration

## Autonomy Budget

- Max iterations: 2
- Stop if scope expands into Skills/hooks/examples code

## Risks

- Low: docs-only change; risk of stale memory if skipped

## First Mate Recommendation

Approve as a small docs PR base **`main`**. Prefer **no VERSION bump** (CHANGELOG Unreleased).
