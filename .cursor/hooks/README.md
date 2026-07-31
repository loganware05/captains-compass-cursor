# Hooks

Configured in `.cursor/hooks.json` (`beforeShellExecution` + `preToolUse`):

1. **secret-protection** — block staging/committing secrets (**fail-closed**)
2. **protected-branch** — block mutations on main/master/develop/release/production (**fail-closed**)
3. **plan-approval-check** — block product source edits without an APPROVED plan (**fail-closed**)
4. **branch-name-validation** — require `feature|fix|chore|docs|agent|hotfix/<name>` (fail-open)
5. **pre-commit-formatting** — run `npm run format` or `lint` before commit when present (`COMPASS_SKIP_FORMAT=1`) (fail-open)
6. **pre-push-tests** — run `npm test` before push when present (`COMPASS_SKIP_TESTS=1`) (fail-open)
7. **pr-evidence-validation** — require plan + `.agent/evidence/` files before `gh pr create` (`COMPASS_SKIP_PR_EVIDENCE=1`) (fail-open)

## Fail-closed vs fail-open

- **Critical** hooks (`secret-protection`, `protected-branch`, `plan-approval-check`) use
  `failClosed: true`. If the hook process crashes or returns unusable output, Cursor
  **denies** the action. Safety must not silently degrade.
- **Soft** hooks (branch name, format, tests, PR evidence) use `failClosed: false` so
  missing local tooling or transient runner issues do not freeze Captain workflows.
  Soft shell hooks still honor `COMPASS_SKIP_*` env vars when present.

Shared helpers live in `_common.sh`. Hooks use `python3` for JSON.

Before `gh pr create`, collect evidence per [`docs/EVIDENCE_MATRIX.md`](../../docs/EVIDENCE_MATRIX.md)
(change-type → required artifacts under `.agent/evidence/`). The PR-evidence hook
only checks that an approved/complete plan exists and that `.agent/evidence/` is
non-empty (soft / fail-open).

## Manual tests

```bash
echo '{"command":"git commit -m x"}' | .cursor/hooks/branch-name-validation.sh
echo '{"command":"gh pr create","cwd":"/path/to/repo"}' | .cursor/hooks/pr-evidence-validation.sh
```
