# Budget — m30-github-draft-reviews

| Field | Value |
|---|---|
| Plan | m30-github-draft-reviews |
| Status | implementing |
| Started | 2026-09-13 |
| Soft stop | AC met + tests green + sandbox evidence + PR |
| Hard stop | No final/blocking reviews; no webhooks; no model in CI; no auto-merge |

## Locks

1. Opt-in posting only (`--post-github-draft` or equivalent)
2. Allowlist-gated; sandbox first
3. Draft reviews only
4. Skill slug `code-reviewer` unchanged
5. Hermetic default path unchanged

## Iteration log

| When | Note |
|---|---|
| 2026-09-13 | M29 shipped (v1.32.0); M30 plan drafted; paused for Captain approval |

| 2026-09-13 | Captain approved; implementing github_draft + CLI |
| 2026-09-15 | Resolved merge conflicts with main (PR #148 closeout) |
