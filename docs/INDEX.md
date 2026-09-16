# NorthStar docs index

Operator map for **one product**: Skills Learning Loop + Code Reviewer.
Launcher: `scripts/northstar` (control repo only).

## Start here

| Goal | Doc / command |
|---|---|
| Install into a product repo | [`PRODUCT_ONBOARDING.md`](PRODUCT_ONBOARDING.md) · `./scripts/install.sh <repo>` |
| Upgrade an existing install | [`UPGRADING.md`](UPGRADING.md) · `./scripts/update.sh <repo>` |
| Sandbox validation | [`SANDBOX_VALIDATION.md`](SANDBOX_VALIDATION.md) |
| Evidence expectations | [`EVIDENCE_MATRIX.md`](EVIDENCE_MATRIX.md) |
| Star → Skill Learning Run | [`guides/starred-repos-to-skills.md`](guides/starred-repos-to-skills.md) |

## Launcher surfaces (`northstar …`)

| Surface | Purpose | Primary docs |
|---|---|---|
| `skills` | TI refresh, learn, promote, ledger sync, agent routing | [`integrations/linear-skills-learning-loop.md`](integrations/linear-skills-learning-loop.md), [`integrations/technology-intelligence.md`](integrations/technology-intelligence.md) |
| `review` | Code review detect→…→verify→report | [`integrations/code-reviewer.md`](integrations/code-reviewer.md) |
| `intent` | Intent pack export (never Captain approval) | [`integrations/code-reviewer.md`](integrations/code-reviewer.md) (intent packs) |
| `outcomes` | Finding triage → Experience (+ proposal-only routing) | [`integrations/code-reviewer.md`](integrations/code-reviewer.md) |
| `repair` | FIND→PROVE→packet (never auto-merge) | [`integrations/code-reviewer.md`](integrations/code-reviewer.md), [`plans/B4_REPAIR_LOOP.md`](plans/B4_REPAIR_LOOP.md) |
| `precision` | Precision ledger / dashboard from outcomes | [`integrations/code-reviewer.md`](integrations/code-reviewer.md), [`plans/B5_PRECISION_LEDGER.md`](plans/B5_PRECISION_LEDGER.md) |

```bash
# From the control repo
./scripts/northstar help
./scripts/northstar review --repo /path/to/product
./scripts/northstar skills learn --repo /path/to/sandbox --objective "…"
```

## Control vs product

| Lives in | What |
|---|---|
| **Control** (`captains-compass-cursor`) | `scripts/northstar`, orchestrator, doctor, Learning Loop + repair/precision CLIs |
| **Product** (after `install.sh`) | `.cursor/` Skills/rules/agents, memory docs, `.agent/` layout — **not** control `scripts/` |

Full product-repo install polish for a specific app (e.g. `bitcoin-data-collector`) is roadmap **C2** — separate Captain plan.

## Roadmap

- Continuation roadmap: [`plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md`](plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md)
- Track B (Code Reviewer) complete through B5 / v1.36.0
- Track C starts at C1 (this launcher UX) → C2 product install

## Integrations (selected)

- [`integrations/code-reviewer.md`](integrations/code-reviewer.md)
- [`integrations/linear-skills-learning-loop.md`](integrations/linear-skills-learning-loop.md)
- [`integrations/linear.md`](integrations/linear.md)
- [`integrations/github.md`](integrations/github.md)
- [`integrations/agent-routing-contract.md`](integrations/agent-routing-contract.md)
- [`integrations/northstar-live-ops.md`](integrations/northstar-live-ops.md)
