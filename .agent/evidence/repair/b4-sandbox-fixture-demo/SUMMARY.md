# Repair run `b4-sandbox-fixture-demo`

- Stage: **fix_authorized_prepare_submit**
- Finding: `sec-hardcoded-key` (verified / high)
- Repository: `loganware05/captain-compass-sandbox`
- Auto-merge: **false**
- Captain FIX authorized: `True`

## Title

Hardcoded API key introduced in session helper

## Suggested fix

Remove hardcoded secret; load from environment; rotate if exposed.
