# Hooks

Configured in `.cursor/hooks.json` (`beforeShellExecution` + `preToolUse`):

1. **secret-protection** — block staging/committing secrets
2. **protected-branch** — block mutations on main/master/develop/release/production
3. **plan-approval-check** — block product source edits without an APPROVED plan
4. **branch-name-validation** — require `feature|fix|chore|docs|agent|hotfix/<name>`
5. **pre-commit-formatting** — run `npm run format` or `lint` before commit when present (`COMPASS_SKIP_FORMAT=1`)
6. **pre-push-tests** — run `npm test` before push when present (`COMPASS_SKIP_TESTS=1`)
7. **pr-evidence-validation** — require plan + `.agent/evidence/` files before `gh pr create` (`COMPASS_SKIP_PR_EVIDENCE=1`)

Shared helpers live in `_common.sh`. Hooks use `python3` for JSON. Default `failClosed: false`.

## Manual tests

```bash
echo '{"command":"git commit -m x"}' | .cursor/hooks/branch-name-validation.sh
echo '{"command":"gh pr create","cwd":"/path/to/repo"}' | .cursor/hooks/pr-evidence-validation.sh
```
