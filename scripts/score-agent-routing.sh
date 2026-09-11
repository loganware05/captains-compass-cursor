#!/usr/bin/env bash
# score-agent-routing.sh — Score Cursor agents with wakeability-adjusted availability.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRY=""
OBJECTIVE=""
OUT=""

usage() {
  cat <<'USAGE'
Usage:
  score-agent-routing.sh --registry PATH --objective PATH [--out PATH]

Reads an agent registry JSON and objective JSON, writes a routing decision.
Never hardcodes a dispatcher. Expired/unreachable agents are not dispatch-ready
even when declared availability=1.0 (OVA-17 / M25).
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --registry) REGISTRY="$2"; shift 2 ;;
    --objective) OBJECTIVE="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$REGISTRY" || -z "$OBJECTIVE" ]]; then
  echo "error: --registry and --objective are required" >&2
  usage >&2
  exit 2
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
python3 - "$REGISTRY" "$OBJECTIVE" "$OUT" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.routing.agent_router import (
    RouteObjective,
    decision_to_dict,
    load_registry,
    route_agents,
)

registry_path = Path(sys.argv[1])
objective_path = Path(sys.argv[2])
out_arg = sys.argv[3]

registry = json.loads(registry_path.read_text(encoding="utf-8"))
objective_raw = json.loads(objective_path.read_text(encoding="utf-8"))
objective = RouteObjective(
    title=str(objective_raw.get("title") or objective_raw.get("objective") or "untitled"),
    category=str(objective_raw.get("category") or ""),
    target_repository=str(objective_raw.get("target_repository") or ""),
    required_skills=list(objective_raw.get("required_skills") or []),
    skill_scope=str(objective_raw.get("skill_scope") or "sandbox"),
    context_agent_id=objective_raw.get("context_agent_id"),
)
decision = route_agents(load_registry(registry), objective)
payload = decision_to_dict(decision)
text = json.dumps(payload, indent=2) + "\n"
if out_arg:
    Path(out_arg).write_text(text, encoding="utf-8")
    print(out_arg)
else:
    sys.stdout.write(text)
PY
