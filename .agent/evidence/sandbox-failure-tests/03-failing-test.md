# Failure test 3 — Failing test

## Procedure (2026-07-14)

1. Intentionally broke `EMAIL_PATTERN` in `src/lib/contactValidation.ts` so invalid emails were accepted.
2. Observed **3 failing tests** (suite exit 1). Did **not** delete or weaken assertions.
3. Restored correct implementation.
4. Suite returned to **15/15** green. Test-file diffs empty.

## Result

**Pass** — fixed implementation; tests preserved.

See `03-failing-test.txt`.
