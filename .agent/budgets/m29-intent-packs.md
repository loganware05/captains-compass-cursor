# Budget — m29-intent-packs

| Field | Value |
|---|---|
| Plan | m29-intent-packs |
| Status | implementing |
| Started | 2026-09-13 |
| Approved | 2026-09-13 (Captain: “I approve”) |
| Soft stop | AC met + tests green + evidence + PR |
| Hard stop | No GitHub review posts; no Linear-as-approval; no model in CI |

## Locks

1. Intent packs are repo evidence; Linear is flight recorder only
2. Installer skip-if-exists for existing plans unless `--force`
3. Skill slug `code-reviewer` unchanged
4. Evidence-only reviews (M30 posting deferred)

## Iteration log

| When | Note |
|---|---|
| 2026-09-13 | M28 shipped (v1.31.0); M29 plan drafted; paused for Captain approval |
| 2026-09-13 | Captain approved; implementing schema/loader/CLI/installer/tests |
