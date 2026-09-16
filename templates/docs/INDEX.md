# NorthStar docs index (product install)

This file is installed into **product** repositories. Control-repo scripts are
**not** copied here — run Learning Loop and Code Reviewer from the control
checkout.

Control repository: https://github.com/loganware05/captains-compass-cursor

## Run from control (required)

```bash
CONTROL=/path/to/captains-compass-cursor
$CONTROL/scripts/northstar help
$CONTROL/scripts/northstar review --repo "$(pwd)"
$CONTROL/scripts/northstar skills learn --repo /path/to/sandbox --objective "…"
```

## Surfaces (`northstar …` in control)

| Surface | Purpose |
|---|---|
| `skills` | Learning Loop — refresh TI, learn, promote, sync-ledger, route-agents |
| `review` | Code Reviewer — detect→investigate→verify→report (evidence-only default) |
| `intent` | Export / normalize intent packs (never Captain approval) |
| `outcomes` | Finding triage → Experience (+ optional proposal-only routing) |
| `repair` | FIND→PROVE→packet from verified findings (never auto-merge) |
| `precision` | Aggregate finding outcomes into precision ledger / dashboard |

## Docs available in this product checkout

| Doc | Notes |
|---|---|
| [`EVIDENCE_MATRIX.md`](EVIDENCE_MATRIX.md) | Evidence expectations |
| [`integrations/code-reviewer.md`](integrations/code-reviewer.md) | Code Reviewer operator guide |
| [`integrations/multi-runtime-agents.md`](integrations/multi-runtime-agents.md) | Multi-runtime agents |
| [`integrations/technology-intelligence.md`](integrations/technology-intelligence.md) | Technology intelligence |

Full control operator map (Learning Loop guides, plans, onboarding):  
https://github.com/loganware05/captains-compass-cursor/blob/main/docs/INDEX.md

## Control vs product

| Lives in | What |
|---|---|
| **Control** | `scripts/northstar`, orchestrator, doctor, Learning Loop + repair/precision CLIs |
| **Product** (this repo) | `.cursor/` Skills/rules/agents, memory docs, `.agent/` layout — **not** control `scripts/` |
