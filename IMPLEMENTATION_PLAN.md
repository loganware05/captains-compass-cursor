# Implementation Plan — C6 Cognitive Core REA Deep Analysis

- Status: **AWAITING APPROVAL**

## Metadata

| Field | Value |
|---|---|
| Status | **AWAITING APPROVAL** |
| Plan ID | `c6-cognitive-core-rea-deep-analysis` |
| Issue | [#214](https://github.com/loganware05/captains-compass-cursor/issues/214) |
| Notion | [Cognitive Core — C6 REA deep analysis](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.64.0** @ `56ac9de` (C5 merged #213) |
| Branch | *(create after approval)* `cursor/214-c6-rea-deep-analysis-64df` |
| Rollback | *(create after approval)* `rollback/pre-c6-cognitive-core-rea-deep-analysis` |
| Release | **v1.65.0** (proposed) |
| Captain | Logan Ware |
| Created | 2026-10-19 |

## Approval record

| Field | Value |
|---|---|
| Approved by | *(pending)* |
| Approval date | *(pending)* |
| Notes | Post-merge continuation after C5 (#213). Implementation must not begin until Captain explicitly approves this plan. |

## Request

Ship Cognitive Core **C6 — REA deep analysis**: a feature-gated `northstar rea investigate` adapter that runs only for an **authorized** packaged/runtime question when source/docs are insufficient, after an explicit licensing/permission checklist. Produce a versioned evidence packet (tool version, commands, artifact hash, observed behavior, uncertainties) suitable for Captain review. Prefer hermetic fixture mode in CI. Never present speculation as fact; never expand approval authority.

## Problem Statement

Notion Adaptive Intelligence places REA behind Cognitive Core governance: trigger only when binaries/packages/runtime questions cannot be answered from source and docs; capture reproducible evidence; isolate execution when possible. NorthStar has C1–C5 memory/assess/cycle/route surfaces but no governed REA investigate path. Uncontrolled REA use risks license violations, unsafe execution, and speculative claims (e.g. recovering private model training corpora).

## Desired Outcome

```bash
COMPASS_REA_ENABLED=1 \
./scripts/northstar rea investigate \
  --target PATH_OR_URL \
  --question TEXT \
  [--mode native|js-electron|dotnet|browser|android|network-capture] \
  [--allow-live] \
  --repo PATH
```

Returns schema-validated JSON evidence packet with:

- Target + question + mode + permission checklist status
- Tool version, command transcript refs, artifact content hash
- Observations labeled `observed` vs `hypothesis` (hypotheses never authoritative)
- Uncertainties list; `approved_for_execution: false` / `authority_mutation: false`
- Default path is **fixture/hermetic** (`--allow-live` required for any real REA invocation; still never grants NorthStar authority)

### Governed workflow (Notion)

1. Define allowed target and question
2. Review licensing and execution permissions (explicit fields; fail closed if incomplete)
3. Pick REA mode
4. Prefer isolated environment when live
5. Capture versioned evidence packet
6. Cross-validate via repeatable experiment / fixture replay
7. Do not claim recovery of private pretraining corpora / hidden optimizer details from weights

## Acceptance Criteria

- [ ] Gated `northstar rea investigate` (fail-closed when `COMPASS_REA_ENABLED` unset)
- [ ] Schema `rea-evidence-packet` with authority flags const false; claim kinds distinguish observed vs hypothesis
- [ ] Explicit permission/licensing checklist required before live run; incomplete → refuse
- [ ] Hermetic fixture mode default for CI (no live REA/binary execution required)
- [ ] Live mode requires `--allow-live` and still cannot mutate authority or auto-merge
- [ ] Evidence cites artifact hash + tool version + command refs; uncertainties required when incomplete
- [ ] Doctor + unit tests green; evidence under `.agent/evidence/c6-cognitive-core-rea-deep-analysis/`
- [ ] Memory docs + CHANGELOG + VERSION **v1.65.0**; ADR-083
- [ ] PR opened (standing order after approval)

## Non-Goals

- C7 Training bridge / weight export
- Automatic REA on every plan or cycle
- Presenting speculative REA output as repository fact
- Claiming recovery of Kimi K3 (or any model) private training data from weights
- Expanding Captain approval gates or auto-installing REA globally
- HTTP `/v1/rea/investigate` public API (CLI/orchestrator only this milestone)
- External cognitive-core package extract

## Affected systems

| Area | Change |
|---|---|
| `orchestrator/rea/` (new) | Enabled gate, permission checklist, investigate service, fixture runner |
| `orchestrator/schemas/` | `rea-evidence-packet.schema.json` |
| `scripts/` | `run-rea.sh` + `northstar rea` wiring |
| `scripts/doctor.sh` | schema + fail-closed smoke |
| Tests / fixtures | Hermetic REA evidence fixtures (no live binary) |
| Project memory | PLAN / PROGRESS / CHANGELOG / DECISIONS / TESTING / VERSION |

## Workstreams (after approval)

1. Schema + permission checklist + claim-kind rules
2. Hermetic fixture investigate path
3. Optional live adapter stub behind `--allow-live` (documented; may no-op if REA binary absent)
4. CLI / doctor / docs / release bump

## Validation

- Doctor; unit + hermetic fixture tests
- Security: no authority expansion; live path fail-closed without checklist + `--allow-live`
- Rollback tag before implementation

## Autonomy Budget (proposed)

| Limit | Value |
|---|---|
| Maximum iterations | 10 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 300 |
| Maximum estimated cost (USD) | 0 |
| Stop on scope change | true |

## Rollback

Documented SHA / tag created only after approval, before implementation.

## Definition of Done

Acceptance criteria checked; evidence recorded; PR open; First Mate inspected.

## Prior closeout (C5)

C5 Adaptive routing **COMPLETE** — merged [#213](https://github.com/loganware05/captains-compass-cursor/pull/213) → `main` @ `56ac9de` (**v1.64.0**). Plan ID `c5-cognitive-core-adaptive-routing`. Issue #211 closed.
