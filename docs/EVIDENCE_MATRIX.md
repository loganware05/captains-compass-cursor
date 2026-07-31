# Evidence matrix

Use this matrix when planning validation and when collecting artifacts under
`.agent/evidence/<slug>/`. Required items are the minimum for a merge-ready
change of that type. Add more when risk is higher.

| Change type | Required evidence (examples) | Typical Skills |
|---|---|---|
| Docs / workflow-only | Doctor and/or `./tests/run.sh` (or product test) transcript | `testing-validation` |
| Library / API | Unit and/or integration test results | `testing-validation`, stack Skills |
| UI | Automated tests + accessibility notes + screenshot path(s) | `testing-validation`, `accessibility-review`, Playwright Skill when used |
| Schema / migration | Migration/rollback notes + relevant test results | `postgres-prisma` (or stack Skill), `testing-validation` |
| Security-sensitive | Security review notes (authz, secrets, injection) | `security-review` |
| Harness / Compass workflow | Doctor + control `./tests/run.sh`; note VERSION bump | `testing-validation` |

## How to use

1. Classify the change in the implementation plan Testing / Definition of Done.
2. Create `.agent/evidence/<plan-id-or-slug>/`.
3. Store command transcripts, screenshots, and review notes as files (not only chat).
4. Before `/prepare-pr` or `gh pr create`, ensure the directory has at least one file.
   The soft `pr-evidence-validation` hook checks plan status + evidence presence
   (fail-open if the hook cannot run).

## Private evidence

Sensitive output may live under `.agent/evidence/private/` (gitignored).
Summarize non-sensitive conclusions in a committed validation note.
