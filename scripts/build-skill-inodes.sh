#!/usr/bin/env bash
# build-skill-inodes.sh — Build/refresh the content-addressed Skill inode index (M40)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: build-skill-inodes.sh [--repo-root PATH] [--check] [--captain-approved]

Builds .cursor/skills/inodes/ — content-addressed Skill identity (SHA-256 over
SKILL.md + capability.yaml). Editing a Skill produces a new inode; reputation
carry-over to the new inode defaults to NOT approved.

Options:
  --repo-root PATH     Repository (default: control repo root)
  --check              Do not write; fail (exit 1) when inodes are stale/missing
  --captain-approved [SLUG ...]
                       Approve reputation carry-over for Skills whose content
                       changed since the last indexed inode (Captain gate).
                       Bare flag approves all changed Skills; with SLUGs,
                       approval is scoped to those Skills only.
  -h, --help           Show help
USAGE
}

REPO_ROOT="$ROOT"
CHECK=0
CAPTAIN_APPROVED=0
APPROVED_SLUGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="${2:-}"
      shift 2
      ;;
    --check)
      CHECK=1
      shift
      ;;
    --captain-approved)
      CAPTAIN_APPROVED=1
      shift
      # Optional per-slug scoping: consume following non-flag args as slugs.
      while [[ $# -gt 0 && "$1" != -* ]]; do
        APPROVED_SLUGS+=("$1")
        shift
      done
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

PYTHONPATH="$ROOT" python3 - "$REPO_ROOT" "$CHECK" "$CAPTAIN_APPROVED" "${APPROVED_SLUGS[@]+"${APPROVED_SLUGS[@]}"}" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.registry.inodes import build_skill_inode_index, verify_skill_inodes

repo_root = Path(sys.argv[1]).resolve()
check = sys.argv[2] == "1"
captain_approved = sys.argv[3] == "1"
approved_slugs = [slug for slug in sys.argv[4:] if slug]

if check:
    problems = verify_skill_inodes(repo_root)
    if problems:
        print(json.dumps({"ok": False, "problems": problems}, indent=2))
        sys.exit(1)
    print(json.dumps({"ok": True, "problems": []}, indent=2))
    sys.exit(0)

result = build_skill_inode_index(
    repo_root,
    captain_approved=captain_approved and not approved_slugs,
    captain_approved_slugs=approved_slugs or None,
)
index = result["index"]
changed_pending = [
    slug
    for slug, entry in sorted(index["skills"].items())
    if entry["reputation"].get("carry_over_from") and not entry["reputation"].get("captain_approved")
]
print(json.dumps({
    "ok": True,
    "skills_indexed": index["skill_count"],
    "carry_over_pending_captain": changed_pending,
}, indent=2))
PY
