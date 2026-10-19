# Implementation Plan — C6 Cognitive Core REA Deep Analysis

- Status: **APPROVED**

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `c6-cognitive-core-rea-deep-analysis` |
| Issue | [#214](https://github.com/loganware05/captains-compass-cursor/issues/214) |
| Notion | [Cognitive Core — C6 REA deep analysis](https://app.notion.com/p/3f8e6a901c438110882bceb01d2dd249) |
| Product | **NorthStar** (control repo) |
| Baseline | **v1.64.0** @ `735cb6a` (C5 closeout #215 on main) |
| Branch | `cursor/214-c6-rea-deep-analysis-64df` |
| PR | [#216](https://github.com/loganware05/captains-compass-cursor/pull/216) (draft) |
| Rollback | `rollback/pre-c6-cognitive-core-rea-deep-analysis` @ `735cb6a` |
| Release | **v1.65.0** |
| Captain | Logan Ware |
| Created | 2026-10-19 |
| Approved | 2026-10-19 |

## Approval record

| Field | Value |
|---|---|
| Approved by | Captain (Logan Ware) |
| Approval date | 2026-10-19 |
| Notes | Explicit “I approve c6-cognitive-core-rea-deep-analysis”; #215 merged. Standing order: implement → validate → commit → open PR. |

## Request

Ship Cognitive Core **C6 — REA deep analysis**: gated `northstar rea investigate` with permission checklist, hermetic fixture default, and versioned evidence packets distinguishing observed vs hypothesis claims.

## Desired Outcome

```bash
COMPASS_REA_ENABLED=1 \
./scripts/northstar rea investigate \
  --target PATH_OR_URL --question TEXT [--mode MODE] --repo .
```

## Acceptance Criteria

- [x] Gated `northstar rea investigate` (fail-closed when `COMPASS_REA_ENABLED` unset)
- [x] Schema `rea-evidence-packet` with authority flags const false; claim kinds distinguish observed vs hypothesis
- [x] Explicit permission/licensing checklist required before live run; incomplete → refuse
- [x] Hermetic fixture mode default for CI (no live REA/binary execution required)
- [x] Live mode requires `--allow-live` and still cannot mutate authority; auto-execution withheld (detect-only stub)
- [x] Evidence cites artifact hash + tool version + command refs; uncertainties required
- [x] Doctor + unit tests green; evidence under `.agent/evidence/c6-cognitive-core-rea-deep-analysis/`
- [x] Memory docs + CHANGELOG + VERSION **v1.65.0**; ADR-083
- [x] PR opened (standing order) — [#216](https://github.com/loganware05/captains-compass-cursor/pull/216)

## Non-Goals

C7; automatic REA; speculative training-data recovery; HTTP REA API; expanding approval gates.

## Autonomy Budget

| Limit | Value |
|---|---|
| Maximum iterations | 10 |
| Maximum failed validation cycles | 3 |
| Maximum elapsed minutes | 300 |
| Maximum estimated cost (USD) | 0 |

## Rollback

`rollback/pre-c6-cognitive-core-rea-deep-analysis` @ `735cb6a`
