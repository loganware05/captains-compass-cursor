# Testing

## What we test

1. **Doctor script** — expected files, rule frontmatter, Skill structure, hooks, VERSION
2. **Installer** — copies workflow into a temporary Git repo; refuses overwrite without `--force`
3. **Hooks** — secret protection, protected-branch, plan-approval allow/deny cases
4. **Sandbox exercise (manual)** — approval gate, then implement after approval

## Automated tests

```bash
./tests/run.sh
```

## Manual sandbox checklist

See [docs/SANDBOX_VALIDATION.md](docs/SANDBOX_VALIDATION.md).

Install verification for the disposable sandbox was completed during the V0.1 build.
Cursor approval-gate and failure exercises must be run interactively in that sandbox.

## Deliberate failure tests

See design doc Part 9 and `docs/SANDBOX_VALIDATION.md`: bypass approval, scope expansion, failing test, hard-coded secret.
