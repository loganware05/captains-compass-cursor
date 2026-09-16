# Budget — c2-product-repo-install

| Field | Value |
|---|---|
| Plan | c2-product-repo-install |
| Status | active (soft stop met on control; product PR pending Captain) |
| Started | 2026-09-16 |
| Soft stop | AC met + evidence + PRs |
| Hard stop | No control-script copy; no memory clobber; Linear never approves |

## Locks

1. Captain plan gate — **satisfied**
2. No control `scripts/` in product tree — **verified locally**
3. Product memory docs skip-if-exists — **held**
4. Hermetic default path on control
5. Skill slug `code-reviewer` unchanged

## Iteration log

| When | Note |
|---|---|
| 2026-09-16 | Plan drafted on M34 closeout; awaiting approval |
| 2026-09-16 | Captain approved; local install OK; product push 403; patch in evidence |
| 2026-09-16 | Adversarial: evidence SHA/version drift + bare `./scripts/` in product docs — fixed rewrite + reinstall at 1.38.0 (`0b7bb96`); status PARTIAL until product PR |
