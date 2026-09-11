#!/usr/bin/env bash
# score-agent-routing.sh — Score Cursor agents with wakeability-adjusted availability.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRY=""
OBJECTIVE=""
OUT=""
CLOUD_AGENTS_JSON=""

usage() {
  cat <<'USAGE'
Usage:
  score-agent-routing.sh --registry PATH --objective PATH [--out PATH] \
    [--cloud-agents-json PATH]

Reads an agent registry JSON and objective JSON, writes a routing decision.
Never hardcodes a dispatcher. Expired/unreachable agents are not dispatch-ready
even when declared availability=1.0 (OVA-17 / M25).

M26 live probe:
  --cloud-agents-json PATH  Cursor Cloud agent list snapshot (MCP list-cloud-agents
                            dump). When set, live probe is preferred over stale
                            registry wakeability_status.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --registry) REGISTRY="$2"; shift 2 ;;
    --objective) OBJECTIVE="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --cloud-agents-json) CLOUD_AGENTS_JSON="$2"; shift 2 ;;
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
python3 - "$REGISTRY" "$OBJECTIVE" "$OUT" "$CLOUD_AGENTS_JSON" <<'PY'
import json
import sys
from pathlib import Path

from orchestrator.routing.agent_router import (
    RouteObjective,
    decision_to_dict,
    load_registry,
    route_agents,
)
from orchestrator.routing.cloud_wakeability_probe import (
    build_cloud_wakeability_probe,
    load_cloud_agents_payload,
)

registry_path = Path(sys.argv[1])
objective_path = Path(sys.argv[2])
out_arg = sys.argv[3]
cloud_arg = sys.argv[4]

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

probe = None
prefer_probe = False
if cloud_arg:
    cloud_payload = json.loads(Path(cloud_arg).read_text(encoding="utf-8"))
    cloud_agents = load_cloud_agents_payload(cloud_payload)
    probe = build_cloud_wakeability_probe(cloud_agents)
    prefer_probe = True

decision = route_agents(
    load_registry(registry),
    objective,
    probe=probe,
    prefer_probe=prefer_probe,
)
payload = decision_to_dict(decision)
if prefer_probe:
    payload["live_probe"] = {
        "enabled": True,
        "cloud_agents_json": cloud_arg,
        "prefer_probe": True,
    }
text = json.dumps(payload, indent=2) + "\n"
if out_arg:
    Path(out_arg).write_text(text, encoding="utf-8")
    print(out_arg)
else:
    sys.stdout.write(text)
PY
