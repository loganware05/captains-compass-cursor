# Evidence — M37 agentic security review integration (Phase A)

Encodes Cursor Agentic Security Review medium classes from bitcoin-data-collector
PR #7 into hermetic `emit_security_candidates`:

- `sec-hook-plan-self-serve`
- `sec-hook-checkout-shortcircuit`
- `sec-hook-push-refspec-gap`
- `sec-hook-git-c-gap`

## Land path

- **v1.38.1** tagged @ `d9a059c` after control #167 + product #8
- PR [#168](https://github.com/loganware05/captains-compass-cursor/pull/168) merged into stale M36 branch (not `main`) — do not treat as land
- Land via `cursor/m37-land-main-5182` → `main` (supersedes wrong-base #168 / closeout `#171`)

## Adversarial / security remediations (pre-land)

- Mitigation checks ignore `deny`/`print`/message payloads (echo-string fakes cannot suppress findings)
- Renamed plan hooks under `.cursor/hooks/` still emit Class 1 via behavioral signals
- Protected Class 2 requires protected-base guards (avoids FP on `branch-name-validation.sh`)
- Checkout detector covers `switch -c` and `cursor/` prefixes
- Regression tests: echo-fake, rename, switch/cursor

Validation: `python3 -m unittest tests.orchestrator.test_m37_agentic_security_review` (6 OK)
Doctor: green
Fixtures under `tests/fixtures/code-review/hook-*.diff`.
