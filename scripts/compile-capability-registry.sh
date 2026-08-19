#!/usr/bin/env bash
# compile-capability-registry.sh — Build .agent/capabilities/compiled/registry.json
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PYTHONPATH="$ROOT" python3 -m orchestrator.registry.compiler "$ROOT"
