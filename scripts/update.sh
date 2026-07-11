#!/usr/bin/env bash
# update.sh — Safely refresh Captain's Compass .cursor package in a product repo.
# Preserves product memory docs (same as install.sh --force).
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: update.sh <target-repo-path>

Refreshes rules, Skills, agents, and hooks from this control repository into a
product Git repo without overwriting existing product memory docs.

Equivalent to: install.sh --force <target>

Example:
  ./scripts/update.sh ~/Projects/my-app
USAGE
}

if [[ $# -ne 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  [[ $# -eq 1 && ( "$1" == "-h" || "$1" == "--help" ) ]] && exit 0
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$(cd "$1" && pwd)"
NEW_VERSION="$(tr -d '[:space:]' < "$SOURCE_ROOT/VERSION")"

OLD_VERSION="unknown"
if [[ -f "$TARGET/.agent/COMPASS_VERSION" ]]; then
  OLD_VERSION="$(tr -d '[:space:]' < "$TARGET/.agent/COMPASS_VERSION")"
fi

echo "Captain's Compass update"
echo "  target:  $TARGET"
echo "  from:    $OLD_VERSION"
echo "  to:      $NEW_VERSION"
echo

"$SCRIPT_DIR/install.sh" --force "$TARGET"

echo
echo "Update complete: $OLD_VERSION -> $NEW_VERSION"
echo "Review CHANGELOG.md in the control repo for what changed."
