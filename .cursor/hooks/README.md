# Hooks (V0.2)

Project hooks enforce the first three Captain's Compass safety gates.

Configured in `.cursor/hooks.json`:

1. **secret-protection** (`beforeShellExecution`) — blocks staging/committing `.env`, keys, and hard-coded secret assignments in shell
2. **protected-branch** (`beforeShellExecution`) — blocks commit/push/merge/rebase on `main` / `master` / `develop` / `release` / `production`
3. **plan-approval-check** (`preToolUse` Write|StrReplace|EditNotebook) — blocks product source edits unless `IMPLEMENTATION_PLAN.md` is APPROVED (or later in-progress states) with an approval record, on a non-protected branch

Deferred hooks:

4. Branch-name validation
5. Pre-commit formatting
6. Pre-push test execution
7. Pull-request evidence validation

Hooks use `python3` (stdlib) for JSON. Fail-open by default (`failClosed: false`) so a broken hook does not freeze legitimate work; tighten later if desired.

## Manual test

```bash
echo '{"command":"git commit -m test"}' | .cursor/hooks/protected-branch.sh
echo '{"path":"src/App.tsx"}' | .cursor/hooks/plan-approval-check.sh
```
