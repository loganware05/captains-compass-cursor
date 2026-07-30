# Implementation Plan

## Metadata

- Status: APPROVED
- Plan ID: document-version-pinned-updates
- Issue: #21
- Branch: feature/21-version-update-guide
- Created: 2026-07-30
- Last updated: 2026-07-30
- Approved by: Captain
- Approval date: 2026-07-30
- Approved revision: document-version-pinned-updates (latest + pinned forward upgrades; downgrades unsupported; release repair separate)
- Rollback checkpoint: `rollback/pre-version-update-guide` (`a6b2aae`)

## Request

Update the README with safe instructions for refreshing an existing product
repository to the latest or an explicitly selected Captain's Compass version.

## Current Behavior

- README only shows `./scripts/update.sh /path/to/product-repo`.
- `docs/UPGRADING.md` explains what is preserved, but not how the selected
  control-repo checkout determines the installed version.
- `update.sh` installs the `VERSION` from the control-repo checkout that runs it.
- Updates copy/overwrite workflow assets but do not remove assets absent from an
  older release. Therefore clean downgrades are not currently supported.
- GitHub release `v1.1.0 — micky-inspired-skills` currently targets
  `rollback/pre-micky-inspired-skills`, and no `v1.1.0` Git tag exists. Repair
  is intentionally deferred to a separate approval-gated plan.

## Approved Scope Decisions

1. Document latest and explicitly pinned **forward upgrades**.
2. Explicitly state that downgrades are unsupported.
3. Prepare a separate plan after this PR to repair the v1.1.0 release/tag.

## Desired Outcome

A user can identify the product's installed Compass version, choose a newer
release, run that exact release's scripts without disturbing their normal
control-repo checkout, verify the result, review the diff, and submit the
workflow update through a product-repo branch/PR.

## Acceptance Criteria

- [x] README explains that the source checkout controls the installed version.
- [x] README shows how to read `.agent/COMPASS_VERSION`.
- [x] README documents updating to the latest stable release.
- [x] README documents a pinned forward upgrade using a detached Git worktree
      for `vX.Y.Z`, including tag existence verification and cleanup.
- [x] README tells users to read release notes/CHANGELOG before updating.
- [x] README instructs users to use a dedicated product-repo branch, run doctor,
      review the workflow diff, and open a PR.
- [x] README states that product memory docs are preserved.
- [x] README clearly states downgrades are unsupported by `update.sh`.
- [x] `docs/UPGRADING.md` is aligned with the README and contains the detailed
      procedure (README may remain concise and link to it).
- [x] Commands quote paths and avoid destructive Git operations.
- [x] Documentation does not claim `v1.1.0` is safely pin-able until its tag is
      repaired; examples use placeholders such as `vX.Y.Z`.
- [x] `./scripts/doctor.sh` passes.
- [x] Documentation link/command review passes.
- [x] CHANGELOG and PROGRESS are updated; evidence is recorded.
- [ ] PR targets `main`.

## Non-Goals

- Supporting downgrades or removing stale workflow assets.
- Changing `install.sh`, `update.sh`, or `doctor.sh`.
- Repairing GitHub release/tag metadata in this change.
- Installing/updating Compass in a real product repository.
- Broad project improvements beyond recording specific follow-up candidates.

## Affected Systems

- `README.md`
- `docs/UPGRADING.md`
- `CHANGELOG.md`
- `PROGRESS.md`
- `IMPLEMENTATION_PLAN.md`
- `.agent/evidence/document-version-pinned-updates/`

## Implementation Approach

1. Add a concise README workflow:
   - inspect current product version;
   - choose latest or a newer explicit release;
   - fetch tags in the control repo;
   - create a detached worktree at `vX.Y.Z`;
   - run that checkout's `update.sh` and `doctor.sh`;
   - review/commit changes in a product-repo update branch;
   - remove the temporary worktree.
2. Expand `docs/UPGRADING.md` with rationale, safeguards, and troubleshooting.
3. Preserve the existing statement that product memory docs are not overwritten.
4. Add a prominent unsupported-downgrade warning.

## Test Plan

1. Run `./scripts/doctor.sh`.
2. Review every documented command for valid quoting and path behavior.
3. Verify all README links resolve to repository files.
4. Confirm no product implementation or scripts changed.
5. Record results under `.agent/evidence/document-version-pinned-updates/`.

## Migration / Rollback

- Documentation-only change; no product migration.
- Roll back by reverting the documentation PR.
- A rollback tag and commit SHA will be recorded before implementation.

## Follow-Up (separate approval required)

Create a dedicated plan to repair the v1.1.0 release so it targets an annotated
`v1.1.0` tag on the merged release commit rather than
`rollback/pre-micky-inspired-skills`. Audit tag/release consistency before
performing external GitHub mutations.

## Autonomy Budget

- Max iterations: 2
- Max failed validation cycles: 1
- Max elapsed minutes: 45
