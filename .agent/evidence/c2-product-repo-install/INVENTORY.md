# Inventory — bitcoin-data-collector NorthStar install

| Check | Result |
|---|---|
| Branch | `cursor/m35-c2-northstar-install-3b10` (local commit `0b7bb96`) |
| Full SHA | `0b7bb964c2a5ca1941835172abc1d0eb80a5dc87` |
| Base | `cursor/kalshi-live-decision-system` |
| Control VERSION at install | `1.38.0` |
| `.agent/COMPASS_VERSION` | `1.38.0` |
| `scripts/` dir | **absent** |
| `scripts/northstar` | **absent** |
| Bare `./scripts/` in Skills/agents/commands/integrations | **0** (rewritten to `$CONTROL/scripts/`) |
| Preserved `.cursor/install.sh` (Cloud Agent venv) | yes |
| Preserved `.cursor/environment.json` | yes |
| Product `docs/INDEX.md` | product-scoped template (`--repo "$(pwd)"`) |
| Skills under `.cursor/skills` | 42 |

## Commit

```
0b7bb96 chore(workflow): install NorthStar (Captain's Compass) without control scripts
 .agent/COMPASS_VERSION                             |   1 +
 .agent/budgets/_templates/BUDGET_LEDGER.md         |  39 ++++
 .agent/budgets/_templates/BUDGET_STOP_REPORT.md    |  28 +++
 .agent/budgets/_templates/SESSION_NOTE.md          |  33 +++
```

## Top-level added (selected)

```
 .agent/COMPASS_VERSION                             |   1 +
 .agent/budgets/_templates/BUDGET_LEDGER.md         |  39 ++++
 .agent/budgets/_templates/BUDGET_STOP_REPORT.md    |  28 +++
 .agent/budgets/_templates/SESSION_NOTE.md          |  33 +++
 .agent/review/github-allowlist.yml                 |   9 +
 .agent/sessions/_templates/SESSION_NOTE.md         |  33 +++
 .cursor/agents/accessibility-reviewer.md           |  21 ++
 .cursor/agents/adversarial-reviewer.md             |  40 ++++
 .cursor/agents/architecture-agent.md               |  23 ++
 .cursor/agents/code-reviewer.md                    |  37 ++++
 .cursor/agents/compass-evaluator.md                |  34 +++
 .cursor/agents/documentation-agent.md              |  21 ++
 .cursor/agents/implementation-agent.md             |  23 ++
 .cursor/agents/knowledge-steward.md                |  33 +++
 .cursor/agents/repository-scout.md                 |  31 +++
 .cursor/agents/security-reviewer.md                |  23 ++
 .cursor/agents/test-engineer.md                    |  22 ++
 .cursor/commands/README.md                         |  17 ++
 .cursor/commands/close-workstream.md               |  22 ++
 .cursor/commands/implement-approved-plan.md        |  12 ++
 .cursor/commands/initialize-project.md             |  11 +
 .cursor/commands/plan-feature.md                   |  13 ++
 .cursor/commands/prepare-pr.md                     |   9 +
 .cursor/commands/validate-change.md                |  10 +
 .cursor/hooks.json                                 |  38 ++++
 .cursor/hooks/README.md                            |  42 ++++
 .cursor/hooks/_common.sh                           |  82 ++++++++
 .cursor/hooks/branch-name-validation.sh            |  31 +++
 .cursor/hooks/plan-approval-check.sh               |  77 +++++++
 .cursor/hooks/pr-evidence-validation.sh            |  38 ++++
 .cursor/hooks/pre-commit-formatting.sh             |  38 ++++
 .cursor/hooks/pre-push-tests.sh                    |  39 ++++
 .cursor/hooks/protected-branch.sh                  |  50 +++++
 .cursor/hooks/secret-protection.sh                 |  25 +++
 .cursor/rules/00-core-operating-model.mdc          |  22 ++
 .cursor/rules/01-plan-approval-gate.mdc            |  28 +++
 .cursor/rules/02-git-worktree-policy.mdc           |  29 +++
 .cursor/rules/03-validation-definition-of-done.mdc |  28 +++
 .cursor/rules/04-documentation-memory.mdc          |  21 ++
 .cursor/skills/accessibility-review/SKILL.md       |  34 +++
 .../skills/accessibility-review/capability.yaml    |  34 +++
 .cursor/skills/autonomy-budget/SKILL.md            |  61 ++++++
 .cursor/skills/autonomy-budget/capability.yaml     |  29 +++
 .cursor/skills/bounded-autonomy/SKILL.md           |  61 ++++++
 .cursor/skills/bounded-autonomy/capability.yaml    |  29 +++
 .cursor/skills/candidate-promotion/SKILL.md        |  71 +++++++
 .cursor/skills/candidate-promotion/capability.yaml |  27 +++
 .cursor/skills/capability-planning/SKILL.md        |  65 ++++++
 .cursor/skills/capability-planning/capability.yaml |  30 +++
 .cursor/skills/code-reviewer/SKILL.md              |  70 +++++++
 .cursor/skills/code-reviewer/capability.yaml       |  31 +++
 .cursor/skills/code-structure-cleanup/SKILL.md     |  48 +++++
 .../skills/code-structure-cleanup/capability.yaml  |  28 +++
 .cursor/skills/compass-evaluator/SKILL.md          |  55 +++++
 .cursor/skills/compass-evaluator/capability.yaml   |  28 +++
 .cursor/skills/dependency-supply-chain/SKILL.md    |  45 ++++
 .../skills/dependency-supply-chain/capability.yaml |  34 +++
 .cursor/skills/docker-cloud/SKILL.md               |  37 ++++
 .cursor/skills/docker-cloud/capability.yaml        |  33 +++
 .cursor/skills/embedding-providers/SKILL.md        |  67 ++++++
 .cursor/skills/embedding-providers/capability.yaml |  30 +++
 .cursor/skills/execution-telemetry/SKILL.md        |  49 +++++
 .cursor/skills/execution-telemetry/capability.yaml |  27 +++
 .cursor/skills/experience-routing/SKILL.md         |  67 ++++++
 .cursor/skills/experience-routing/capability.yaml  |  29 +++
 .cursor/skills/experience-skill-training/SKILL.md  |  53 +++++
 .../experience-skill-training/capability.yaml      |  27 +++
 .cursor/skills/external-knowledge-ingest/SKILL.md  |  75 +++++++
 .../external-knowledge-ingest/capability.yaml      |  31 +++
 .cursor/skills/github-integration/SKILL.md         |  49 +++++
 .cursor/skills/github-integration/capability.yaml  |  30 +++
 .cursor/skills/harness-gc/SKILL.md                 |  37 ++++
 .cursor/skills/harness-gc/capability.yaml          |  30 +++
 .cursor/skills/hosted-vector-db/SKILL.md           |  78 +++++++
 .cursor/skills/hosted-vector-db/capability.yaml    |  33 +++
 .cursor/skills/implementation-planning/SKILL.md    |  48 +++++
 .../skills/implementation-planning/capability.yaml |  30 +++
 .cursor/skills/ios-engineering/SKILL.md            |  33 +++
 .cursor/skills/ios-engineering/capability.yaml     |  31 +++
 .cursor/skills/knowledge-steward/SKILL.md          |  99 +++++++++
```
