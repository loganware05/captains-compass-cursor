# Implementation Plan — M30 Opt-in GitHub draft reviews

## Metadata

| Field | Value |
|---|---|
| Status | **APPROVED** |
| Plan ID | `m30-github-draft-reviews` |
| Supersedes | `m29-intent-packs` (CLOSED — shipped as v1.32.0 / M29) |
| Product | **NorthStar** (Captain's Compass compatibility alias) |
| Baseline | `v1.32.0` / `origin/main` (M29 merged, PR #145) |
| Prepared | 2026-09-13 |
| Approved | 2026-09-13 — Captain: “I approve” |
| Design source | `docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md` Track B / **B3** |
| Product dry-run target | `captain-compass-sandbox` first; bitcoin-style product only after sandbox proof |
| Control repo | `loganware05/captains-compass-cursor` |
| Proposed release | **v1.33.0** |
| Rollback tag | `rollback/pre-m30-github-draft-reviews` |
| Branch | `cursor/m30-github-draft-reviews-3b10` |
| Issue | [#147](https://github.com/loganware05/captains-compass-cursor/issues/147) (implementation after approval) |
| Captain | Logan Ware |

## Captain locks (binding — carry forward + M30)

1. **Hermetic CI** — no model calls on the default review path (posting must not require a model)
2. **Skill slug** — orchestrator Skill remains `code-reviewer`
3. **Opt-in only** — GitHub posting is **off by default**; requires explicit CLI flag + allowlist
4. **Draft reviews only** — never submit a final/request-changes review that blocks merge without Captain policy later
5. **Sandbox allowlist first** — only repos on an explicit allowlist; start with `captain-compass-sandbox`
6. **Severity floor** — post only verified findings at/above configured severity (default: `warning`+)
7. **Tracker** — GitHub issues only (Linear = flight recorder, never approval authority)
8. **No auto-merge** — posting never merges or approves the PR
9. **Intent packs remain non-approving** — M29 `captain_approval` stays false forever from export/load

## Request (Captain-level)

Proceed with **M30 — Opt-in GitHub draft-review posting (roadmap B3)**: after hermetic Code Reviewer produces a verified evidence report, optionally post a **draft** PR review to GitHub for allowlisted repos. Prove on sandbox before any product repo.

## Problem statement

1. M27–M29 ship a strong evidence-only loop, but humans still copy findings into PR comments by hand.
2. Roadmap B3 exit: *posted review on sandbox PR with low noise* — draft only, severity floor, Captain allowlist.
3. Premature posting would amplify noise; M28/M29 raised signal quality enough to consider a gated surface.

## Non-goals

- Final / blocking GitHub reviews (REQUEST_CHANGES) in this milestone
- Webhook-driven auto-review on every PR
- Posting outside the allowlist
- Model calls to rewrite comments
- Auto-merge or auto-approve
- Changing Skill slug or Linear approval semantics
- Repair-loop / FIND→FIX automation (M31 / B4)

## Acceptance criteria

1. **Default remains evidence-only** — without `--post-github-draft` (or equivalent), behavior identical to v1.32.0 (`github_review_posted: false`).
2. **Allowlist gate** — posting refused unless repo is listed in config (e.g. `.agent/review/github-allowlist.yml` or env); sandbox listed in fixture/docs.
3. **Draft review only** — uses GitHub “pending/draft review” or comment-only draft path; never APPROVE / REQUEST_CHANGES in M30.
4. **Severity floor** — only verified findings ≥ configured severity are included; discarded/unverified never posted.
5. **Idempotence / evidence** — every post attempt writes evidence under `.agent/evidence/code-review/<run-id>/` including request/response redacted metadata and `github_review_posted: true|false`.
6. **Secrets** — tokens never logged; bodies redacted through existing secret redaction.
7. **CLI** — `run-code-review.sh` / `northstar review` gain opt-in flag; doctor checks module/config template.
8. **Tests** — unit tests with mocked GitHub client; no live network in default CI.
9. **Sandbox proof** — one dry-run against `captain-compass-sandbox` (or fixture PR) documented in evidence.
10. **Docs** — `docs/integrations/code-reviewer.md` + Skill prose; ADR-047; VERSION → **1.33.0**.
11. **Memory** — DECISIONS / PROGRESS / CHANGELOG updated.

## Architecture (proposed)

```
northstar review --post-github-draft
        │
        ▼
run_code_review (hermetic) → report.json
        │
        ▼
github_draft.post_if_allowed(report, allowlist, severity_floor)
        │
        ├─ refuse → evidence note, github_review_posted=false
        └─ draft review via gh API → evidence note, github_review_posted=true
```

## Implementation steps (after approval only)

1. Create GitHub issue + rollback tag `rollback/pre-m30-github-draft-reviews`.
2. Add allowlist config template + schema; refuse-closed without allowlist match.
3. Implement `orchestrator/review/github_draft.py` with injectable HTTP client (mockable).
4. Wire CLI flag; keep default off.
5. Doctor + unit tests (mock GH); sandbox evidence run.
6. Docs + ADR/PROGRESS/CHANGELOG/VERSION.
7. Open PR to `main`; Captain merge → tag **v1.33.0**.

## Validation plan

| Layer | How |
|---|---|
| Static | doctor.sh; schema validate allowlist |
| Unit | mock GitHub; default-off; allowlist refuse; severity floor |
| Integration | sandbox draft post with fixture/token or recorded transport |
| Security | token scrubbing; no secrets in evidence bodies |
| Rollback | revert PR / reset to rollback tag |

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Noisy PR comments | Severity floor + verified-only + draft-only |
| Accidental product posting | Explicit allowlist; sandbox-first |
| Token leakage | Never log Authorization; redact bodies |
| Scope creep to webhooks | Hard non-goal |

## Budget

After approval: `.agent/budgets/m30-github-draft-reviews.md`

Soft stop: AC + tests + sandbox evidence + PR. Hard stop: no final reviews; no webhooks; no model-in-CI; no auto-merge.

## Rollback

1. Revert the M30 PR or reset to rollback tag.
2. Confirm default `northstar review` still evidence-only.
3. VERSION/CHANGELOG note if tag already cut.

## Approval gate

**Captain approved this plan on 2026-09-13** (“I approve”). Implementation proceeds on
`cursor/m30-github-draft-reviews-3b10` toward **v1.33.0**.

Locks confirmed:

- posting off by default
- sandbox allowlist first
- draft only / no REQUEST_CHANGES
- hermetic default review path unchanged
