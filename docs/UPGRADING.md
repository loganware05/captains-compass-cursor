# Upgrading Captain's Compass

## Update an existing product install

From the control repository:

```bash
./scripts/update.sh /path/to/product-repo
```

This refreshes `.cursor/` (rules, Skills, agents, hooks) and updates
`.agent/COMPASS_VERSION`. It **does not** overwrite filled-in product docs such
as `PROJECT_CONTEXT.md` or `IMPLEMENTATION_PLAN.md`.

Equivalent:

```bash
./scripts/install.sh --force /path/to/product-repo
```

## After updating

1. Run `./scripts/doctor.sh /path/to/product-repo`.
2. Skim the control repo `CHANGELOG.md` for the new version.
3. Open the product repo in Cursor so hooks/Skills reload.

## Uninstall

```bash
./scripts/uninstall.sh --yes /path/to/product-repo
```

Add `--purge-docs` only if you also want root memory docs removed.
