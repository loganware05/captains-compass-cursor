# Hooks

Configured in `.cursor/hooks.json` (`beforeShellExecution` + `preToolUse`):

1. **secret-protection** — block staging/committing secrets (**fail-closed**)
2. **protected-branch** — block mutations on main/master/develop/release/production (**fail-closed**).
   Parses `git -C`, push refspecs (`HEAD:main`, `origin main`), and does **not**
   short-circuit on a `checkout -b feature/` substring in the same command.
3. **plan-approval-check** — block product source edits without a **committed**
   APPROVED plan (**fail-closed**). Writing `APPROVED` into `IMPLEMENTATION_PLAN.md`
   requires `COMPASS_CAPTAIN_APPROVE=1` so agents cannot self-serve the gate.
   Status is read from the metadata table (`| Status | … |`) or `- Status:` lines;
   `Approved by` + `Approval date` must be real (not empty / TBD). Working-tree-only
   approval does not unlock product files.
4. **branch-name-validation** — require `feature|fix|chore|docs|agent|hotfix/<name>` (fail-open)
5. **pre-commit-formatting** — run `npm run format` or `lint` before commit when present (`COMPASS_SKIP_FORMAT=1`) (fail-open)
6. **pre-push-tests** — run `npm test` before push when present (`COMPASS_SKIP_TESTS=1`) (fail-open)
7. **pr-evidence-validation** — require plan + `.agent/evidence/` files before `gh pr create` (`COMPASS_SKIP_PR_EVIDENCE=1`) (fail-open)

## Captain approval env

When promoting a plan to APPROVED / IN PROGRESS / VALIDATING / COMPLETE via
Write/StrReplace, set in the Cursor / shell environment:

```bash
export COMPASS_CAPTAIN_APPROVE=1
```

Agents must not set this for themselves. After the plan is committed with a filled
Approval Record, product-source edits are allowed on non-protected branches.

## Fail-closed vs fail-open

- **Critical** hooks (`secret-protection`, `protected-branch`, `plan-approval-check`) use
  `failClosed: true`. If the hook process crashes or returns unusable output, Cursor
  **denies** the action. Safety must not silently degrade.
- **Soft** hooks (branch name, format, tests, PR evidence) use `failClosed: false` so
  missing local tooling or transient runner issues do not freeze Captain workflows.

### Soft-hook skip mechanisms (any one is enough)

1. **Process env:** `COMPASS_SKIP_FORMAT=1`, `COMPASS_SKIP_TESTS=1`, `COMPASS_SKIP_PR_EVIDENCE=1`
2. **Command-string prefix/assignment** visible to the hook, e.g.
   `COMPASS_SKIP_TESTS=1 git push` (needed when Cursor does not forward shell exports)
3. **Repo skip-env file (env inheritance):** `.agent/compass-skip.env` with lines like
   `COMPASS_SKIP_FORMAT=1` (gitignored; use when Cursor does not forward process env)
4. **Marker file:** create `.agent/COMPASS_SKIP_HOOKS` in the repo (remove when done)

Shared helpers live in `_common.sh`. Hooks use `python3` for JSON.

Before `gh pr create`, collect evidence per [`docs/EVIDENCE_MATRIX.md`](../../docs/EVIDENCE_MATRIX.md)
(change-type → required artifacts under `.agent/evidence/`). The PR-evidence hook
only checks that an approved/complete plan exists and that `.agent/evidence/` is
non-empty (soft / fail-open), unless skipped as above.

## Manual tests

```bash
echo '{"command":"git commit -m x"}' | .cursor/hooks/branch-name-validation.sh
echo '{"command":"gh pr create","cwd":"/path/to/repo"}' | .cursor/hooks/pr-evidence-validation.sh
```
