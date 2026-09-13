# Implementation Plan — M29 Intent packs + installer templates

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m29-intent-packs` |
| Supersedes | `m28-reviewer-specialist-composition` (CLOSED — shipped as v1.31.0 / M28) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.31.0` / `origin/main` (M28 merged, PR #143) |
| Prepared | 2026-09-13 |
| Approved | 2026-09-13 — Captain: “I approve” |
| Approved | 2026-09-13 — Captain: “I approve” |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track B / **B2** |
| Product dry-run target | `loganware05/bitcoin-data-collector` + `captain-compass-sandbox` |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.32.0** |
| Rollback tag | `rollback/pre-m29-intent-packs` |
| Branch | `cursor/m29-intent-packs-3b10` |
| Issue | [#146](https://github.com/loganware05/captains-compass-cursor/issues/146) |
| Captain | Logan Ware |

## Captain locks (binding — carry forward + M29)

1. **Hermetic CI** — no model calls on the default review path
2. **Skill slug** — orchestrator Skill remains `code-reviewer`
3. **No GitHub review posting** — still Phase B / M30; evidence-only reports
4. **Tracker** — GitHub issues only (Linear = flight recorder, never approval authority)
5. **Installer must not overwrite** product memory docs without `--force`
6. **Linear ingest is optional and read-only** — issue body → intent artifact only; never treat Linear status as Captain approval
7. **No Star clone/exec** during this plan

## Request (Captain-level)

Proceed with **M29 — Intent packs + installer templates (roadmap B2)**: make product repos carry **reviewable intent** so Code Reviewer can run without a hand-written temporary plan. Ship installer/template support for a stable intent pack shape, wire optional Linear issue-body → intent export, and prove on sandbox (bitcoin-style demo as stretch).

## Problem statement

1. M27/M28 `detect.load_intent` already parses `IMPLEMENTATION_PLAN.md` for acceptance criteria + non-goals, but product installs get a generic DRAFT plan template — not a **review-oriented intent pack**.
2. Roadmap B2 exit criterion: *“Review without hand-written temp plan”* via template `IMPLEMENTATION_PLAN.md` / AC export in installer + optional Linear issue body ingest.
3. Operators still drop ad-hoc plan files for dry-runs (bitcoin M27/M28 demos). That does not scale across product repos.
4. Linear already holds Learning Run / issue prose, but there is no safe, hermetic path from Linear issue body → local intent artifact for review.

## Desired outcomes (M29)

```
Installer / templates
   └─ intent-pack sections in IMPLEMENTATION_PLAN.md (AC, non-goals, rollback, domains)
        ↓
Product repo (or sandbox)
   └─ .agent/intent/current.json  (optional normalized export)
        ↓
northstar review --plan … | --intent-json …
        ↓
detect.load_intent (extended) → specialists → verify → evidence report
```

Optional path:

```
Linear issue body (read-only)
   → scripts/export-intent-from-linear.sh / northstar intent export
   → .agent/intent/<issue-id>.json + markdown summary
   → review --intent-json (Captain still owns approval in repo evidence)
```

### Deferred (non-goals for v1.32.0)

- GitHub PR review posting (M30 / B3)
- Treating Linear as approval authority
- Auto-writing APPROVED into product `IMPLEMENTATION_PLAN.md`
- FIND→FIX repair loop (B4)
- Precision/TP-FP ledger (B5)
- Mutating bitcoin-data-collector application code (docs/intent only if Captain asks)

## Acceptance criteria

1. **Intent pack template** — `templates/docs/IMPLEMENTATION_PLAN.md` (and/or `templates/docs/INTENT_PACK.md`) includes required review sections:
   - Acceptance Criteria
   - Non-Goals / Out of Scope
   - Rollback
   - Security / domains notes (optional bullets)
   - Status gate language preserved (DRAFT → AWAITING_APPROVAL → APPROVED)
2. **Installer** — `scripts/install.sh` installs the intent-capable plan template into product repos without clobbering existing APPROVED plans unless `--force`.
3. **Normalized intent schema** — `orchestrator/schemas/intent-pack.schema.json` (+ validate helper) with fields at least: `acceptance_criteria`, `non_goals`, `rollback`, `plan_path`, `source` (`plan`|`linear`|`fixture`).
4. **Detect/CLI** — `load_intent` accepts plan markdown **or** `--intent-json`; `run-code-review.sh` / `northstar review` gain `--intent-json PATH`.
5. **Optional Linear export** — hermetic fixture mode + live `gh`/`linear` read path behind explicit CLI; writes evidence under `.agent/intent/` / `.agent/evidence/intent-export/`; never sets Captain approval.
6. **Doctor** — checks template + schema presence.
7. **Tests** — unit tests for schema, plan→intent parse, intent-json override, installer dry-run/fixture.
8. **Evidence** — sandbox (and optional bitcoin-style) review run using installed intent pack **without** a hand-authored temp plan.
9. **Docs** — `docs/integrations/code-reviewer.md` + installer README note intent packs.
10. **Memory** — DECISIONS ADR-046, PROGRESS, CHANGELOG, VERSION → **1.32.0**.
11. Default posture unchanged: **no auto-merge**, **no GitHub review posts**, **no model in CI**.

## Architecture

```
scripts/install.sh
   └─ templates/docs/IMPLEMENTATION_PLAN.md  (intent sections)

scripts/export-intent-from-linear.sh   (optional)
   └─ .agent/intent/<id>.json

orchestrator/review/intent.py          (NEW: normalize plan|json → IntentPack)
orchestrator/review/detect.py          (call intent loader)
orchestrator/schemas/intent-pack.schema.json

scripts/run-code-review.sh --plan PATH | --intent-json PATH
```

## Implementation steps (after approval only)

1. Create GitHub issue + rollback tag `rollback/pre-m29-intent-packs`.
2. Author intent-pack template sections + JSON schema.
3. Add `orchestrator/review/intent.py`; extend detect + CLI.
4. Optional Linear export script (fixture-first).
5. Installer wiring + doctor checks.
6. Tests + sandbox evidence dry-run.
7. Docs + ADR/PROGRESS/CHANGELOG/VERSION.
8. Open PR to `main`; Captain merge → tag **v1.32.0**.

## Validation plan

| Layer | How |
|---|---|
| Static | `doctor.sh`; schema validate intent packs |
| Unit | intent parse/normalize; CLI `--intent-json`; installer template presence |
| Integration | sandbox install → review with pack only (no temp plan) |
| Security | Linear token never logged; intent export redacts secrets |
| Rollback | reset to rollback tag / revert PR |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Overwriting product plans | Installer skip-if-exists unless `--force` |
| Linear treated as approval | Explicit docs + code comments; export never writes APPROVED |
| Scope creep into M30 posting | Hard non-goal; evidence-only |
| Weak AC parsing | Schema + fixture tests for section headings |

## Budget

After approval: `.agent/budgets/m29-intent-packs.md`

Soft stop: AC + tests + evidence + PR. Hard stop: no GitHub posting; no Linear-as-approval; no model-in-CI.

## Rollback

1. Revert the M29 PR or reset to rollback tag.
2. Confirm `northstar review --plan IMPLEMENTATION_PLAN.md` still works (M28 path).
3. VERSION/CHANGELOG note if tag already cut.

## Approval gate

**Captain approved this plan on 2026-09-13** (“I approve”). Implementation proceeds on
`cursor/m29-intent-packs-3b10` toward **v1.32.0**.

Locks confirmed:

- installer never overwrites APPROVED plans without `--force`
- Linear export is read-only / never approval
- no GitHub review posting
- hermetic default review path

