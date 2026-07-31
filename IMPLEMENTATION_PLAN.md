# Implementation Plan

## Metadata

- Status: COMPLETE
- Plan ID: repair-v1.1.0-release-tag
- Issue: #23
- Branch: feature/23-repair-v1.1.0-release
- Created: 2026-07-30
- Last updated: 2026-07-30
- Approved by: Captain
- Approval date: 2026-07-30
- Approved revision: repair choices 1–3 (retag/recreate, checklist harden, sandbox refresh)
- Rollback checkpoint: `rollback/pre-v1.1.0-release-repair` (`e838f45`)

## Request

Repair the broken Captain's Compass **v1.1.0** GitHub release/tag so pinned
forward upgrades can target a real `v1.1.0` tag, and harden the release
checklist to prevent the same mistake.

## Current Defect (evidence)

Observed 2026-07-30 after PR #22 merge:

| Item | Current state | Expected |
|---|---|---|
| Git tag `v1.1.0` | **Missing** | Annotated tag on the v1.1.0 merge commit |
| GitHub release name | `v1.1.0 — micky-inspired-skills` | Title `v1.1.0` (or equivalent) |
| Release `tag_name` | `rollback/pre-micky-inspired-skills` | `v1.1.0` |
| Release URL | `/releases/tag/rollback/pre-micky-inspired-skills` | `/releases/tag/v1.1.0` |
| Correct content commit | `a6b2aae` (merge of PR #20) | Tag/release must point here |
| Rollback tag commit | `2dd5429` (pre-#20) | Keep as rollback checkpoint; do **not** use as a release |

Impact:

- The new upgrade docs correctly refuse to treat a release title as a pin target.
- Users cannot safely pin/update to v1.1.0 until a real `v1.1.0` tag exists.
- The “Latest” GitHub release currently advertises the wrong tag.

Prior stable tags `v1.0.0` … `v0.2.0` appear correctly named. No other release
currently uses a `rollback/*` tag name.

## Desired Outcome

1. Annotated Git tag `v1.1.0` exists on `a6b2aae`.
2. GitHub release for v1.1.0 is attached to that tag (not any rollback tag).
3. `rollback/pre-micky-inspired-skills` remains as a rollback checkpoint only.
4. `docs/RELEASE_CHECKLIST.md` forbids attaching releases to `rollback/*` tags
   and requires verifying tag name == `vX.Y.Z` before publish.
5. `PROGRESS.md` / CHANGELOG note the repair; evidence is recorded.
6. Light verification that older releases still look healthy (no mass rewrite
   unless a second defect is found).

## Recommended Repair Procedure (after approval)

Exact commands will be executed only after Captain approval and on a non-protected
branch for docs; tag/release mutations use explicit `gh`/`git` commands:

```bash
# 1) Create the missing annotated release tag on the v1.1.0 merge commit
git tag -a v1.1.0 a6b2aae -m "Captain's Compass v1.1.0"
git push origin v1.1.0

# 2) Remove the malformed release that is bound to the rollback tag
#    (does not delete the rollback/* Git tag)
gh release delete "rollback/pre-micky-inspired-skills" --yes

# 3) Create the correct release against v1.1.0
#    Notes: extract the ## 1.1.0 section from CHANGELOG.md (or equivalent notes file)
gh release create v1.1.0 \
  --title "v1.1.0" \
  --notes-file /path/to/v1.1.0-notes.md \
  --latest

# 4) Verify
git ls-remote --tags origin 'refs/tags/v1.1.0'
git rev-parse 'v1.1.0^{commit}'   # expect a6b2aae
gh release view v1.1.0 --json tagName,name,targetCommitish,url
```

Preserve `rollback/pre-micky-inspired-skills` (`2dd5429`).

## Acceptance Criteria

- [x] GitHub issue created for the repair ([#23](https://github.com/loganware05/captains-compass-cursor/issues/23))
- [x] Annotated tag `v1.1.0` points at `a6b2aae`
- [x] Remote `refs/tags/v1.1.0` exists and matches local peeled commit
- [x] GitHub release `v1.1.0` exists with `tag_name == v1.1.0`
- [x] No GitHub release remains attached to `rollback/pre-micky-inspired-skills`
- [x] `rollback/pre-micky-inspired-skills` Git tag still exists
- [x] `docs/RELEASE_CHECKLIST.md` requires:
  - release tag name `vX.Y.Z` only
  - refuse/publish-block for `rollback/*` tags
  - verify `git rev-parse vX.Y.Z^{commit}` matches intended merge commit
  - verify `gh release view vX.Y.Z` `tagName`
- [x] Prior releases spot-checked (`v1.0.0` … `v0.2.0`); no additional defects found
- [x] PROGRESS/CHANGELOG updated; evidence under `.agent/evidence/repair-v1.1.0-release/`
- [x] Doctor still passes
- [x] PR for checklist/docs targets `main` ([#24](https://github.com/loganware05/captains-compass-cursor/pull/24))

## Non-Goals

- Changing VERSION (already `1.1.0` on main)
- Rewriting product-repo installs
- Supporting downgrades
- Force-moving existing version tags other than creating the missing `v1.1.0`
- Deleting rollback checkpoint tags
- Changes to sandbox product behavior beyond the approved Compass 1.1.0 refresh

## Open Questions (resolved)

1. Repair method → **delete malformed release + create `v1.1.0` tag/release on `a6b2aae`**.
2. Checklist harden → **include in this change**.
3. Sandbox → **refresh to 1.1.0 via its own branch/PR**.

## Affected Systems

- Git tags / GitHub Releases (mutating; Captain-approved)
- `docs/RELEASE_CHECKLIST.md`
- `PROGRESS.md`, `CHANGELOG.md`, `IMPLEMENTATION_PLAN.md`
- `.agent/evidence/repair-v1.1.0-release/`

## Test / Verification Plan

1. Local/remote peeled commit equality for `v1.1.0`
2. `gh release view v1.1.0` shows correct `tagName`
3. Confirm no release remains on `rollback/pre-micky-inspired-skills`
4. Dry-run the README upgrade selector: newest stable tag becomes `v1.1.0`
5. `./scripts/doctor.sh`
6. Record command transcripts under evidence

## Migration / Rollback

- If the new release/tag must be undone: delete GitHub release `v1.1.0`, delete
  remote/local tag `v1.1.0`, and recreate the previous release only if needed
  (prefer leaving rollback tag untouched).
- Docs checklist changes roll back by reverting the docs PR.

## Risks

- Deleting a GitHub release is visible/public; communicate that the “Latest”
  release was mis-tagged and is being replaced.
- Creating `v1.1.0` after the fact is still correct because content already
  landed via PR #20; the tag was simply never created.

## Autonomy Budget

- Max iterations: 2
- Max failed validation cycles: 1
- Max elapsed minutes: 45

## Completion Record

- Public `v1.1.0` tag/release repaired and verified
- Control checklist/evidence merged in [PR #24](https://github.com/loganware05/captains-compass-cursor/pull/24)
- Sandbox workflow refresh merged in [sandbox PR #6](https://github.com/loganware05/captain-compass-sandbox/pull/6)
- Post-merge sandbox verification: Compass doctor passed; `npm test` 15/15
- Issues [#23](https://github.com/loganware05/captains-compass-cursor/issues/23)
  and [sandbox #5](https://github.com/loganware05/captain-compass-sandbox/issues/5)
  closed
