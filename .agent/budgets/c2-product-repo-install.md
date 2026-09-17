# Budget — c2-product-repo-install

| Field | Value |
|---|---|
| Plan | c2-product-repo-install |
| Status | draft (awaiting Captain approval) |
| Started | — |
| Soft stop | AC met + evidence + product/control PRs |
| Hard stop | No control-script copy; no memory clobber; Linear never approves |

## Locks

1. Captain plan gate before product implementation
2. No control `scripts/` in product tree
3. Product memory docs skip-if-exists
4. Hermetic default path on control
5. Skill slug `code-reviewer` unchanged

## Iteration log

| When | Note |
|---|---|
| 2026-09-16 | Plan drafted on M34 closeout PR; awaiting approval |
