# Release checklist (control repository)

Use this for Captain's Compass version tags.

1. Choose `RELEASE_VERSION=X.Y.Z` and fail closed unless it produces a stable
   release tag:
   ```bash
   RELEASE_VERSION="X.Y.Z"
   RELEASE_TAG="v${RELEASE_VERSION}"
   if ! [[ "$RELEASE_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] ||
      [[ "$RELEASE_TAG" == rollback/* ]]; then
     printf 'Invalid release tag: %s\n' "$RELEASE_TAG" >&2
     exit 1
   fi
   ```
   Never publish a GitHub release from a `rollback/*` tag.
2. Ensure the release PR **base is `main`** (not a stack feature branch).
3. Merge the release PR to `main`.
4. Fetch and verify the current remote `main` instead of trusting a potentially
   stale local tracking ref:
   ```bash
   git fetch origin main --tags || exit 1
   REMOTE_MAIN="$(
     git ls-remote origin refs/heads/main |
       awk 'NR == 1 { print $1 }'
   )"
   RELEASE_COMMIT="$(git rev-parse origin/main)"
   if [[ -z "$REMOTE_MAIN" || "$RELEASE_COMMIT" != "$REMOTE_MAIN" ]]; then
     printf 'origin/main mismatch: local=%s remote=%s\n' \
       "$RELEASE_COMMIT" "$REMOTE_MAIN" >&2
     exit 1
   fi
   ```
5. Validate the exact release commit in a temporary detached worktree:
   ```bash
   (
     set -euo pipefail
     RELEASE_WORKTREE="$(
       mktemp -d "${TMPDIR:-/tmp}/captains-compass-release-XXXXXX"
     )"
     cleanup_release_worktree() {
       git worktree remove "$RELEASE_WORKTREE" 2>/dev/null || true
       rmdir "$RELEASE_WORKTREE" 2>/dev/null || true
     }
     trap cleanup_release_worktree EXIT

     git worktree add --detach "$RELEASE_WORKTREE" "$RELEASE_COMMIT"
     "$RELEASE_WORKTREE/scripts/doctor.sh" "$RELEASE_WORKTREE"
     "$RELEASE_WORKTREE/tests/run.sh"
   )
   ```
6. Confirm `VERSION`, the `CHANGELOG.md` release heading, and
   `RELEASE_VERSION` match:
   ```bash
   COMMIT_VERSION="$(
     git show "$RELEASE_COMMIT:VERSION" |
       tr -d '[:space:]'
   )"
   if [[ "$COMMIT_VERSION" != "$RELEASE_VERSION" ]] ||
      ! git show "$RELEASE_COMMIT:CHANGELOG.md" |
        rg -q "^## ${RELEASE_VERSION} —"; then
     printf 'VERSION/CHANGELOG release mismatch\n' >&2
     exit 1
   fi
   ```
7. Immediately before creating the tag, revalidate its name and intended
   commit; then create, verify, and push the annotated tag. Do not continue
   unless the entire subshell succeeds:
   ```bash
   (
     set -euo pipefail
     if ! [[ "$RELEASE_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] ||
        [[ "$RELEASE_TAG" == rollback/* ]]; then
       printf 'Invalid release tag: %s\n' "$RELEASE_TAG" >&2
       exit 1
     fi
     if git show-ref --verify --quiet "refs/tags/$RELEASE_TAG"; then
       printf 'Release tag already exists: %s\n' "$RELEASE_TAG" >&2
       exit 1
     fi
     test "$RELEASE_COMMIT" = "$REMOTE_MAIN"
     git tag -a "$RELEASE_TAG" "$RELEASE_COMMIT" \
       -m "Captain's Compass $RELEASE_TAG"
     test "$(git rev-parse "$RELEASE_TAG^{commit}")" = "$RELEASE_COMMIT"
     git push origin "$RELEASE_TAG"
   )
   ```
8. Confirm the remote tag resolves to the same peeled commit:
   ```bash
   LOCAL_COMMIT="$(git rev-parse "$RELEASE_TAG^{commit}")"
   REMOTE_COMMIT="$(
     git ls-remote --tags origin \
       "refs/tags/$RELEASE_TAG" "refs/tags/$RELEASE_TAG^{}" |
       awk '$2 ~ /\^\{\}$/ { peeled=$1 } $2 !~ /\^\{\}$/ { direct=$1 }
         END { print peeled ? peeled : direct }'
   )"
   if [[ -z "$REMOTE_COMMIT" || "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]]; then
     printf 'Local/remote release tag mismatch\n' >&2
     exit 1
   fi
   ```
9. Immediately before publishing, repeat the stable-tag and commit checks. Then
   create the GitHub release using notes for this version only. Do not continue
   unless the entire subshell succeeds:
   ```bash
   (
     set -euo pipefail
     if ! [[ "$RELEASE_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] ||
        [[ "$RELEASE_TAG" == rollback/* ]]; then
       printf 'Invalid release tag: %s\n' "$RELEASE_TAG" >&2
       exit 1
     fi
     test "$LOCAL_COMMIT" = "$RELEASE_COMMIT"
     test "$REMOTE_COMMIT" = "$RELEASE_COMMIT"
     gh release create "$RELEASE_TAG" \
       --verify-tag \
       --title "$RELEASE_TAG" \
       --notes-file "/path/to/${RELEASE_TAG}-notes.md" \
       --latest
   )
   ```
10. Verify GitHub attached the release to the intended version tag:
   ```bash
   if [[ "$(gh release view "$RELEASE_TAG" --json tagName --jq .tagName)" != "$RELEASE_TAG" ]]; then
     printf 'GitHub release tagName mismatch\n' >&2
     exit 1
   fi
   gh release view "$RELEASE_TAG" --json name,tagName,targetCommitish,url
   ```
11. Refresh the disposable sandbox:
   ```bash
   ./scripts/update.sh /path/to/captain-compass-sandbox
   ./scripts/doctor.sh /path/to/captain-compass-sandbox
   ```
12. Run required sandbox release smokes (M18 — automated + interactive evidence):
   ```bash
   ./scripts/run-sandbox-release-smokes.sh \
     --sandbox /path/to/captain-compass-sandbox \
     --version "$RELEASE_VERSION"
   ```
   Complete `docs/evals/SANDBOX_BEHAVIORAL_CHECKLIST.md` in the sandbox Cursor
   session. Copy the interactive attestation template from
   `.agent/evidence/_templates/sandbox-release-smoke/sandbox-smokes-interactive.json`
   into `.agent/evidence/release-v${RELEASE_VERSION}/sandbox-smokes-interactive.json`
   with `passed: true` and per-item `checklist_results`.
   Gate closeout:
   ```bash
   ./scripts/validate-sandbox-release-smokes.sh --version "$RELEASE_VERSION"
   ```
13. Update `PROGRESS.md` and save release/validation evidence, including raw
    scrubbed command transcripts.
