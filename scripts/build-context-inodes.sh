#!/usr/bin/env bash
# build-context-inodes.sh — Build the inode metadata store + derived context tree (M40)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: build-context-inodes.sh [--repo-root PATH] [--output DIR] [--context-output DIR] [--check]

Builds .agent/inodes/ (content-addressed structural metadata) and derives the
.agent/context/ route tree. Deterministic: identical sources ⇒ identical bytes.

Options:
  --repo-root PATH     Repository to index (default: control repo root)
  --output DIR         Inode store output (default: <repo>/.agent/inodes)
  --context-output DIR Context tree output (default: <repo>/.agent/context)
  --check              Do not write; fail (exit 1) if indexed sources are stale
  -h, --help           Show help
USAGE
}

REPO_ROOT="$ROOT"
OUTPUT=""
CONTEXT_OUTPUT=""
CHECK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT="${2:-}"
      shift 2
      ;;
    --context-output)
      CONTEXT_OUTPUT="${2:-}"
      shift 2
      ;;
    --check)
      CHECK=1
      shift
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

PYTHONPATH="$ROOT" python3 - "$REPO_ROOT" "$OUTPUT" "$CONTEXT_OUTPUT" "$CHECK" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.context.inodes import build_store, find_stale
from orchestrator.context.walker import derive_context_tree

repo_root = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve() if sys.argv[2] else None
context_output = Path(sys.argv[3]).resolve() if sys.argv[3] else None
check = sys.argv[4] == "1"

if check:
    stale = find_stale(repo_root, store_dir=output)
    if stale:
        print(json.dumps({"ok": False, "stale": stale}, indent=2))
        print("error: inode store is stale — rerun scripts/build-context-inodes.sh", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"ok": True, "stale": []}, indent=2))
    sys.exit(0)

index = build_store(repo_root, output_dir=output)
tree = derive_context_tree(repo_root, store_dir=output, output_dir=context_output)
print(json.dumps({
    "ok": True,
    "files_indexed": index["file_count"],
    "inodes": index["inode_count"],
    "context_nodes": tree["node_count"],
}, indent=2))
PY
