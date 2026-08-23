#!/usr/bin/env bash
# train-skill-from-experience.sh — Draft a Skill in control repo from an Experience sample.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPERIENCE=""
CONTROL_ROOT="$ROOT"
SKILL_SLUG=""

usage() {
  cat <<'USAGE'
Usage: train-skill-from-experience.sh --experience <file.json> [--control-root PATH] [--skill-slug SLUG]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --experience) EXPERIENCE="$2"; shift 2 ;;
    --control-root) CONTROL_ROOT="$2"; shift 2 ;;
    --skill-slug) SKILL_SLUG="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$EXPERIENCE" ]]; then
  echo "error: --experience is required" >&2
  exit 1
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$CONTROL_ROOT" "$EXPERIENCE" "$SKILL_SLUG" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.training.from_experience import train_skill_from_experience

control = Path(sys.argv[1]).resolve()
experience = Path(sys.argv[2]).resolve()
slug = sys.argv[3].strip() or None
paths = train_skill_from_experience(control, experience, skill_slug=slug)
print(json.dumps({k: str(v) for k, v in paths.items()}, indent=2))
PY
