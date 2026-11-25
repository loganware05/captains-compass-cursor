# Repair run `b4-sandbox-fixture-demo`

- Stage: **submit_prepared**
- Finding: `sec-hardcoded-key` (verified / high)
- Repository: `loganware05/captain-compass-sandbox`
- Auto-merge: **false**
- Captain FIX authorized: `True`
- Draft PR requested: `False`
- Submit prepared: `True`

## Title

Hardcoded API key introduced in session helper

## Suggested fix

Remove hardcoded secret; load from environment; rotate if exposed.
