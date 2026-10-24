# NorthStar docs index

Operator map for the **NorthStar** control repository.
Launcher: `scripts/northstar` (control repo only).

## Start here

| Goal | Doc / command |
|---|---|
| **Captain Handbook (start here)** | [`guides/captain-handbook.md`](guides/captain-handbook.md) |
| Install into a product repo | [`PRODUCT_ONBOARDING.md`](PRODUCT_ONBOARDING.md) · `./scripts/install.sh <repo>` |
| Upgrade an existing install | [`UPGRADING.md`](UPGRADING.md) · `./scripts/update.sh <repo>` |
| Sandbox validation | [`SANDBOX_VALIDATION.md`](SANDBOX_VALIDATION.md) |
| Evidence expectations | [`EVIDENCE_MATRIX.md`](EVIDENCE_MATRIX.md) |
| Star → Skill Learning Run | [`guides/starred-repos-to-skills.md`](guides/starred-repos-to-skills.md) |
| A1 Skills library fill | [`guides/skills-library-fill-a1.md`](guides/skills-library-fill-a1.md) |
| Starred catalog ranking | [`guides/starred-library-ranking.md`](guides/starred-library-ranking.md) · `.agent/intelligence/starred-catalog/` |

## Launcher surfaces (`northstar …`)

| Surface | Purpose | Primary docs |
|---|---|---|
| `skills` | TI refresh, learn, promote, ledger sync, agent routing | [`guides/captain-handbook.md`](guides/captain-handbook.md), [`integrations/technology-intelligence.md`](integrations/technology-intelligence.md) |
| `review` | Code review detect→…→verify→report | [`integrations/code-reviewer.md`](integrations/code-reviewer.md) |
| `intent` | Intent pack export (never Captain approval) | [`integrations/code-reviewer.md`](integrations/code-reviewer.md) |
| `outcomes` | Finding triage → Experience (+ proposal-only routing) | [`integrations/code-reviewer.md`](integrations/code-reviewer.md) |
| `repair` | FIND→PROVE→packet (never auto-merge) | [`integrations/code-reviewer.md`](integrations/code-reviewer.md), [`plans/B4_REPAIR_LOOP.md`](plans/B4_REPAIR_LOOP.md) |
| `precision` | Precision ledger / dashboard from outcomes | [`integrations/code-reviewer.md`](integrations/code-reviewer.md), [`plans/B5_PRECISION_LEDGER.md`](plans/B5_PRECISION_LEDGER.md) |
| `context` | Inode store build + context route walking (M40) | [`integrations/context-inodes.md`](integrations/context-inodes.md) |
| `evaluate` / `learn` / `instructions` / `prompt-eval` / `policy` | Behavior Intelligence Loop (M46–M50) | [`plans/M46_BEHAVIOR_INTELLIGENCE_FOUNDATION.md`](plans/M46_BEHAVIOR_INTELLIGENCE_FOUNDATION.md) |
| `status` | Project Overseer snapshot/explain/compare/reconcile/**closeout** | [`plans/M51_PROJECT_OVERSEER.md`](plans/M51_PROJECT_OVERSEER.md), [`plans/N1_OPERATIONAL_RECONCILIATION.md`](plans/N1_OPERATIONAL_RECONCILIATION.md) |
| `provenance` / `examples` | Execution provenance + exemplars (M53) | [`plans/M53_PROMPT_POLICY_PROVENANCE.md`](plans/M53_PROMPT_POLICY_PROVENANCE.md) |
| `brain` / `assess` / `cycle` / `learning` / `model` / `rea` / `train` | Cognitive Core C1–C7 | [`plans/C1_COGNITIVE_CORE_SOURCE_OF_TRUTH.md`](plans/C1_COGNITIVE_CORE_SOURCE_OF_TRUTH.md) |
| `cognitive` | Hermetic C1–C7 e2e evaluation | [`plans/E2E_COGNITIVE_CORE_EVALUATION.md`](plans/E2E_COGNITIVE_CORE_EVALUATION.md) |
| `oversight` | Read-only persistent oversight compose | [`plans/READ_ONLY_PERSISTENT_OVERSIGHT.md`](plans/READ_ONLY_PERSISTENT_OVERSIGHT.md) |
| `specialized` | Specialized Model Level 0–2 (baseline / LoRA / GPU) | [`plans/SPECIALIZED_MODEL_LEVEL_0.md`](plans/SPECIALIZED_MODEL_LEVEL_0.md) |
| `adaptive` | N3 Adaptive Intelligence scorecard (proposal-only) | [`plans/N3_ADAPTIVE_INTELLIGENCE_VALIDATION.md`](plans/N3_ADAPTIVE_INTELLIGENCE_VALIDATION.md) |
| `ui` | Open UI emitters (plan/tower/scorecard/closeout) + gated approve/reject | [`plans/OPENUI_CONTROL_PLANE.md`](plans/OPENUI_CONTROL_PLANE.md) |

```bash
# From the control repo
./scripts/northstar help
./scripts/northstar review --repo /path/to/product
./scripts/northstar status closeout --repo .
./scripts/northstar ui emit --surface plan --repo . --enable-gates
./scripts/northstar skills learn --repo /path/to/sandbox --objective "…"
```

## Control vs product

| Lives in | What |
|---|---|
| **Control** (`captains-compass-cursor`) | `scripts/northstar`, orchestrator, doctor, Learning Loop + repair/precision CLIs |
| **Product** (after `install.sh`) | `.cursor/` Skills/rules/agents, memory docs, `.agent/` layout, product-scoped `docs/INDEX.md` from `templates/docs/INDEX.md` — **not** control `scripts/` |

Full product-repo install polish for a specific app (e.g. `bitcoin-data-collector`) is track **`roadmap/C2`** (issue #164 / N2 follow-on) — separate Captain plan. Do not confuse with Cognitive Core **`cognitive/C2`** (memory retrieval).

## Roadmap tracks (namespaces)

Use a track prefix in prose and plan IDs when referring to milestones:

| Track | Example | Meaning |
|---|---|---|
| `roadmap/*` | `roadmap/C2` product-repo install | Historical Captain continuation / product install ladder |
| `cognitive/*` | `cognitive/C2` memory retrieval | Cognitive Core C1–C7 |
| `specialized/*` | `specialized/L3` | Specialized Model Levels 0–3 |
| `consolidation/*` | `consolidation/N1` | N1–N3 closeout / validation track |

- Continuation roadmap: [`plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md`](plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md)
- Consolidation: [`plans/N1_OPERATIONAL_RECONCILIATION.md`](plans/N1_OPERATIONAL_RECONCILIATION.md) → [`plans/N2_PRODUCT_INTEGRATION_VALIDATION.md`](plans/N2_PRODUCT_INTEGRATION_VALIDATION.md) → [`plans/N3_ADAPTIVE_INTELLIGENCE_VALIDATION.md`](plans/N3_ADAPTIVE_INTELLIGENCE_VALIDATION.md) (**complete**)
- Specialized Model Level 3 remains **DEFERRED**: [`plans/SPECIALIZED_MODEL_LEVEL_3.md`](plans/SPECIALIZED_MODEL_LEVEL_3.md)

## Integrations (selected)

- [`integrations/code-reviewer.md`](integrations/code-reviewer.md)
- [`integrations/linear-skills-learning-loop.md`](integrations/linear-skills-learning-loop.md)
- [`integrations/linear.md`](integrations/linear.md)
- [`integrations/github.md`](integrations/github.md)
- [`integrations/agent-routing-contract.md`](integrations/agent-routing-contract.md)
- [`integrations/decision-provider.md`](integrations/decision-provider.md)
- [`integrations/northstar-live-ops.md`](integrations/northstar-live-ops.md)
