# Evidence — M38 shell forge gate

Deny `beforeShellExecution` writes that forge `IMPLEMENTATION_PLAN.md` unless
`COMPASS_CAPTAIN_APPROVE=1`.

Registered `plan-approval-check.sh` on `beforeShellExecution` (fail-closed) in
addition to existing `preToolUse` Write/StrReplace gate (M36).

## v1.40.1 residual close (#174 after #173)

Opaque redirects (`cat elsewhere.md > IMPLEMENTATION_PLAN.md`) without promote
tokens in the argv are now **denied** fail-closed. Bare reads remain allowed.

Validation: `python3 -m unittest tests.orchestrator.test_m38_shell_forge_gate`
