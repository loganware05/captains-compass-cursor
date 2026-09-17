# Evidence — M37 agentic security review integration (Phase A)

Encodes Cursor Agentic Security Review medium classes from bitcoin-data-collector
PR #7 into hermetic `emit_security_candidates`:

- `sec-hook-plan-self-serve`
- `sec-hook-checkout-shortcircuit`
- `sec-hook-push-refspec-gap`
- `sec-hook-git-c-gap`

Validation: `python3 -m unittest tests.orchestrator.test_m37_agentic_security_review`
Fixtures under `tests/fixtures/code-review/hook-*.diff`.
