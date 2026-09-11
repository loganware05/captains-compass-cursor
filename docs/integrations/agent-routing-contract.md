# Agent Routing Contract (v1) — wakeability

Canonical module: `orchestrator/routing/agent_router.py`
Router version: `northstar.agent_router.v1`
CLI: `northstar skills route-agents --registry PATH --objective PATH`

## Authority

- Scores eligible Cursor agents for a Skill objective.
- Does **not** hardcode a single dispatcher.
- Does **not** originate Captain approval.
- Linear may record the decision; repository JSON is canonical.

## Hard filters

Agent is ineligible when any apply:

- `status != active`
- `effective_availability <= 0`
- target repository not in allowlist
- category unsupported
- skill scope mismatch
- autonomy budget blocked

## Wakeability (OVA-17 / M25)

Declared registry `availability` is **not** dispatch-ready alone.

Resolve wakeability in order:

1. `wakeability_status`
2. `cloud_status`
3. optional live probe callback
4. default `unknown`

Effective availability:

| Wakeability | Cap on declared availability |
|---|---|
| `wakeable` | 100% |
| `unknown` | 25% |
| `expired` | 0% (fail closed) |
| `unreachable` | 0% (fail closed) |

`dispatch_ready` is true only when the selected agent is `wakeable` and
`effective_availability > 0`.

When the best historical pin is not wakeable, Captain may authorize a First Mate
proxy with **dual attribution** (selected vs executing agent ids).

## Weights (default)

| Component | Weight |
|---|---|
| skill_match | 0.30 |
| category_match | 0.20 |
| repository_familiarity | 0.15 |
| historical_success | 0.15 |
| context_continuity | 0.10 |
| availability (effective) | 0.10 |

## Related

- Linear: OVA-19 (M25), OVA-17 Experience
- Evidence: `.agent/evidence/m25-agent-router-wakeability/`

## Live Cloud probe (M26)

Supply a Cursor Cloud agent list snapshot (MCP `list-cloud-agents` dump):

```bash
"$CONTROL/scripts/northstar" skills route-agents \
  --registry "$SANDBOX/.agent/agents/registry.json" \
  --objective /tmp/objective.json \
  --cloud-agents-json /tmp/cloud-agents.json
```

When `--cloud-agents-json` is set, live probe is preferred over stale registry
`wakeability_status`. Missing snapshot entries map to `unknown` (0.25 cap).
