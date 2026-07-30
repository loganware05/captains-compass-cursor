# Upgrading Captain's Compass

## How version selection works

`update.sh` installs the workflow from the control-repo checkout that contains
the script. Its `VERSION` becomes the product repo's
`.agent/COMPASS_VERSION`.

Use a tagged release checkout rather than an arbitrary branch commit. The
procedure below creates a temporary detached Git worktree, so it does not switch
or dirty your normal control-repo checkout.

> **Forward upgrades only.** `update.sh` refreshes current workflow files but
> does not remove files that are absent from an older release. A downgrade can
> therefore leave a mixed installation and is not supported.

## 1. Set paths and inspect the current version

```bash
CONTROL="/absolute/path/to/captains-compass-cursor"
PRODUCT="/absolute/path/to/product-repo"

CURRENT_VERSION="v$(tr -d '[:space:]' < "$PRODUCT/.agent/COMPASS_VERSION")"
printf 'Current Compass version: %s\n' "$CURRENT_VERSION"
git -C "$PRODUCT" status --short
```

Stop if the product repo has unrelated changes. Review the Compass
[releases](https://github.com/loganware05/captains-compass-cursor/releases) and
`CHANGELOG.md` before choosing a **newer** target.

## 2. Choose a target release

Fetch tags and select the newest valid version tag:

```bash
git -C "$CONTROL" fetch origin --tags || exit 1
TARGET_VERSION="$(git -C "$CONTROL" tag --list 'v*' --sort=-version:refname | awk '/^v[0-9]+\.[0-9]+\.[0-9]+$/ { print; exit }')"
printf 'Target Compass version: %s\n' "$TARGET_VERSION"
```

For a pinned forward upgrade, set the tag explicitly instead:

```bash
TARGET_VERSION="vX.Y.Z"
```

Confirm the tag exists and resolves to a commit:

```bash
STABLE_SEMVER='^v[0-9]+\.[0-9]+\.[0-9]+$'
[[ "$CURRENT_VERSION" =~ $STABLE_SEMVER && "$TARGET_VERSION" =~ $STABLE_SEMVER ]] || {
  printf 'Invalid stable version: current=%s target=%s\n' "$CURRENT_VERSION" "$TARGET_VERSION" >&2
  exit 1
}

LOCAL_COMMIT="$(git -C "$CONTROL" rev-parse --verify "refs/tags/${TARGET_VERSION}^{commit}")"
REMOTE_COMMIT="$(
  git -C "$CONTROL" ls-remote --tags origin \
    "refs/tags/$TARGET_VERSION" "refs/tags/$TARGET_VERSION^{}" |
    awk '$2 ~ /\^\{\}$/ { peeled=$1 } $2 !~ /\^\{\}$/ { direct=$1 }
      END { print peeled ? peeled : direct }'
)"
[[ -n "$REMOTE_COMMIT" && "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]] || {
  printf 'Local/remote tag mismatch for %s\n' "$TARGET_VERSION" >&2
  exit 1
}

semver_gt() {
  local target="${1#v}" current="${2#v}"
  local t_major t_minor t_patch c_major c_minor c_patch
  IFS=. read -r t_major t_minor t_patch <<< "$target"
  IFS=. read -r c_major c_minor c_patch <<< "$current"
  (( 10#$t_major > 10#$c_major ||
    (10#$t_major == 10#$c_major && 10#$t_minor > 10#$c_minor) ||
    (10#$t_major == 10#$c_major && 10#$t_minor == 10#$c_minor &&
      10#$t_patch > 10#$c_patch) ))
}

semver_gt "$TARGET_VERSION" "$CURRENT_VERSION" || {
  printf 'Refusing non-forward update: %s -> %s\n' "$CURRENT_VERSION" "$TARGET_VERSION" >&2
  exit 1
}
```

These checks reject prereleases, local-only/stale or mismatched tags, and targets
that are not newer than the version recorded in the product repo. A GitHub
release title alone is not sufficient; the local and remote `vX.Y.Z` tag must
resolve to the same commit.

## 3. Create the product update branch

Choose the dedicated product-repo branch name. The next step creates it and
aborts before updating if branch creation fails.

```bash
UPDATE_BRANCH="chore/update-captains-compass-${TARGET_VERSION}"
```

Use a dedicated branch and PR so workflow-file changes are reviewable and easy
to revert.

## 4. Run the selected release

```bash
(
  set -euo pipefail
  UPDATE_WORKTREE="$(mktemp -d "${TMPDIR:-/tmp}/captains-compass-update-XXXXXX")"
  cleanup_update_worktree() {
    git -C "$CONTROL" worktree remove "$UPDATE_WORKTREE" 2>/dev/null || true
    rmdir "$UPDATE_WORKTREE" 2>/dev/null || true
  }
  trap cleanup_update_worktree EXIT

  git -C "$CONTROL" worktree add --detach "$UPDATE_WORKTREE" "$TARGET_VERSION"
  git -C "$PRODUCT" switch -c "$UPDATE_BRANCH"
  "$UPDATE_WORKTREE/scripts/update.sh" "$PRODUCT"
  "$UPDATE_WORKTREE/scripts/doctor.sh" "$PRODUCT"
)
```

The update refreshes `.cursor/` (rules, Skills, agents, commands, and hooks) and
updates `.agent/COMPASS_VERSION`. It **does not** overwrite filled-in product
memory docs such as `PROJECT_CONTEXT.md`, `DECISIONS.md`, or
`IMPLEMENTATION_PLAN.md`.

## 5. Review and clean up

```bash
cat "$PRODUCT/.agent/COMPASS_VERSION"
git -C "$PRODUCT" status --short
git -C "$PRODUCT" add .cursor .agent/COMPASS_VERSION .cursorignore .gitignore
git -C "$PRODUCT" diff --cached
```

Confirm:

1. `.agent/COMPASS_VERSION` matches the selected release without the leading `v`.
2. Doctor passes.
3. Product memory docs retain their project-specific content.
4. The staged diff contains only expected Compass workflow changes.

Commit the changes using the product repository's conventions, push the branch,
and open a PR. Reopen the product repo in Cursor after merge so updated rules,
hooks, agents, and Skills reload.

## Troubleshooting

- **Tag verification fails:** fetch tags again and confirm the release has a
  real `vX.Y.Z` tag. Do not update from a release title or rollback tag.
- **Update or doctor fails:** leave the product branch unmerged, record the
  output, and remove the temporary worktree after investigation.
- **Unrelated product changes exist:** commit/stash them separately or use a
  clean ordinary clone before updating. The current installer expects `.git`
  to be a directory and does not support linked product worktrees.
- **A downgrade is required:** stop and create a dedicated rollback plan. Do
  not run an older `update.sh` over a newer install.

## Equivalent refresh command

When the control checkout is already at the intended newer version:

```bash
"$CONTROL/scripts/install.sh" --force "$PRODUCT"
```

This is equivalent to `update.sh`, including preservation of product memory
docs. The tagged-worktree procedure remains preferred because the selected
version is explicit.

## Uninstall

```bash
./scripts/uninstall.sh --yes /path/to/product-repo
```

Add `--purge-docs` only if you also want root memory docs removed.
